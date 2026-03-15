"""
Ingest Google Chat messages from Takeout export into the megabase.
Structure: Google Chat/Groups/<DM name>/messages.json + group_info.json
           Google Chat/Users/<user id>/messages.json
"""

import os
import sys
import json
import logging
from datetime import datetime

from schema import get_db, create_db, register_source, update_conversation_stats

logger = logging.getLogger("ingest_google_chat")

DEFAULT_SRC = os.path.expanduser("~/Downloads/Takeout/Google Chat")


def parse_gc_date(date_str):
    """Parse Google Chat date format: 'Monday, July 22, 2013 at 6:35:25 PM UTC'"""
    if not date_str:
        return None
    try:
        # Remove day name and 'at'
        cleaned = date_str.replace(" at ", " ")
        # Remove day of week
        parts = cleaned.split(", ", 1)
        if len(parts) > 1:
            cleaned = parts[1]
        # Try parsing
        for fmt in ("%B %d, %Y %I:%M:%S %p %Z", "%B %d, %Y %I:%M:%S %p"):
            try:
                return datetime.strptime(cleaned, fmt).isoformat()
            except ValueError:
                continue
    except Exception:
        pass
    return None


def ingest(src_path=None, db_path=None):
    src = src_path or DEFAULT_SRC
    if not os.path.isdir(src):
        print(f"ERROR: {src} not found")
        sys.exit(1)

    conn = get_db(db_path)
    create_db(db_path)
    conn = get_db(db_path)

    source_id = register_source(conn, "google_chat", src)

    # Clear previous
    existing = conn.execute("SELECT id FROM conversations WHERE source_id=?", (source_id,)).fetchall()
    if existing:
        ids = [r[0] for r in existing]
        ph = ",".join("?" * len(ids))
        conn.execute(f"DELETE FROM messages WHERE conversation_id IN ({ph})", ids)
        conn.execute(f"DELETE FROM conversations WHERE id IN ({ph})", ids)
        conn.commit()

    total_convos = 0
    total_msgs = 0

    # Process both Groups and Users directories
    for subdir in ("Groups", "Users"):
        chat_dir = os.path.join(src, subdir)
        if not os.path.isdir(chat_dir):
            continue

        for thread_name in os.listdir(chat_dir):
            thread_path = os.path.join(chat_dir, thread_name)
            if not os.path.isdir(thread_path):
                continue

            messages_file = os.path.join(thread_path, "messages.json")
            if not os.path.exists(messages_file):
                continue

            # Get group info for title
            title = thread_name
            group_info_file = os.path.join(thread_path, "group_info.json")
            if os.path.exists(group_info_file):
                try:
                    with open(group_info_file, "r", encoding="utf-8") as f:
                        info = json.load(f)
                    members = [m.get("name", "") for m in info.get("members", [])]
                    other = [m for m in members if m and m != "Ted Hand"]
                    if other:
                        title = "GChat: " + ", ".join(other[:3])
                except Exception:
                    pass

            try:
                with open(messages_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read {messages_file}: {e}")
                continue

            msgs = data.get("messages", [])
            if not msgs:
                continue

            # Get date range
            dates = [parse_gc_date(m.get("created_date")) for m in msgs]
            dates = [d for d in dates if d]
            created = min(dates) if dates else None
            updated = max(dates) if dates else None

            cur = conn.execute(
                "INSERT INTO conversations (source_id, external_id, title, created_at, updated_at, folder_path) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (source_id, f"{subdir}/{thread_name}", title, created, updated, thread_path),
            )
            conv_id = cur.lastrowid

            for msg in msgs:
                sender = msg.get("creator", {}).get("name", "")
                text = msg.get("text", "")
                if not text:
                    continue
                msg_time = parse_gc_date(msg.get("created_date"))
                role = "user" if "Ted" in sender else "sender"

                conn.execute(
                    "INSERT INTO messages (conversation_id, role, content, created_at, char_count) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (conv_id, role, text, msg_time, len(text)),
                )
                total_msgs += 1

            update_conversation_stats(conn, conv_id)
            total_convos += 1

    conn.commit()
    conn.close()
    print(f"Ingested {total_convos} conversations, {total_msgs} messages from Google Chat.")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else None
    ingest(src_path=src)
