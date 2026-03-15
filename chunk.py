"""
Megabase Chunker — export conversations as GPT-ready .md chunk files.

Subcommands:
  export <id>        Export a single conversation
  export-tagged <tag> Export all conversations with a given tag
  export-ideas       Export all idea candidates
  list-big           Show conversations over N pages (for choosing what to deep-read)
"""

import os
import sys
import argparse
import sqlite3

from schema import get_db, DB_PATH

CHUNKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chunks", "reading")
PROMPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")

# Target chunk size in chars (~15K tokens for GPT-4)
CHUNK_SIZE = 60000


def load_prompt(prompt_name):
    """Load a prompt template from prompts/ directory."""
    path = os.path.join(PROMPTS_DIR, f"{prompt_name}.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def export_conversation(conn, conv_id, prompt_name="theme_summary"):
    """Export a conversation as chunked .md files."""
    conv = conn.execute(
        "SELECT c.id, c.title, c.created_at, c.estimated_pages, s.name "
        "FROM conversations c JOIN sources s ON s.id=c.source_id WHERE c.id=?",
        (conv_id,),
    ).fetchone()

    if not conv:
        print(f"Conversation {conv_id} not found.")
        return []

    conv_id, title, created, pages, source = conv

    msgs = conn.execute(
        "SELECT role, content, created_at FROM messages WHERE conversation_id=? ORDER BY id",
        (conv_id,),
    ).fetchall()

    if not msgs:
        print(f"No messages in conversation {conv_id}.")
        return []

    # Build full text with role markers
    full_parts = []
    for role, content, ts in msgs:
        if not content:
            continue
        header = f"[{role.upper()}]"
        if ts:
            header += f" ({ts[:10]})"
        full_parts.append(f"{header}\n{content}")

    full_text = "\n\n---\n\n".join(full_parts)

    # Load prompt template
    prompt = load_prompt(prompt_name)

    # Create output directory
    safe_title = "".join(c for c in title[:60] if c.isalnum() or c in " -_").strip()
    conv_dir = os.path.join(CHUNKS_DIR, f"{conv_id}_{safe_title}")
    os.makedirs(conv_dir, exist_ok=True)

    # Split into chunks at message boundaries
    chunks = []
    current_chunk = []
    current_size = 0

    for part in full_parts:
        part_len = len(part)
        if current_size + part_len > CHUNK_SIZE and current_chunk:
            chunks.append("\n\n---\n\n".join(current_chunk))
            current_chunk = [part]
            current_size = part_len
        else:
            current_chunk.append(part)
            current_size += part_len

    if current_chunk:
        chunks.append("\n\n---\n\n".join(current_chunk))

    total_chunks = len(chunks)
    files = []

    for i, chunk_text in enumerate(chunks):
        chunk_num = i + 1
        filename = f"chunk_{chunk_num:02d}.md"
        filepath = os.path.join(conv_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(f"**Source:** {source} | **Date:** {created or 'unknown'} | ")
            f.write(f"**Pages:** {pages:.0f} | **Chunk {chunk_num}/{total_chunks}**\n\n")

            if prompt and chunk_num == 1:
                f.write(f"## Analysis Prompt\n\n{prompt}\n\n")

            f.write(f"---\n\n")
            f.write(chunk_text)

            if chunk_num < total_chunks:
                f.write(f"\n\n---\n\n*Continue to chunk_{chunk_num+1:02d}.md for more.*\n")

        files.append(filepath)

    # Record in DB
    for i, fp in enumerate(files):
        conn.execute(
            "INSERT INTO chunk_exports (conversation_id, chunk_number, file_path, char_count, exported_at) "
            "VALUES (?, ?, ?, ?, datetime('now'))",
            (conv_id, i + 1, fp, os.path.getsize(fp)),
        )
    conn.commit()

    print(f"  [{conv_id}] {title}: {total_chunks} chunks ({pages:.0f} pages)")
    return files


def list_big(conn, min_pages=50, tag=None):
    """List conversations over a threshold, optionally filtered by tag."""
    if tag:
        rows = conn.execute("""
            SELECT c.id, c.title, s.name, c.estimated_pages, c.message_count
            FROM conversations c
            JOIN sources s ON s.id=c.source_id
            JOIN conversation_tags ct ON ct.conversation_id=c.id
            JOIN tags t ON t.id=ct.tag_id
            WHERE t.name=? AND c.estimated_pages >= ?
            ORDER BY c.estimated_pages DESC
        """, (tag, min_pages)).fetchall()
    else:
        rows = conn.execute("""
            SELECT c.id, c.title, s.name, c.estimated_pages, c.message_count
            FROM conversations c JOIN sources s ON s.id=c.source_id
            WHERE c.estimated_pages >= ?
            ORDER BY c.estimated_pages DESC
        """, (min_pages,)).fetchall()

    print(f"\n{'ID':>6} {'Pages':>6} {'Msgs':>6} {'Source':<15} Title")
    print("-" * 80)
    for cid, title, source, pages, msgs in rows:
        t = (title or "")[:45]
        print(f"{cid:>6} {pages:>6.0f} {msgs:>6} {source:<15} {t}")
    print(f"\n{len(rows)} conversations over {min_pages} pages")


def main():
    parser = argparse.ArgumentParser(description="Megabase Chunker")
    sub = parser.add_subparsers(dest="command")

    exp = sub.add_parser("export", help="Export a single conversation")
    exp.add_argument("id", type=int, help="Conversation ID")
    exp.add_argument("--prompt", default="theme_summary", help="Prompt template name")

    expt = sub.add_parser("export-tagged", help="Export all conversations with a tag")
    expt.add_argument("tag", help="Tag name")
    expt.add_argument("--min-pages", type=float, default=10, help="Minimum pages to export")
    expt.add_argument("--prompt", default="theme_summary", help="Prompt template name")

    sub.add_parser("export-ideas", help="Export all idea candidates")

    lb = sub.add_parser("list-big", help="List big conversations")
    lb.add_argument("--min-pages", type=float, default=50, help="Minimum page threshold")
    lb.add_argument("--tag", help="Filter by tag")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    conn = get_db()

    if args.command == "export":
        export_conversation(conn, args.id, args.prompt)

    elif args.command == "export-tagged":
        rows = conn.execute("""
            SELECT c.id FROM conversations c
            JOIN conversation_tags ct ON ct.conversation_id=c.id
            JOIN tags t ON t.id=ct.tag_id
            WHERE t.name=? AND c.estimated_pages >= ?
            ORDER BY c.estimated_pages DESC
        """, (args.tag, args.min_pages)).fetchall()
        print(f"Exporting {len(rows)} conversations tagged '{args.tag}' (>={args.min_pages} pages)...")
        for (cid,) in rows:
            export_conversation(conn, cid, args.prompt)

    elif args.command == "export-ideas":
        rows = conn.execute("""
            SELECT DISTINCT conversation_id FROM ideas ORDER BY conversation_id
        """).fetchall()
        print(f"Exporting {len(rows)} idea conversations...")
        for (cid,) in rows:
            export_conversation(conn, cid, "idea_extraction")

    elif args.command == "list-big":
        list_big(conn, min_pages=args.min_pages, tag=getattr(args, 'tag', None))

    conn.close()


if __name__ == "__main__":
    main()
