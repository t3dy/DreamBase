"""
Ingest ChatGPT conversations.json into the megabase.
Adapts tree-walking logic from Desktop/GPT Data/build_chats.py.
"""

import json
import os
import sys
import logging
from datetime import datetime

from schema import get_db, create_db, register_source, update_conversation_stats, DB_PATH

logger = logging.getLogger("ingest_chatgpt")

# Default path to conversations.json
DEFAULT_SRC = os.path.expanduser("~/Desktop/GPT Data/conversations.json")


def walk_messages(conv):
    """Traverse the mapping tree from current_node back to root, yielding (role, text, create_time) in order."""
    mapping = conv.get("mapping", {})
    current = conv.get("current_node")
    if not current or current not in mapping:
        return []

    # Build path from current_node back to root
    chain = []
    node_id = current
    while node_id and node_id in mapping:
        chain.append(node_id)
        node_id = mapping[node_id].get("parent")
    chain.reverse()

    msgs = []
    for nid in chain:
        node = mapping[nid]
        msg = node.get("message")
        if not msg:
            continue
        author = msg.get("author", {}).get("role", "unknown")
        content = msg.get("content", {})
        ctype = content.get("content_type", "")

        if ctype not in ("text", "code", ""):
            continue

        parts = content.get("parts", [])
        text_parts = []
        for p in parts:
            if isinstance(p, str) and p.strip():
                text_parts.append(p)

        if not text_parts:
            continue

        text = "\n\n".join(text_parts)
        create_time = msg.get("create_time")
        msgs.append((author, text, create_time))
    return msgs


def ts_to_iso(ts):
    """Convert Unix timestamp to ISO 8601 string."""
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(ts).isoformat()
    except (ValueError, OSError, TypeError):
        return None


def ingest(src_path=None, db_path=None):
    src = src_path or DEFAULT_SRC
    if not os.path.exists(src):
        print(f"ERROR: {src} not found")
        sys.exit(1)

    print(f"Loading {src}...")
    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Found {len(data)} conversations.")

    conn = get_db(db_path)
    # Ensure tables exist
    create_db(db_path)
    conn = get_db(db_path)

    source_id = register_source(conn, "chatgpt", src)

    # Clear previous chatgpt data for clean re-ingestion
    existing = conn.execute(
        "SELECT id FROM conversations WHERE source_id=?", (source_id,)
    ).fetchall()
    if existing:
        ids = [r[0] for r in existing]
        placeholders = ",".join("?" * len(ids))
        conn.execute(f"DELETE FROM messages WHERE conversation_id IN ({placeholders})", ids)
        conn.execute(f"DELETE FROM conversations WHERE id IN ({placeholders})", ids)
        conn.commit()
        print(f"Cleared {len(ids)} previous chatgpt conversations.")

    total_msgs = 0
    total_convos = 0
    batch_size = 100

    for i, conv in enumerate(data):
        title = conv.get("title") or "Untitled"
        created = ts_to_iso(conv.get("create_time"))
        updated = ts_to_iso(conv.get("update_time"))
        # Use index as external_id since conversations.json has no stable ID field
        # Actually, the mapping keys or the first node could work, but index is simplest
        ext_id = str(i)

        msgs = walk_messages(conv)

        # Insert conversation
        cur = conn.execute(
            "INSERT INTO conversations (source_id, external_id, title, created_at, updated_at, folder_path) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (source_id, ext_id, title, created, updated, src),
        )
        conv_id = cur.lastrowid

        # Insert messages
        for role, text, msg_time in msgs:
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, created_at, char_count) "
                "VALUES (?, ?, ?, ?, ?)",
                (conv_id, role, text, ts_to_iso(msg_time), len(text)),
            )
            total_msgs += 1

        update_conversation_stats(conn, conv_id)
        total_convos += 1

        if (i + 1) % batch_size == 0:
            conn.commit()

    conn.commit()
    conn.close()

    print(f"Ingested {total_convos} conversations, {total_msgs} messages from ChatGPT.")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else None
    ingest(src_path=src)
