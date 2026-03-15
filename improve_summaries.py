"""
Eldritch Swarm: Summary Improvement System.
Six agents for improving all Dreambase summaries and website copy.

Usage:
    python improve_summaries.py janitor      # Fix bot-voice summaries (deterministic)
    python improve_summaries.py messenger    # Generate SMS/Facebook/etc summaries
    python improve_summaries.py curator      # Propose improved featured summaries
    python improve_summaries.py copywriter   # Propose improved app.py copy
    python improve_summaries.py batch-export # Export batches for ChatGPT
    python improve_summaries.py batch-import <file>  # Import ChatGPT responses
"""

import os
import re
import sqlite3
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "megabase.db")
IMPROVEMENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "improvements")

# Import featured IDs from app.py to avoid stale duplicates
def _get_featured_ids():
    """Pull all conversation IDs from SHOWCASES + COLLECTIONS in app.py."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from app import SHOWCASES, COLLECTIONS
    ids = set()
    for sc in SHOWCASES.values():
        ids.update(sc.get("conversation_ids", []))
    for col in COLLECTIONS.values():
        ids.update(col.get("conversation_ids", []))
    return list(ids)

ALL_FEATURED = _get_featured_ids()

BAD_PREFIXES = [
    "Would you like", "It seems", "Here is a", "Here is the",
    "Sure", "Certainly", "I'd be happy", "I'll ", "Of course",
    "Let me ", "Based on the", "The file", "The document",
    "I can help", "I've ", "Great question", "That's a great",
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def extract_clean_summary(summary, title, first_user_msg=""):
    """Strip bot preamble from a summary and extract useful content."""
    if not summary:
        return None

    text = summary.strip()

    # Strip known bad prefixes
    for prefix in BAD_PREFIXES:
        if text.startswith(prefix):
            # Find first sentence boundary after the preamble
            # Look for the actual content (usually after a colon, period, or newline)
            after = text[len(prefix):]
            # Try to find where the actual content starts
            for sep in [":\n", ":\r\n", ". ", ".\n"]:
                if sep in after:
                    after = after.split(sep, 1)[1].strip()
                    break
            text = after
            break

    # If it's a markdown table summary, extract table title or first row content
    if "|" in text and "---" in text:
        lines = text.split("\n")
        # Try to find a non-table line first
        for line in lines:
            line = line.strip()
            if line and not line.startswith("|") and not line.startswith("---"):
                text = line
                break
        else:
            # Extract from title or first user message
            if first_user_msg:
                text = first_user_msg[:300]
            else:
                text = title or ""

    # Truncate to ~3 sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) > 3:
        text = " ".join(sentences[:3])

    # Final cleanup
    text = text.strip()
    if len(text) < 15:
        return None

    return text[:500]


def run_janitor():
    """Fix bot-voice summaries deterministically."""
    conn = get_db()

    # Find conversations with bot-voice summaries
    conditions = " OR ".join(f"c.summary LIKE ? " for _ in BAD_PREFIXES)
    params = [f"{p}%" for p in BAD_PREFIXES]
    rows = conn.execute(f"""
        SELECT c.id, c.title, c.summary,
               (SELECT content FROM messages WHERE conversation_id=c.id AND role='user'
                ORDER BY id LIMIT 1) as first_user_msg
        FROM conversations c
        JOIN sources s ON s.id=c.source_id
        WHERE s.name IN ('chatgpt', 'claude', 'llm_logs_html', 'llm_logs_pdf')
        AND ({conditions})
    """, params).fetchall()

    fixed = 0
    for r in rows:
        cleaned = extract_clean_summary(r["summary"], r["title"], r["first_user_msg"])
        if cleaned and cleaned != r["summary"]:
            conn.execute("UPDATE conversations SET summary=? WHERE id=?",
                         (cleaned, r["id"]))
            fixed += 1

    conn.commit()
    conn.close()
    print(f"Janitor: fixed {fixed} bot-voice summaries (out of {len(rows)} candidates)")


def run_messenger():
    """Generate summaries for SMS/Facebook/Google Chat from message content."""
    conn = get_db()

    rows = conn.execute("""
        SELECT c.id, c.title, c.message_count, c.created_at, c.char_count,
               s.name as source_name,
               (SELECT content FROM messages WHERE conversation_id=c.id
                ORDER BY id LIMIT 1) as first_msg,
               (SELECT group_concat(DISTINCT role) FROM messages
                WHERE conversation_id=c.id) as roles
        FROM conversations c
        JOIN sources s ON s.id=c.source_id
        WHERE s.name IN ('sms', 'facebook', 'google_chat', 'twitter')
        AND (c.summary IS NULL OR length(c.summary) < 15)
    """).fetchall()

    updated = 0
    for r in rows:
        parts = []

        # Title-based summary
        title = r["title"] or "Untitled"
        if title and title != "Untitled":
            parts.append(title)

        # First message preview
        first = (r["first_msg"] or "")[:150].strip()
        if first:
            # Clean up and truncate at sentence boundary
            first = first.split("\n")[0]
            if len(first) > 100:
                first = first[:100] + "..."
            parts.append(f'"{first}"')

        # Stats
        mc = r["message_count"] or 0
        date = (r["created_at"] or "")[:10]
        source = r["source_name"]
        if mc > 0:
            parts.append(f"{mc} messages via {source}")
        if date:
            parts.append(date)

        summary = " — ".join(parts) if parts else None
        if summary:
            conn.execute("UPDATE conversations SET summary=? WHERE id=?",
                         (summary[:500], r["id"]))
            updated += 1

    conn.commit()
    conn.close()
    print(f"Messenger: generated {updated} summaries for non-LLM conversations")


def run_curator():
    """Generate improved summary proposals for featured conversations."""
    os.makedirs(IMPROVEMENTS_DIR, exist_ok=True)
    conn = get_db()

    with open(os.path.join(IMPROVEMENTS_DIR, "featured_summaries.md"), "w",
              encoding="utf-8") as out:
        out.write("# Featured Summary Improvements\n\n")
        out.write("Review each proposal. Edit as needed, then run:\n")
        out.write("`python improve_summaries.py apply-featured`\n\n---\n\n")

        for conv_id in sorted(ALL_FEATURED):
            c = conn.execute("""
                SELECT c.id, c.title, c.summary, c.estimated_pages,
                       c.message_count, c.created_at, s.name as source_name
                FROM conversations c JOIN sources s ON s.id=c.source_id
                WHERE c.id=?
            """, (conv_id,)).fetchone()

            if not c:
                continue

            # Get tags
            tags = conn.execute("""
                SELECT t.name FROM conversation_tags ct
                JOIN tags t ON t.id=ct.tag_id WHERE ct.conversation_id=?
            """, (conv_id,)).fetchall()
            tag_names = [t["name"] for t in tags]

            # Get first 5 user messages
            user_msgs = conn.execute("""
                SELECT substr(content, 1, 300) as preview FROM messages
                WHERE conversation_id=? AND role='user'
                ORDER BY id LIMIT 5
            """, (conv_id,)).fetchall()

            # Get first 3 assistant messages
            asst_msgs = conn.execute("""
                SELECT substr(content, 1, 300) as preview FROM messages
                WHERE conversation_id=? AND role='assistant'
                ORDER BY id LIMIT 3
            """, (conv_id,)).fetchall()

            out.write(f"## CONVERSATION {c['id']}: {c['title']}\n\n")
            out.write(f"**Source:** {c['source_name']} | "
                      f"**Pages:** {c['estimated_pages']:.0f} | "
                      f"**Messages:** {c['message_count']} | "
                      f"**Date:** {(c['created_at'] or '')[:10]}\n")
            out.write(f"**Tags:** {', '.join(tag_names)}\n\n")

            current = c["summary"] or "(no summary)"
            out.write(f"**Current summary:**\n> {current[:300]}\n\n")

            out.write("**User message previews:**\n")
            for i, msg in enumerate(user_msgs, 1):
                preview = (msg["preview"] or "").replace("\n", " ")[:200]
                out.write(f"{i}. {preview}\n")

            out.write("\n**Assistant message previews:**\n")
            for i, msg in enumerate(asst_msgs, 1):
                preview = (msg["preview"] or "").replace("\n", " ")[:200]
                out.write(f"{i}. {preview}\n")

            out.write(f"\n**PROPOSED SUMMARY:**\n")
            out.write(f"> [Write 2-3 sentences following Template A from SUMMARYTEMPLATE.md]\n")
            out.write(f"\n---\n\n")

    conn.close()
    print(f"Curator: wrote proposals for {len(ALL_FEATURED)} featured conversations")
    print(f"  Output: improvements/featured_summaries.md")


def run_copywriter():
    """Generate improved copy proposals for collections and showcases."""
    os.makedirs(IMPROVEMENTS_DIR, exist_ok=True)
    conn = get_db()

    # Import the dicts from app.py
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from app import COLLECTIONS, SHOWCASES

    with open(os.path.join(IMPROVEMENTS_DIR, "copy_improvements.md"), "w",
              encoding="utf-8") as out:
        out.write("# Copy Improvements for app.py\n\n")
        out.write("Review each proposal. Edit, then paste into app.py.\n\n---\n\n")

        # Collections
        out.write("# COLLECTION DESCRIPTIONS\n\n")
        for slug, col in COLLECTIONS.items():
            conv_ids = col["conversation_ids"]
            if conv_ids:
                ph = ",".join("?" * len(conv_ids))
                convos = conn.execute(f"""
                    SELECT c.title, c.estimated_pages, c.summary
                    FROM conversations c WHERE c.id IN ({ph})
                    ORDER BY c.estimated_pages DESC
                """, conv_ids).fetchall()
            else:
                convos = []

            out.write(f"## Collection: {col['title']}\n\n")
            out.write(f"**Current description:**\n> {col.get('description', '(none)')}\n\n")
            out.write(f"**Conversations ({len(convos)}):**\n")
            for c in convos[:8]:
                out.write(f"- {c['title']} ({c['estimated_pages']:.0f}p)\n")
            out.write(f"\n**PROPOSED DESCRIPTION (Template B):**\n")
            out.write(f"> [2-4 sentences. Name specific texts/thinkers. State the thread.]\n\n---\n\n")

        # Showcases
        out.write("# SHOWCASE HOOKS & PEDAGOGY\n\n")
        for slug, sc in SHOWCASES.items():
            conv_ids = sc["conversation_ids"]
            if conv_ids:
                ph = ",".join("?" * len(conv_ids))
                convos = conn.execute(f"""
                    SELECT c.title, c.estimated_pages
                    FROM conversations c WHERE c.id IN ({ph})
                    ORDER BY c.estimated_pages DESC
                """, conv_ids).fetchall()
            else:
                convos = []

            out.write(f"## Showcase: {sc['title']}\n\n")
            out.write(f"**Current hook:** {sc.get('hook', '(none)')}\n")
            out.write(f"**Current pedagogy:** {sc.get('pedagogy', '(none)')}\n\n")
            out.write(f"**Conversations ({len(convos)}):**\n")
            for c in convos:
                out.write(f"- {c['title']} ({c['estimated_pages']:.0f}p)\n")
            out.write(f"\n**PROPOSED HOOK (Template C):**\n")
            out.write(f"> [1 sentence, 12-25 words, curiosity gap]\n\n")
            out.write(f"**PROPOSED PEDAGOGY (Template D paragraph 4):**\n")
            out.write(f"> [What cognitive skill the mechanic develops]\n\n---\n\n")

    conn.close()
    print(f"Copywriter: wrote proposals for {len(COLLECTIONS)} collections + {len(SHOWCASES)} showcases")
    print(f"  Output: improvements/copy_improvements.md")


def run_batch_export():
    """Export remaining conversations as ChatGPT batch files."""
    conn = get_db()
    batch_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "chunks", "summaries")
    os.makedirs(batch_dir, exist_ok=True)

    # Get all LLM conversations that still need good summaries
    # Skip: already featured (handled by curator), SMS/Facebook (handled by messenger)
    featured_ph = ",".join("?" * len(ALL_FEATURED))
    rows = conn.execute(f"""
        SELECT c.id, c.title, c.estimated_pages, c.created_at,
               (SELECT content FROM messages WHERE conversation_id=c.id AND role='user'
                ORDER BY id LIMIT 1) as first_user,
               (SELECT content FROM messages WHERE conversation_id=c.id AND role='assistant'
                ORDER BY id LIMIT 1) as first_asst
        FROM conversations c
        JOIN sources s ON s.id=c.source_id
        WHERE s.name IN ('chatgpt', 'claude', 'llm_logs_html', 'llm_logs_pdf')
        AND c.id NOT IN ({featured_ph})
        ORDER BY c.estimated_pages DESC
    """, ALL_FEATURED).fetchall()

    BATCH_SIZE = 20
    batch_num = 0
    file_count = 0

    prompt_header = """For each conversation below, provide a 2-3 sentence summary following this structure:

