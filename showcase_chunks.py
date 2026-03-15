"""
Dreambase — Showcase Batch Chunk Generator.
Produces paste-ready .md files for ChatGPT reading sessions.
Each file contains conversation excerpts + a structured extraction prompt.

Usage:
    python showcase_chunks.py                  # Generate all 3 showcases
    python showcase_chunks.py bubble-bog-witch # Generate one showcase

Output: chunks/showcases/<slug>/batch_001.md, batch_002.md, ...
"""

import os
import sqlite3
import sys
from schema import DB_PATH

CHUNK_SIZE = 50000  # ~12.5K tokens per batch — leaves room for prompt + response

# Same showcase definitions as app.py (design conversations only, no code dumps)
SHOWCASES = {
    "bubble-bog-witch": {
        "title": "Bubble Bog Witch",
        "conversation_ids": [40, 239, 3580, 2565],
    },
    "dungeon-autobattler": {
        "title": "Dungeon Autobattler",
        "conversation_ids": [4, 10, 37, 7, 2580, 2578, 2591, 2564, 2582, 2668, 2577, 3594],
    },
    "alchemy-board-game": {
        "title": "Alchemy Board Game",
        # Design conversations only — skip the 662pg Code Fix session (id=566)
        "conversation_ids": [567, 851, 2700, 347, 500, 531, 533, 511, 513, 2523, 2515],
    },
}

EXTRACTION_PROMPT = """You are reading conversations from a personal knowledge archaeology project called Dreambase.
These conversations are about the game concept: {title}.

For this batch, please extract:

1. **NARRATIVE** (3-5 paragraphs): Tell the story of this game idea — what is it, what makes it
   interesting, how did the design evolve across conversations? Write in third person present
   ("Ted explores..." not "I wanted to..."). Tone: intellectual but accessible, curious not pretentious.

2. **TIMELINE** (one entry per conversation in this batch):
   - DATE: (from conversation metadata)
   - TITLE: (conversation title)
   - DESCRIPTION: (1-2 sentences — what happened in this conversation, what design decisions were made)

3. **QUOTES** (3-5 best moments — lines that capture the creative energy):
   - QUOTE: (exact text, max 50 words)
   - ROLE: (user or assistant)
   - CONVERSATION: (which conversation it came from)

4. **DESIGN INSIGHTS** (2-3 key design decisions or innovations):
   - What mechanic or idea emerged?
   - Why is it interesting from a game design perspective?

5. **VISUAL THEMES** (for future illustration):
   - What visual imagery does this conversation suggest?
   - What art style would fit?

Format your response as clean markdown with these exact headers.
---

"""


def get_conversation_text(conn, conv_id, max_chars=None):
    """Extract conversation as readable text."""
    conv = conn.execute("""
        SELECT c.title, c.created_at, c.estimated_pages, s.name as source
        FROM conversations c JOIN sources s ON s.id=c.source_id
        WHERE c.id=?
    """, (conv_id,)).fetchone()

    if not conv:
        return "", ""

    header = f"## {conv[0]}\n**Source:** {conv[3]} | **Date:** {(conv[1] or 'unknown')[:10]} | **Pages:** {conv[2]:.0f}\n\n"

    messages = conn.execute("""
        SELECT role, content FROM messages
        WHERE conversation_id=? ORDER BY id
    """, (conv_id,)).fetchall()

    lines = []
    char_count = 0
    for msg in messages:
        role = (msg[0] or "unknown").upper()
        content = msg[1] or ""
        # Truncate very long assistant messages (likely code output)
        if len(content) > 8000 and role == "ASSISTANT":
            content = content[:4000] + "\n\n[... truncated — full message is " + str(len(content)) + " chars ...]\n\n" + content[-2000:]
        line = f"**{role}:** {content}\n\n"
        if max_chars and char_count + len(line) > max_chars:
            lines.append(f"\n[... remaining messages truncated at {max_chars} chars ...]\n")
            break
        lines.append(line)
        char_count += len(line)

    return header, "".join(lines)


def generate_chunks(slug):
    """Generate batch chunk files for a showcase."""
    sc = SHOWCASES.get(slug)
    if not sc:
        print(f"Unknown showcase: {slug}")
        return

    conn = sqlite3.connect(DB_PATH)
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "chunks", "showcases", slug)
    os.makedirs(out_dir, exist_ok=True)

    # Gather all conversation texts
    conv_texts = []
    for conv_id in sc["conversation_ids"]:
        header, body = get_conversation_text(conn, conv_id)
        if body:
            conv_texts.append((conv_id, header, body))

    conn.close()

    # Pack into batches respecting CHUNK_SIZE
    batch_num = 1
    current_batch = []
    current_size = 0
    prompt_size = len(EXTRACTION_PROMPT.format(title=sc["title"]))

    for conv_id, header, body in conv_texts:
        entry_size = len(header) + len(body)

        # If this single conversation exceeds chunk size, give it its own batch
        if entry_size > CHUNK_SIZE:
            # Flush current batch first
            if current_batch:
                write_batch(out_dir, batch_num, sc["title"], current_batch, prompt_size)
                batch_num += 1
                current_batch = []
                current_size = 0

            # Write oversized conversation as its own batch (truncated)
            truncated_body = body[:CHUNK_SIZE - len(header) - prompt_size - 500]
            truncated_body += f"\n\n[... truncated to fit batch. Full conversation is {entry_size} chars ...]\n"
            write_batch(out_dir, batch_num, sc["title"],
                       [(conv_id, header, truncated_body)], prompt_size)
            batch_num += 1
            continue

        # Would adding this overflow the batch?
        if current_size + entry_size > CHUNK_SIZE - prompt_size:
            write_batch(out_dir, batch_num, sc["title"], current_batch, prompt_size)
            batch_num += 1
            current_batch = []
            current_size = 0

        current_batch.append((conv_id, header, body))
        current_size += entry_size

    # Final batch
    if current_batch:
        write_batch(out_dir, batch_num, sc["title"], current_batch, prompt_size)
        batch_num += 1

    total = batch_num - 1
    print(f"  {sc['title']}: {total} batch files in {out_dir}")
    return total


def write_batch(out_dir, batch_num, title, entries, prompt_size):
    """Write a single batch file."""
    filename = f"batch_{batch_num:03d}.md"
    filepath = os.path.join(out_dir, filename)

    total_chars = sum(len(h) + len(b) for _, h, b in entries)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {title} — Batch {batch_num}\n")
        f.write(f"**Conversations in this batch:** {len(entries)} | **~{total_chars:,} chars**\n\n")
        f.write(EXTRACTION_PROMPT.format(title=title))

        for conv_id, header, body in entries:
            f.write(f"---\n\n")
            f.write(header)
            f.write(body)
            f.write("\n")

    print(f"    {filename}: {len(entries)} conversations, {total_chars:,} chars")


if __name__ == "__main__":
    slugs = sys.argv[1:] if len(sys.argv) > 1 else list(SHOWCASES.keys())

    print("Dreambase Showcase Chunk Generator")
    print("=" * 40)
    total_batches = 0
    for slug in slugs:
        if slug in SHOWCASES:
            n = generate_chunks(slug)
            if n:
                total_batches += n
        else:
            print(f"Unknown showcase: {slug}")

    print(f"\nTotal: {total_batches} batch files ready for ChatGPT reading sessions.")
    print("Workflow: paste each batch into ChatGPT, copy structured response,")
    print("save as chunks/showcases/<slug>/response_NNN.md")
