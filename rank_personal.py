"""
Agent K2: Personal Thread Ranker

Scores personal threads by "interestingness":
  length × sentiment_variance × unique_contacts

The most interesting threads have strong emotional range AND sustained length.
Exports top 30 threads as skim files for Claude desktop reading.
"""

import json
import math
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "megabase.db")
CENSUS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personal_census.json")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chunks", "personal_skim")
RANKED_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personal_ranked.json")

SKIM_CHARS = 12000
TOP_N = 30
BATCH_SIZE = 4

PROMPT = """## Reading Task — Personal Thread

This is a personal message thread from Ted's archive (SMS, Facebook, Google Chat).

Please provide:

1. **RELATIONSHIP SUMMARY** (2-3 sentences): Who is this person to Ted? What kind of relationship do the messages suggest?
2. **KEY EVENTS** (3-5 bullets): Major life events, milestones, or turning points visible in the thread.
3. **EMOTIONAL ARC** (2-3 sentences): How does the emotional tone change over time? Are there high/low points?
4. **RECURRING THEMES**: What topics come up repeatedly?
5. **INTEREST RATING** (1-5): Is this thread worth featuring in a 'Personal Archive' collection?
   - 5 = Deeply revealing, shows real emotional depth or major life events
   - 3 = Interesting but routine
   - 1 = Mostly logistical/transactional

---

"""


def score_threads(conn):
    """Score all personal threads by interestingness."""
    rows = conn.execute("""
        SELECT c.id, c.title, c.estimated_pages, c.message_count,
               s.name as source, c.created_at, c.updated_at
        FROM conversations c
        JOIN sources s ON c.source_id = s.id
        WHERE s.name IN ('sms', 'facebook', 'google_chat')
          AND c.message_count > 50
        ORDER BY c.message_count DESC
    """).fetchall()

    # Deduplicate by title within each source
    seen = set()
    unique_rows = []
    for row in rows:
        key = (row[1], row[4])  # title, source
        if key in seen:
            continue
        seen.add(key)
        unique_rows.append(row)

    scored = []
    for row in unique_rows:
        conv_id, title, pages, msg_count, source, created, updated = row

        # Skip "(Unknown)" and generic titles
        if "(Unknown)" in (title or ""):
            continue
        if title in ("Facebook user", "Twitter Timeline"):
            continue

        # Get sentiment variance for this thread
        sent_row = conn.execute("""
            SELECT avg(sentiment_vader), count(sentiment_vader),
                   sum((sentiment_vader - sub.mean) * (sentiment_vader - sub.mean)) / count(sentiment_vader)
            FROM messages m,
                 (SELECT avg(sentiment_vader) as mean FROM messages WHERE conversation_id = ? AND sentiment_vader IS NOT NULL) sub
            WHERE m.conversation_id = ? AND m.sentiment_vader IS NOT NULL
        """, (conv_id, conv_id)).fetchone()

        avg_sent = sent_row[0] or 0
        sent_count = sent_row[1] or 0
        variance = sent_row[2] or 0
        std_dev = math.sqrt(variance) if variance > 0 else 0

        # Count unique "contacts" (from title parsing)
        contacts = len([c.strip() for c in title.replace("SMS: ", "").replace("GChat: ", "").split(",") if c.strip()])

        # Interestingness = log(messages) × sentiment_std_dev × sqrt(contacts)
        # log dampens the massive SMS threads, variance rewards emotional range
        interest_score = math.log10(max(msg_count, 1)) * std_dev * math.sqrt(max(contacts, 1))

        scored.append({
            "id": conv_id,
            "title": title,
            "pages": round(pages or 0, 1),
            "message_count": msg_count,
            "source": source,
            "created_at": created,
            "updated_at": updated,
            "avg_sentiment": round(avg_sent, 4),
            "sentiment_std_dev": round(std_dev, 4),
            "contact_count": contacts,
            "interest_score": round(interest_score, 4),
        })

    scored.sort(key=lambda x: x["interest_score"], reverse=True)
    return scored


