"""
Ingest Facebook Messenger threads from Takeout export into the megabase.
Each inbox folder has message_1.json (and possibly message_2.json etc.) with participants and messages.
"""

import os
import sys
import json
import logging
from datetime import datetime

from schema import get_db, create_db, register_source, update_conversation_stats

logger = logging.getLogger("ingest_facebook")

DEFAULT_SRC = os.path.expanduser("~/Downloads/your_facebook_activity/messages/inbox")


def fix_encoding(s):
    """Facebook exports use mojibake (UTF-8 bytes interpreted as Latin-1). Fix it."""
    if not s:
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return s


def ingest(src_path=None, db_path=None):
    src = src_path or DEFAULT_SRC
    if not os.path.isdir(src):
        print(f"ERROR: {src} not found")
        sys.exit(1)

    conn = get_db(db_path)
    create_db(db_path)
    conn = get_db(db_path)

    source_id = register_source(conn, "facebook", src)

    # Clear previous
    existing = conn.execute("SELECT id FROM conversations WHERE source_id=?", (source_id,)).fetchall()
    if existing:
        ids = [r[0] for r in existing]
        ph = ",".join("?" * len(ids))
        conn.execute(f"DELETE FROM messages WHERE conversation_id IN ({ph})", ids)
        conn.execute(f"DELETE FROM conversations WHERE id IN ({ph})", ids)
        conn.commit()

    thread_dirs = [d for d in os.listdir(src) if os.path.isdir(os.path.join(src, d))]
    print(f"Found {len(thread_dirs)} Facebook message threads.")

    total_convos = 0
    total_msgs = 0

    for thread_name in thread_dirs:
        thread_path = os.path.join(src, thread_name)

        # Collect all message JSON files (message_1.json, message_2.json, etc.)
        all_messages = []
        participants = []
        title = thread_name

        msg_files = sorted([f for f in os.listdir(thread_path) if f.startswith("message_") and f.endswith(".json")])
        for mf in msg_files:
            try:
                with open(os.path.join(thread_path, mf), "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read {thread_path}/{mf}: {e}")
                continue

            if not participants and "participants" in data:
                participants = [fix_encoding(p.get("name", "")) for p in data["participants"]]
                title = fix_encoding(data.get("title", thread_name))

            for msg in data.get("messages", []):
                all_messages.append(msg)

        if not all_messages:
            continue

        # Sort by timestamp (oldest first)
        all_messages.sort(key=lambda m: m.get("timestamp_ms", 0))

        # Determine date range
        first_ts = all_messages[0].get("timestamp_ms", 0) / 1000
        last_ts = all_messages[-1].get("timestamp_ms", 0) / 1000
        created = datetime.fromtimestamp(first_ts).isoformat() if first_ts else None
        updated = datetime.fromtimestamp(last_ts).isoformat() if last_ts else None

        # Build a title from participants if the title is just an ID
        if title == thread_name and participants:
            other = [p for p in participants if p and p != "Ted Hand"]
            if other:
                title = "FB: " + ", ".join(other[:3])

        cur = conn.execute(
            "INSERT INTO conversations (source_id, external_id, title, created_at, updated_at, folder_path) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (source_id, thread_name, title, created, updated, thread_path),
        )
        conv_id = cur.lastrowid

        for msg in all_messages:
            sender = fix_encoding(msg.get("sender_name", ""))
            content = fix_encoding(msg.get("content", ""))
            if not content:
                # Check for shares, photos, etc.
                if "share" in msg:
                    share = msg["share"]
                    content = f"[Shared: {share.get('link', '')}] {fix_encoding(share.get('share_text', ''))}"
                elif "photos" in msg:
                    content = "[Photo]"
                elif "sticker" in msg:
                    content = "[Sticker]"
                elif "audio_files" in msg:
                    content = "[Audio]"
                elif "videos" in msg:
                    content = "[Video]"
                else:
                    continue

            ts = msg.get("timestamp_ms", 0) / 1000
            msg_time = datetime.fromtimestamp(ts).isoformat() if ts else None

            # Role: 'user' if Ted, 'sender' otherwise
            role = "user" if "Ted" in sender else "sender"

            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, created_at, char_count) "
                "VALUES (?, ?, ?, ?, ?)",
                (conv_id, role, content, msg_time, len(content)),
            )
            total_msgs += 1

        update_conversation_stats(conn, conv_id)
        total_convos += 1

        if total_convos % 500 == 0:
            conn.commit()

    conn.commit()
    conn.close()
    print(f"Ingested {total_convos} conversations, {total_msgs} messages from Facebook Messenger.")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else None
    ingest(src_path=src)
