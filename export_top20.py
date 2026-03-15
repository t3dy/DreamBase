"""
Export the first ~12,000 chars of each of the top 20 conversations
as individual .md files for deep-skim reading in Claude desktop.

Strategy 2: Read enough to write a proper 3-sentence summary + tags.
"""

import os
import sqlite3
from schema import get_db

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chunks", "top20_skim")
SKIM_CHARS = 12000  # ~4 pages, enough to understand the conversation

TOP_20 = [712, 670, 726, 716, 734, 666, 674, 566, 616, 725,
          598, 669, 673, 662, 721, 570, 687, 636, 559, 631]

PROMPT = """## Reading Task

You are reading a skim (first ~12,000 characters) of a conversation from Ted's personal knowledge archive (4,308 conversations over 2 years of LLM work).

For this conversation, please provide:

1. **SUMMARY** (exactly 3 sentences): What is this conversation about? What was accomplished? What's the significance?
2. **TAGS** (comma-separated from: game_idea, app_project, educational, alchemy, esoteric, pkd, mtg, coding, philosophy, personal, history, literature, science, mathematics, art): Choose all that apply.
3. **KEY TOPICS** (3-5 bullet points): The main subjects discussed.
4. **NOTABLE QUOTES** (1-3): The most striking or insightful lines from either participant.
5. **CONNECTIONS**: What other topics or projects might this relate to?
6. **QUALITY ASSESSMENT**: Is this conversation worth a full deep-read, or is the skim sufficient?

---

"""


def export_skim(conn, conv_id):
    """Export the first SKIM_CHARS of a conversation as a .md file."""
    conv = conn.execute(
        "SELECT c.id, c.title, c.created_at, c.estimated_pages, c.char_count, "
        "c.summary, s.name "
        "FROM conversations c JOIN sources s ON s.id=c.source_id WHERE c.id=?",
        (conv_id,),
    ).fetchone()

    if not conv:
        print(f"  [{conv_id}] NOT FOUND")
        return None

    cid, title, created, pages, total_chars, summary, source = conv

    # Get tags
    tags = conn.execute(
        "SELECT GROUP_CONCAT(t.name) FROM conversation_tags ct "
        "JOIN tags t ON t.id=ct.tag_id WHERE ct.conversation_id=?",
        (conv_id,),
    ).fetchone()[0] or "NONE"

    # Get messages
    msgs = conn.execute(
        "SELECT role, content, created_at FROM messages "
        "WHERE conversation_id=? ORDER BY id",
        (conv_id,),
    ).fetchall()

    if not msgs:
        print(f"  [{conv_id}] No messages")
        return None

    # Build skim text up to SKIM_CHARS
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
            # Add truncated remainder
            remaining = SKIM_CHARS - chars_so_far
            if remaining > 200:
                parts.append(part[:remaining] + "\n\n*[...truncated at skim boundary...]*")
            break
        parts.append(part)
        chars_so_far += len(part)

    skim_text = "\n\n---\n\n".join(parts)

    # Write file
    safe_title = "".join(c for c in title[:50] if c.isalnum() or c in " -_").strip()
    filename = f"{conv_id}_{safe_title}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"**ID:** {cid} | **Source:** {source} | **Date:** {created or 'unknown'} | ")
        f.write(f"**Total Pages:** {pages:.0f} | **Total Chars:** {total_chars:,}\n\n")
        f.write(f"**Current Summary:** {summary or 'NONE'}\n\n")
        f.write(f"**Current Tags:** {tags}\n\n")
        f.write(PROMPT)
        f.write(skim_text)

    print(f"  [{cid:>5}] {pages:>6.0f}pp  {tags:<30} {title[:45]}")
    return filepath


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = get_db()

    print("Exporting top 20 conversation skims for Claude desktop reading...\n")
    print(f"{'ID':>7} {'Pages':>7}  {'Tags':<30} Title")
    print("-" * 90)

    files = []
    for conv_id in TOP_20:
        fp = export_skim(conn, conv_id)
        if fp:
            files.append(fp)

    # Also create a batch file that combines 4 skims per batch
    # (Claude desktop can handle ~4 skims × 12K chars = 48K chars comfortably)
    batch_dir = os.path.join(OUTPUT_DIR, "batches")
    os.makedirs(batch_dir, exist_ok=True)

    batch_size = 4
    for i in range(0, len(files), batch_size):
        batch_files = files[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        batch_path = os.path.join(batch_dir, f"batch_{batch_num:02d}.md")

        with open(batch_path, "w", encoding="utf-8") as bf:
            bf.write(f"# Deep Skim Batch {batch_num}\n\n")
            bf.write(f"**{len(batch_files)} conversations** — read each and provide the analysis requested.\n\n")
            bf.write("---\n\n")
            for fp in batch_files:
                with open(fp, "r", encoding="utf-8") as sf:
                    bf.write(sf.read())
                bf.write("\n\n" + "=" * 80 + "\n\n")

        print(f"\n  Batch {batch_num}: {len(batch_files)} conversations -> {batch_path}")

    conn.close()
    print(f"\nDone. {len(files)} individual skims + {(len(files) + batch_size - 1) // batch_size} batch files.")
    print(f"Individual files in: {OUTPUT_DIR}")
    print(f"Batch files in:      {batch_dir}")
    print(f"\nWorkflow: Open each batch in Claude desktop, paste it, get summaries + tags back.")


if __name__ == "__main__":
    main()