def export_skim(conn, entry):
    """Export first SKIM_CHARS of a personal thread as .md."""
    conv_id = entry["id"]
    msgs = conn.execute(
        "SELECT role, content, created_at FROM messages "
        "WHERE conversation_id=? ORDER BY id",
        (conv_id,),
    ).fetchall()

    if not msgs:
        return None

    parts = []
    chars_so_far = 0
    for role, content, ts in msgs:
        if not content:
            continue
        header = f"**[{role.upper()}]**"
        if ts:
            header += f" ({ts[:10]})"
        part = f"{header}\n{content}"

        if chars_so_far + len(part) > SKIM_CHARS:
            remaining = SKIM_CHARS - chars_so_far
            if remaining > 200:
                parts.append(part[:remaining] + "\n\n*[...truncated at skim boundary...]*")
            break
        parts.append(part)
        chars_so_far += len(part)

    skim_text = "\n\n---\n\n".join(parts)

    safe_title = "".join(c for c in entry["title"][:50] if c.isalnum() or c in " -_").strip()
    filename = f"{conv_id}_{safe_title}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {entry['title']}\n\n")
        f.write(f"**ID:** {conv_id} | **Source:** {entry['source']} | ")
        f.write(f"**Messages:** {entry['message_count']:,} | **Pages:** {entry['pages']:.0f}\n")
        f.write(f"**Date range:** {entry['created_at'] or '?'} to {entry['updated_at'] or '?'}\n")
        f.write(f"**Avg sentiment:** {entry['avg_sentiment']:.3f} | ")
        f.write(f"**Sentiment std dev:** {entry['sentiment_std_dev']:.3f} | ")
        f.write(f"**Interest score:** {entry['interest_score']:.2f}\n\n")
        f.write(PROMPT)
        f.write(skim_text)

    return filepath


def main():
    conn = sqlite3.connect(DB_PATH)

    print("Scoring personal threads by interestingness...\n")
    scored = score_threads(conn)
    print(f"Scored {len(scored)} threads (after dedup + filtering)\n")

    # Save full rankings
    with open(RANKED_PATH, "w", encoding="utf-8") as f:
        json.dump(scored, f, indent=2, ensure_ascii=False)
    print(f"Full rankings saved to {RANKED_PATH}\n")

    # Export top N as skims
    top = scored[:TOP_N]
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    batch_dir = os.path.join(OUTPUT_DIR, "batches")
    os.makedirs(batch_dir, exist_ok=True)

    print(f"Exporting top {len(top)} threads:\n")
    print(f"{'Rank':>4} {'Score':>7} {'Msgs':>8} {'StdDev':>7} {'Source':<10} Title")
    print("-" * 80)

    files = []
    for i, entry in enumerate(top, 1):
        fp = export_skim(conn, entry)
        if fp:
            files.append(fp)
        title_safe = entry['title'][:35].encode('ascii', 'replace').decode()
        print(f"  {i:>2}  {entry['interest_score']:>7.2f} {entry['message_count']:>8,} {entry['sentiment_std_dev']:>7.3f} {entry['source']:<10} {title_safe}")

    # Create batches
    for i in range(0, len(files), BATCH_SIZE):
        batch_files = files[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        batch_path = os.path.join(batch_dir, f"personal_batch_{batch_num:02d}.md")

        with open(batch_path, "w", encoding="utf-8") as bf:
            bf.write(f"# Personal Archive — Batch {batch_num}\n\n")
            bf.write(f"**{len(batch_files)} personal threads** — read each and provide the analysis requested.\n\n")
            bf.write("---\n\n")
            for fp in batch_files:
                with open(fp, "r", encoding="utf-8") as sf:
                    bf.write(sf.read())
                bf.write("\n\n" + "=" * 80 + "\n\n")

    conn.close()

    num_batches = (len(files) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"\nDone. {len(files)} skims + {num_batches} batch files.")
    print(f"Individual files: {OUTPUT_DIR}")
    print(f"Batch files:      {batch_dir}")
    print(f"\nTed: Review the top 10 in Claude desktop. Skip any threads too private to share.")


if __name__ == "__main__":
    main()
