"""
Agent J2: Skim Exporter for Untagged Giants

Reads untagged_manifest.json, exports first 12,000 chars of each
conversation as .md files, batched 4 per file for Claude desktop reading.
"""

import json
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "megabase.db")
MANIFEST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "untagged_manifest.json")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chunks", "untagged_skim")
SKIM_CHARS = 12000
BATCH_SIZE = 4

PROMPT = """## Reading Task

For this conversation, provide:

1. **TAGS** (comma-separated from controlled vocabulary: game_idea, app_project, educational, alchemy, esoteric, pkd, mtg, coding, philosophy, personal, history, literature, science, mathematics, art, music, linguistics, psychology): Choose all that apply.
2. **SUMMARY** (exactly 3 sentences): What is this conversation about? What was accomplished? What's its significance?
3. **COLLECTION** (which existing collection it fits, or 'NEW: [name]'): Options are alchemy-scholarship, pkd-literary, philosophy, dark-horses, game-design, music-engineering, meta-learning, code-architecture, web-design — or suggest a new collection.
4. **SCHOLAR** (which scholar page it relates to, or 'NONE'): e.g., crowley, dee, fludd, paracelsus, bruno, hermes, etc.

---

"""


def export_skim(conn, entry):
    """Export first SKIM_CHARS of a conversation as .md."""
    conv_id = entry["id"]

    msgs = conn.execute(
        "SELECT role, content, created_at FROM messages "
        "WHERE conversation_id=? ORDER BY id",
        (conv_id,),
    ).fetchall()

    if not msgs:
        print(f"  [{conv_id}] No messages — skipping")
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
        f.write(f"**Pages:** {entry['pages']:.0f} | **Messages:** {entry.get('message_count', '?')}\n\n")
        f.write(f"**Current Summary:** {entry['first_500_chars_of_summary'][:200] or 'NONE'}\n\n")
        f.write(PROMPT)
        f.write(skim_text)

    return filepath


def main():
    if not os.path.exists(MANIFEST_PATH):
        print(f"ERROR: {MANIFEST_PATH} not found. Run census_untagged.py first.")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    print(f"Loaded manifest with {len(manifest)} entries")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    batch_dir = os.path.join(OUTPUT_DIR, "batches")
    os.makedirs(batch_dir, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    files = []
    print(f"\n{'ID':>7} {'Pages':>7}  {'Source':<16} Title")
    print("-" * 90)

    for entry in manifest:
        fp = export_skim(conn, entry)
        if fp:
            files.append(fp)
            title_safe = entry['title'][:50].encode('ascii', 'replace').decode()
        print(f"  {entry['id']:>5} {entry['pages']:>7.0f}p  {entry['source']:<16} {title_safe}")

    # Create batch files (4 per batch)
    for i in range(0, len(files), BATCH_SIZE):
        batch_files = files[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        batch_path = os.path.join(batch_dir, f"batch_{batch_num:02d}.md")

        with open(batch_path, "w", encoding="utf-8") as bf:
            bf.write(f"# Untagged Giants — Batch {batch_num}\n\n")
            bf.write(f"**{len(batch_files)} conversations** — read each and provide TAGS, SUMMARY, COLLECTION, SCHOLAR as requested.\n\n")
            bf.write("---\n\n")
            for fp in batch_files:
                with open(fp, "r", encoding="utf-8") as sf:
                    bf.write(sf.read())
                bf.write("\n\n" + "=" * 80 + "\n\n")

        size_kb = os.path.getsize(batch_path) / 1024
        print(f"\n  Batch {batch_num}: {len(batch_files)} conversations ({size_kb:.0f} KB) -> {os.path.basename(batch_path)}")

    conn.close()

    num_batches = (len(files) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"\nDone. {len(files)} individual skims + {num_batches} batch files.")
    print(f"Individual files: {OUTPUT_DIR}")
    print(f"Batch files:      {batch_dir}")
    print(f"\nNext: Open each batch in Claude desktop and paste for tagging.")


if __name__ == "__main__":
    main()
