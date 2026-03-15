"""
Agent J4: Response Parser & Integrator

Parses Claude desktop responses for untagged giants.
Updates megabase.db with tags and summaries.
Reports which conversations need new collections or scholar pages.

Expected response format per conversation (from Claude desktop):
    **ID: 712 — Medieval Magic Summary Request**
    1. **TAGS**: esoteric, history
    2. **SUMMARY**: ...three sentences...
    3. **COLLECTION**: alchemy-scholarship
    4. **SCHOLAR**: dee, fludd

Usage:
    python parse_responses.py <response_file.md>
    python parse_responses.py --all     (process all files in chunks/untagged_skim/responses/)
    python parse_responses.py --report  (show status of all manifest entries)
"""

import json
import os
import re
import sqlite3
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "megabase.db")
MANIFEST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "untagged_manifest.json")
RESPONSES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chunks", "untagged_skim", "responses")

# Existing tags in the DB
KNOWN_TAGS = {
    "game_idea", "app_project", "educational", "alchemy", "pkd", "mtg",
    "esoteric", "coding", "personal", "history", "literature", "science",
    "mathematics", "art", "music", "linguistics", "psychology", "philosophy",
}


def parse_response_file(filepath):
    """Parse a Claude desktop response file into per-conversation entries."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    entries = []
    # Split on conversation headers: "**ID: NNN — Title**" or "## ID NNN" or similar
    # Be flexible about format since Claude desktop output varies
    sections = re.split(r'(?:^|\n)(?:\*\*ID:\s*|##\s*ID\s*)(\d+)', text)

    # sections[0] is preamble, then alternating: id, content, id, content...
    for i in range(1, len(sections) - 1, 2):
        conv_id = int(sections[i])
        content = sections[i + 1]
        entry = parse_single_entry(conv_id, content)
        if entry:
            entries.append(entry)

    # Fallback: try to find IDs mentioned anywhere if structured splitting failed
    if not entries:
        # Try line-by-line parsing
        entries = parse_freeform(text)

    return entries


def parse_single_entry(conv_id, text):
    """Extract tags, summary, collection, scholar from a section of text."""
    entry = {"id": conv_id, "tags": [], "summary": "", "collection": "", "scholar": ""}

    # Extract TAGS
    tags_match = re.search(r'(?:TAGS|Tags)[:\s]*([^\n]+)', text)
    if tags_match:
        raw_tags = tags_match.group(1).strip().strip("*").strip().lstrip(":").strip()
        entry["tags"] = [t.strip().lower().replace(" ", "_").lstrip(":").lstrip("_").strip()
                         for t in re.split(r'[,;]', raw_tags)
                         if t.strip().lstrip(":").lstrip("_").strip()]

    # Extract SUMMARY
    summary_match = re.search(r'(?:SUMMARY|Summary)[:\s]*(.+?)(?=\n\s*\d+\.|$|\n\s*\*\*)', text, re.DOTALL)
    if summary_match:
        entry["summary"] = summary_match.group(1).strip().strip("*").strip()

    # Extract COLLECTION
    coll_match = re.search(r'(?:COLLECTION|Collection)[:\s]*([^\n]+)', text)
    if coll_match:
        entry["collection"] = coll_match.group(1).strip().strip("*").strip()

    # Extract SCHOLAR
    scholar_match = re.search(r'(?:SCHOLAR|Scholar)[:\s]*([^\n]+)', text)
    if scholar_match:
        entry["scholar"] = scholar_match.group(1).strip().strip("*").strip()

    return entry


def parse_freeform(text):
    """Fallback parser for less structured responses."""
    entries = []
    # Look for any pattern like "ID 712" or "ID: 712" followed by content
    for match in re.finditer(r'ID[:\s]+(\d+)[^\n]*\n((?:(?!ID[:\s]+\d).)*)', text, re.DOTALL):
        conv_id = int(match.group(1))
        content = match.group(2)
        entry = parse_single_entry(conv_id, content)
        if entry:
            entries.append(entry)
    return entries


def ensure_tag_exists(conn, tag_name):
    """Create tag if it doesn't exist, return tag_id."""
    row = conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,)).fetchone()
    if row:
        return row[0]
    conn.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
    return conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,)).fetchone()[0]


