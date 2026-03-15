"""
Agent J1: Census of Untagged Giants

Queries megabase.db for all untagged conversations over 100 pages,
excluding personal sources (SMS, Facebook, Twitter, Google Chat).
Deduplicates cross-source copies (same title → prefer chatgpt source).
Outputs untagged_manifest.json.
"""

import json
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "megabase.db")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "untagged_manifest.json")

# Personal sources handled by Workstream K
PERSONAL_SOURCES = ("sms", "facebook", "twitter", "google_chat")

# Minimum page threshold
MIN_PAGES = 100
# Fallback if fewer than 15 found
FALLBACK_MIN_PAGES = 50


def get_untagged_giants(conn, min_pages):
    """Query all untagged conversations above min_pages, excluding personal sources."""
    placeholders = ",".join("?" for _ in PERSONAL_SOURCES)
    rows = conn.execute(f"""
        SELECT c.id, c.title, c.estimated_pages, s.name as source,
               c.summary, c.created_at, c.message_count, c.char_count
        FROM conversations c
        JOIN sources s ON c.source_id = s.id
        WHERE c.id NOT IN (SELECT conversation_id FROM conversation_tags)
          AND c.estimated_pages > ?
          AND s.name NOT IN ({placeholders})
        ORDER BY c.estimated_pages DESC
    """, (min_pages, *PERSONAL_SOURCES)).fetchall()
    return rows


def deduplicate(rows):
    """Remove cross-source duplicates. For same title, prefer chatgpt > llm_logs_html > llm_logs_pdf."""
    source_priority = {"chatgpt": 0, "llm_logs_html": 1, "llm_logs_pdf": 2, "claude": 3, "pkd_chats": 4, "gmail": 5}
    by_title = {}
    for row in rows:
        title = row[1]
        source = row[3]
        priority = source_priority.get(source, 99)
        if title not in by_title or priority < by_title[title][1]:
            by_title[title] = (row, priority)

    return [entry[0] for entry in by_title.values()]


def build_manifest(conn, rows):
    """Build the manifest with first 500 chars of summary for each conversation."""
    manifest = []
    for row in rows:
        conv_id, title, pages, source, summary, created_at, msg_count, char_count = row
        # Get first 500 chars of actual content if summary is sparse
        first_content = ""
        if summary:
            first_content = summary[:500]
        else:
            content_row = conn.execute("""
                SELECT substr(content, 1, 500)
                FROM messages
                WHERE conversation_id = ? AND content IS NOT NULL AND content != ''
                ORDER BY id
                LIMIT 1
            """, (conv_id,)).fetchone()
            if content_row:
                first_content = content_row[0]

        manifest.append({
            "id": conv_id,
            "title": title,
            "pages": round(pages, 1),
            "source": source,
            "created_at": created_at,
            "message_count": msg_count,
            "char_count": char_count,
            "first_500_chars_of_summary": first_content
        })

    # Sort by pages descending
    manifest.sort(key=lambda x: x["pages"], reverse=True)
    return manifest


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = None

    # Try with standard threshold
    rows = get_untagged_giants(conn, MIN_PAGES)
    print(f"Found {len(rows)} untagged conversations > {MIN_PAGES} pages")

    # Deduplicate
    deduped = deduplicate(rows)
    print(f"After deduplication: {len(deduped)} unique conversations")

    # Fallback if too few
    if len(deduped) < 15:
        print(f"Fewer than 15 found, lowering threshold to {FALLBACK_MIN_PAGES} pages...")
        rows = get_untagged_giants(conn, FALLBACK_MIN_PAGES)
        deduped = deduplicate(rows)
        print(f"With lower threshold: {len(deduped)} unique conversations")

    manifest = build_manifest(conn, deduped)
    conn.close()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\nManifest written to {OUTPUT_PATH}")
    print(f"Total entries: {len(manifest)}")
    print(f"\nTop 15 by pages:")
    for entry in manifest[:15]:
        print(f"  ID {entry['id']:>5} | {entry['pages']:>7.0f}p | {entry['source']:<15} | {entry['title'][:60]}")


if __name__ == "__main__":
    main()
