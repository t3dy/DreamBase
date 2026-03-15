"""
Ingest Claude conversations from Dev/Claude Data/claude_data.db into the megabase.
"""

import os
import sys
import sqlite3
import logging

from schema import get_db, create_db, register_source, update_conversation_stats

logger = logging.getLogger("ingest_claude")

DEFAULT_SRC = os.path.expanduser("~/../../Dev/Claude Data/claude_data.db")


def ingest(src_path=None, db_path=None):
    src = src_path or DEFAULT_SRC
    # Normalize path
    src = os.path.normpath(src)
    if not os.path.exists(src):
        # Try alternate path
        src = "C:/Dev/Claude Data/claude_data.db"
    if not os.path.exists(src):
        print(f"ERROR: {src} not found")
        sys.exit(1)

    print(f"Reading from {src}...")
    src_conn = sqlite3.connect(src)
    src_conn.row_factory = sqlite3.Row

    conn = get_db(db_path)
    create_db(db_path)
    conn = get_db(db_path)

    source_id = register_source(conn, "claude", src)

    # Clear previous
    existing = conn.execute("SELECT id FROM conversations WHERE source_id=?", (source_id,)).fetchall()
    if existing:
        ids = [r[0] for r in existing]
        ph = ",".join("?" * len(ids))
        conn.execute(f"DELETE FROM messages WHERE conversation_id IN ({ph})", ids)
        conn.execute(f"DELETE FROM conversations WHERE id IN ({ph})", ids)
        conn.commit()

    # Read conversations
    convos = src_conn.execute("SELECT uuid, name, summary, created_at, updated_at FROM conversations").fetchall()
    print(f"Found {len(convos)} Claude conversations.")

    total_msgs = 0
    for conv in convos:
        cur = conn.execute(
            "INSERT INTO conversations (source_id, external_id, title, summary, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (source_id, conv["uuid"], conv["name"], conv["summary"], conv["created_at"], conv["updated_at"]),
        )
        conv_id = cur.lastrowid

        msgs = src_conn.execute(
            "SELECT uuid, sender, text, created_at FROM messages WHERE conversation_uuid=? ORDER BY created_at",
            (conv["uuid"],),
        ).fetchall()

        for msg in msgs:
            role = "assistant" if msg["sender"] == "assistant" else "user"
            text = msg["text"] or ""
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, created_at, char_count) "
                "VALUES (?, ?, ?, ?, ?)",
                (conv_id, role, text, msg["created_at"], len(text)),
            )
            total_msgs += 1

        update_conversation_stats(conn, conv_id)

    conn.commit()
    src_conn.close()
    conn.close()
    print(f"Ingested {len(convos)} conversations, {total_msgs} messages from Claude.")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else None
    ingest(src_path=src)
