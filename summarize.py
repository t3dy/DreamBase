"""
Megabase Summarizer — hybrid deterministic + ChatGPT batch workflow.

Subcommands:
  auto          Extract first assistant response as provisional summary (instant, free)
  batch-export  Generate .md files with conversation excerpts for ChatGPT summarization
  batch-import  Parse ChatGPT's structured responses back into the DB
"""

import os
import sys
import re
import argparse
import sqlite3

from schema import get_db, DB_PATH

CHUNKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chunks", "summaries")

# How many conversations per batch file
BATCH_SIZE = 50

# How many chars of conversation to include per excerpt
EXCERPT_CHARS = 3000


def auto_summarize(conn):
    """Extract first assistant response (truncated) as provisional summary for all conversations."""
    print("Running auto-summarize (deterministic excerpts)...")

    rows = conn.execute("""
        SELECT c.id,
               (SELECT content FROM messages
                WHERE conversation_id=c.id AND role='assistant'
                ORDER BY id LIMIT 1) as first_response
        FROM conversations c
        WHERE c.summary IS NULL OR c.summary = ''
    """).fetchall()

    count = 0
    for conv_id, first_response in rows:
        if not first_response:
            continue
        # Take first 500 chars, clean up, end at sentence boundary if possible
        excerpt = first_response[:500].strip()
        # Try to end at a sentence
        last_period = excerpt.rfind(".")
        if last_period > 200:
            excerpt = excerpt[:last_period + 1]
        conn.execute("UPDATE conversations SET summary=? WHERE id=?", (excerpt, conv_id))
        count += 1

    conn.commit()
    print(f"Auto-summarized {count} conversations with first-response excerpts.")