Sentence 1: WHAT — the core subject or idea, naming specific texts, concepts, or frameworks.
Sentence 2: HOW — what the user actually did (designed, summarized, debated, built).
Sentence 3: SO WHAT — what emerged (a design decision, new question, working prototype).

DO NOT start with "This conversation discusses..." or "In this conversation...".
DO NOT use words: various, interesting, explores, delve, comprehensive.
DO use specific nouns. Name texts, thinkers, tools, mechanics.

Output format for each:
CONVERSATION_ID: [id]
TITLE: [title]
SUMMARY: [your 2-3 sentence summary]
---

"""

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i + BATCH_SIZE]
        batch_num += 1
        filename = f"batch_{batch_num:03d}.md"
        filepath = os.path.join(batch_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(prompt_header)
            f.write(f"\n# Batch {batch_num} ({len(batch)} conversations)\n\n")

            for r in batch:
                f.write(f"## CONVERSATION_ID: {r['id']}\n")
                f.write(f"**Title:** {r['title']}\n")
                f.write(f"**Pages:** {r['estimated_pages']:.0f}\n")
                f.write(f"**Date:** {(r['created_at'] or '')[:10]}\n\n")

                user_preview = (r["first_user"] or "")[:2000]
                f.write(f"**First user message:**\n{user_preview}\n\n")

                asst_preview = (r["first_asst"] or "")[:2000]
                f.write(f"**First assistant response:**\n{asst_preview}\n\n")
                f.write("---\n\n")

        file_count += 1

    conn.close()
    print(f"Batcher: exported {file_count} batch files ({len(rows)} conversations)")
    print(f"  Output: chunks/summaries/batch_001.md through batch_{batch_num:03d}.md")


def run_batch_import(filepath):
    """Import ChatGPT summary responses back into database."""
    conn = get_db()

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse structured output
    entries = re.split(r'\n---\n', content)
    imported = 0

    for entry in entries:
        id_match = re.search(r'CONVERSATION_ID:\s*(\d+)', entry)
        sum_match = re.search(r'SUMMARY:\s*(.+?)(?:\n(?:CONVERSATION_ID|$))', entry, re.DOTALL)

        if id_match and sum_match:
            conv_id = int(id_match.group(1))
            summary = sum_match.group(1).strip()

            if len(summary) > 20:
                conn.execute("UPDATE conversations SET summary=? WHERE id=?",
                             (summary[:500], conv_id))
                imported += 1

    conn.commit()
    conn.close()
    print(f"Importer: imported {imported} summaries from {filepath}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "janitor":
        run_janitor()
    elif command == "messenger":
        run_messenger()
    elif command == "curator":
        run_curator()
    elif command == "copywriter":
        run_copywriter()
    elif command == "batch-export":
        run_batch_export()
    elif command == "batch-import":
        if len(sys.argv) < 3:
            print("Usage: python improve_summaries.py batch-import <file>")
            sys.exit(1)
        run_batch_import(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)