def apply_entry(conn, entry, dry_run=False):
    """Apply parsed entry to the database."""
    conv_id = entry["id"]

    # Verify conversation exists
    exists = conn.execute("SELECT id FROM conversations WHERE id = ?", (conv_id,)).fetchone()
    if not exists:
        print(f"  WARNING: Conversation {conv_id} not found in DB — skipping")
        return False

    if dry_run:
        print(f"  [DRY RUN] Would apply to {conv_id}: tags={entry['tags']}, collection={entry['collection']}")
        return True

    # Apply tags
    for tag_name in entry["tags"]:
        tag_id = ensure_tag_exists(conn, tag_name)
        try:
            conn.execute(
                "INSERT OR IGNORE INTO conversation_tags (conversation_id, tag_id, confidence, method) "
                "VALUES (?, ?, 0.9, 'llm')",
                (conv_id, tag_id)
            )
        except sqlite3.IntegrityError:
            pass  # Already tagged

    # Update summary if provided and current summary is sparse
    if entry["summary"]:
        current = conn.execute("SELECT summary FROM conversations WHERE id = ?", (conv_id,)).fetchone()[0]
        if not current or len(current) < 50:
            conn.execute("UPDATE conversations SET summary = ? WHERE id = ?",
                         (entry["summary"], conv_id))

    conn.commit()
    return True


def report_status(conn):
    """Show which manifest entries have been tagged."""
    if not os.path.exists(MANIFEST_PATH):
        print("No manifest found. Run census_untagged.py first.")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    tagged = 0
    untagged = 0
    print(f"\n{'ID':>6} {'Pages':>6} {'Tags':>5} {'Status':<10} Title")
    print("-" * 80)

    for entry in manifest:
        tag_count = conn.execute(
            "SELECT count(*) FROM conversation_tags WHERE conversation_id = ?",
            (entry["id"],)
        ).fetchone()[0]

        status = "TAGGED" if tag_count > 0 else "PENDING"
        if tag_count:
            tagged += 1
        else:
            untagged += 1

        title_safe = entry['title'][:45].encode('ascii', 'replace').decode()
        print(f"  {entry['id']:>4} {entry['pages']:>6.0f} {tag_count:>5} {status:<10} {title_safe}")

    print(f"\nTagged: {tagged}/{len(manifest)} | Pending: {untagged}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python parse_responses.py <response_file.md>")
        print("  python parse_responses.py --all")
        print("  python parse_responses.py --report")
        print("  python parse_responses.py --dry-run <response_file.md>")
        return

    conn = sqlite3.connect(DB_PATH)

    if sys.argv[1] == "--report":
        report_status(conn)
        conn.close()
        return

    dry_run = "--dry-run" in sys.argv

    if "--all" in sys.argv:
        if not os.path.exists(RESPONSES_DIR):
            print(f"No responses directory found at {RESPONSES_DIR}")
            print("Create it and paste Claude desktop responses as .md files there.")
            conn.close()
            return

        files = sorted(f for f in os.listdir(RESPONSES_DIR) if f.endswith(".md"))
        if not files:
            print(f"No .md files found in {RESPONSES_DIR}")
            conn.close()
            return

        total = 0
        for fname in files:
            filepath = os.path.join(RESPONSES_DIR, fname)
            print(f"\nProcessing: {fname}")
            entries = parse_response_file(filepath)
            print(f"  Found {len(entries)} entries")
            for entry in entries:
                if apply_entry(conn, entry, dry_run):
                    total += 1
                    tags_str = ", ".join(entry["tags"][:5])
                    print(f"  ID {entry['id']}: [{tags_str}] -> {entry['collection']}")

        print(f"\nTotal: {total} entries applied" + (" (dry run)" if dry_run else ""))

    else:
        filepath = sys.argv[-1]
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            conn.close()
            return

        print(f"Processing: {filepath}")
        entries = parse_response_file(filepath)
        print(f"Found {len(entries)} entries\n")

        for entry in entries:
            if apply_entry(conn, entry, dry_run):
                tags_str = ", ".join(entry["tags"][:5])
                coll = entry["collection"] or "uncollected"
                scholar = entry["scholar"] or "none"
                print(f"  ID {entry['id']:>5}: tags=[{tags_str}] collection={coll} scholar={scholar}")

        if not entries:
            print("No entries parsed. Check the response format.")
            print("Expected format:")
            print("  **ID: 712 — Title**")
            print("  1. **TAGS**: tag1, tag2")
            print("  2. **SUMMARY**: Three sentences.")
            print("  3. **COLLECTION**: collection-slug")
            print("  4. **SCHOLAR**: scholar-name")

    conn.close()


if __name__ == "__main__":
    main()