def batch_export(conn, tag_filter=None):
    """Generate batch .md files for ChatGPT summarization.
    Groups conversations by BATCH_SIZE, includes title + first EXCERPT_CHARS of content."""

    os.makedirs(CHUNKS_DIR, exist_ok=True)

    # Build query — optionally filter by tag
    if tag_filter:
        query = """
            SELECT c.id, c.title, c.source_id, s.name as source_name, c.estimated_pages
            FROM conversations c
            JOIN sources s ON s.id=c.source_id
            JOIN conversation_tags ct ON ct.conversation_id=c.id
            JOIN tags t ON t.id=ct.tag_id
            WHERE t.name=?
            ORDER BY c.estimated_pages DESC
        """
        convos = conn.execute(query, (tag_filter,)).fetchall()
        label = tag_filter
    else:
        # All tagged conversations, prioritized by page count
        query = """
            SELECT DISTINCT c.id, c.title, c.source_id, s.name as source_name, c.estimated_pages
            FROM conversations c
            JOIN sources s ON s.id=c.source_id
            JOIN conversation_tags ct ON ct.conversation_id=c.id
            ORDER BY c.estimated_pages DESC
        """
        convos = conn.execute(query).fetchall()
        label = "all_tagged"

    print(f"Exporting {len(convos)} conversations for ChatGPT summarization (tag={label})...")

    batch_num = 0
    files_written = []

    for i in range(0, len(convos), BATCH_SIZE):
        batch = convos[i:i + BATCH_SIZE]
        batch_num += 1
        filename = f"batch_{label}_{batch_num:03d}.md"
        filepath = os.path.join(CHUNKS_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Summarization Batch {batch_num} ({label})\n\n")
            f.write("For each conversation below, provide:\n")
            f.write("- CONV_ID: (the number shown)\n")
            f.write("- SUMMARY: (exactly 3 sentences describing what was discussed and decided)\n")
            f.write("- TAGS: (comma-separated from: game_idea, app_project, educational, alchemy, pkd, mtg, esoteric, coding, personal, other)\n")
            f.write("- IDEA: (if this contains a game/app/edu product idea, describe it in 1 sentence; otherwise \"none\")\n\n")
            f.write("---\n\n")

            for conv_id, title, source_id, source_name, pages in batch:
                # Get excerpt from messages
                msgs = conn.execute(
                    "SELECT role, content FROM messages WHERE conversation_id=? ORDER BY id",
                    (conv_id,),
                ).fetchall()

                excerpt_parts = []
                total_chars = 0
                for role, content in msgs:
                    if not content:
                        continue
                    remaining = EXCERPT_CHARS - total_chars
                    if remaining <= 0:
                        break
                    chunk = content[:remaining]
                    excerpt_parts.append(f"[{role}] {chunk}")
                    total_chars += len(chunk)

                excerpt = "\n".join(excerpt_parts)

                f.write(f"## CONV_ID: {conv_id}\n")
                f.write(f"**Title:** {title}\n")
                f.write(f"**Source:** {source_name} | **Pages:** {pages:.0f}\n\n")
                f.write(f"```\n{excerpt}\n```\n\n---\n\n")

        files_written.append(filepath)

    print(f"Wrote {len(files_written)} batch files to {CHUNKS_DIR}/")
    print(f"  {BATCH_SIZE} conversations per file, {EXCERPT_CHARS} chars excerpt each")
    print(f"  Paste each file into ChatGPT and save the response as response_NNN.md")


def batch_import(response_file, conn):
    """Parse a ChatGPT response file and update conversations in the DB."""
    if not os.path.exists(response_file):
        print(f"ERROR: {response_file} not found")
        sys.exit(1)

    with open(response_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse structured responses — looking for CONV_ID, SUMMARY, TAGS, IDEA blocks
    blocks = re.split(r"(?:^|\n)(?:#+\s*)?CONV_ID:\s*(\d+)", content)

    updated = 0
    ideas_added = 0

    # blocks[0] is preamble, then alternating (id, content) pairs
    for i in range(1, len(blocks) - 1, 2):
        try:
            conv_id = int(blocks[i])
        except ValueError:
            continue
        block_text = blocks[i + 1]

        # Extract SUMMARY
        summary_match = re.search(r"SUMMARY:\s*(.+?)(?:\n(?:TAGS|IDEA)|$)", block_text, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else None

        # Extract TAGS
        tags_match = re.search(r"TAGS:\s*(.+?)(?:\n|$)", block_text)
        tags_str = tags_match.group(1).strip() if tags_match else ""

        # Extract IDEA
        idea_match = re.search(r"IDEA:\s*(.+?)(?:\n|$)", block_text)
        idea_str = idea_match.group(1).strip() if idea_match else ""

        if summary:
            conn.execute("UPDATE conversations SET summary=? WHERE id=?", (summary, conv_id))
            updated += 1

        # Update tags (add LLM-tagged ones with higher confidence)
        if tags_str and tags_str.lower() != "none":
            tag_names = [t.strip().lower().replace(" ", "_") for t in tags_str.split(",")]
            for tag_name in tag_names:
                # Ensure tag exists
                conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
                tag_id_row = conn.execute("SELECT id FROM tags WHERE name=?", (tag_name,)).fetchone()
                if tag_id_row:
                    conn.execute(
                        "INSERT OR REPLACE INTO conversation_tags (conversation_id, tag_id, confidence, method) "
                        "VALUES (?, ?, 0.9, 'llm')",
                        (conv_id, tag_id_row[0]),
                    )

        # Add idea if present
        if idea_str and idea_str.lower() not in ("none", "n/a", ""):
            title = conn.execute("SELECT title FROM conversations WHERE id=?", (conv_id,)).fetchone()
            conn.execute(
                "INSERT INTO ideas (conversation_id, name, description, method, created_at) "
                "VALUES (?, ?, ?, 'llm', datetime('now'))",
                (conv_id, title[0] if title else "Untitled", idea_str),
            )
            ideas_added += 1

    conn.commit()
    print(f"Imported {updated} summaries, {ideas_added} new ideas from {response_file}")


def main():
    parser = argparse.ArgumentParser(description="Megabase Summarizer")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("auto", help="Deterministic auto-summarize using first assistant response")

    exp = sub.add_parser("batch-export", help="Export batch files for ChatGPT summarization")
    exp.add_argument("--tag", help="Only export conversations with this tag")

    imp = sub.add_parser("batch-import", help="Import ChatGPT response file")
    imp.add_argument("file", help="Path to response .md file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    conn = get_db()

    if args.command == "auto":
        auto_summarize(conn)
    elif args.command == "batch-export":
        batch_export(conn, tag_filter=args.tag)
    elif args.command == "batch-import":
        batch_import(args.file, conn)

    conn.close()


if __name__ == "__main__":
    main()
