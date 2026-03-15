"""
Import key data from existing SMS and Twitter SQLite databases into the megabase.
These DBs already have rich schemas — we import conversations and messages into
the unified format while preserving source DB paths for deep queries.
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime

from schema import get_db, create_db, register_source, update_conversation_stats

logger = logging.getLogger("ingest_sms_twitter")

SMS_DB = "C:/Users/PC/Desktop/backup sms/db/sms.db"
TWITTER_DB = "C:/Users/PC/Downloads/twitter-2026-02-09-archive/output/twitter_archive.db"


def ingest_sms(db_path=None):
    """Import SMS messages grouped by contact as conversations."""
    if not os.path.exists(SMS_DB):
        print(f"SMS DB not found: {SMS_DB}")
        return

    print(f"Reading SMS from {SMS_DB}...")
    src_conn = sqlite3.connect(SMS_DB)
    src_conn.row_factory = sqlite3.Row

    conn = get_db(db_path)
    create_db(db_path)
    conn = get_db(db_path)

    source_id = register_source(conn, "sms", SMS_DB)

    # Clear previous
    existing = conn.execute("SELECT id FROM conversations WHERE source_id=?", (source_id,)).fetchall()
    if existing:
        ids = [r[0] for r in existing]
        ph = ",".join("?" * len(ids))
        conn.execute(f"DELETE FROM messages WHERE conversation_id IN ({ph})", ids)
        conn.execute(f"DELETE FROM conversations WHERE id IN ({ph})", ids)
        conn.commit()

    # Group messages by contact
    contacts = src_conn.execute(
        "SELECT DISTINCT contact_name, address FROM messages WHERE contact_name IS NOT NULL AND contact_name != '' "
        "ORDER BY contact_name"
    ).fetchall()

    total_msgs = 0
    total_convos = 0

    for contact in contacts:
        name = contact["contact_name"]
        address = contact["address"]

        msgs = src_conn.execute(
            "SELECT body, date_ms, direction, readable_date FROM messages "
            "WHERE contact_name=? AND body IS NOT NULL AND body != '' ORDER BY date_ms",
            (name,),
        ).fetchall()

        if not msgs:
            continue

        first_date = datetime.fromtimestamp(msgs[0]["date_ms"] / 1000).isoformat() if msgs[0]["date_ms"] else None
        last_date = datetime.fromtimestamp(msgs[-1]["date_ms"] / 1000).isoformat() if msgs[-1]["date_ms"] else None

        ext_id = f"{name}_{address}" if address else name
        cur = conn.execute(
            "INSERT INTO conversations (source_id, external_id, title, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (source_id, ext_id, f"SMS: {name}", first_date, last_date),
        )
        conv_id = cur.lastrowid

        for msg in msgs:
            role = "user" if msg["direction"] == 2 else "sender"
            body = msg["body"]
            ts = datetime.fromtimestamp(msg["date_ms"] / 1000).isoformat() if msg["date_ms"] else None

            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, created_at, char_count) "
                "VALUES (?, ?, ?, ?, ?)",
                (conv_id, role, body, ts, len(body)),
            )
            total_msgs += 1

        update_conversation_stats(conn, conv_id)
        total_convos += 1

    conn.commit()
    src_conn.close()
    conn.close()
    print(f"Ingested {total_convos} SMS conversations, {total_msgs} messages.")


def ingest_twitter(db_path=None):
    """Import tweets as a single conversation (the Twitter timeline)."""
    if not os.path.exists(TWITTER_DB):
        print(f"Twitter DB not found: {TWITTER_DB}")
        return

    print(f"Reading Twitter from {TWITTER_DB}...")
    src_conn = sqlite3.connect(TWITTER_DB)
    src_conn.row_factory = sqlite3.Row

    conn = get_db(db_path)
    create_db(db_path)
    conn = get_db(db_path)

    source_id = register_source(conn, "twitter", TWITTER_DB)

    # Clear previous
    existing = conn.execute("SELECT id FROM conversations WHERE source_id=?", (source_id,)).fetchall()
    if existing:
        ids = [r[0] for r in existing]
        ph = ",".join("?" * len(ids))
        conn.execute(f"DELETE FROM messages WHERE conversation_id IN ({ph})", ids)
        conn.execute(f"DELETE FROM conversations WHERE id IN ({ph})", ids)
        conn.commit()

    # Import tweets as one big conversation
    tweets = src_conn.execute(
        "SELECT id, full_text, created_at FROM tweets ORDER BY created_at"
    ).fetchall()

    if not tweets:
        print("No tweets found.")
        return

    cur = conn.execute(
        "INSERT INTO conversations (source_id, external_id, title, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (source_id, "timeline", "Twitter Timeline", tweets[0]["created_at"], tweets[-1]["created_at"]),
    )
    conv_id = cur.lastrowid

    for tweet in tweets:
        conn.execute(
            "INSERT INTO messages (conversation_id, role, content, created_at, char_count) "
            "VALUES (?, ?, ?, ?, ?)",
            (conv_id, "user", tweet["full_text"], tweet["created_at"], len(tweet["full_text"])),
        )

    update_conversation_stats(conn, conv_id)

    # Also import DMs if they exist
    try:
        dms = src_conn.execute("SELECT * FROM dms ORDER BY rowid").fetchall()
        if dms:
            # Get column names
            cols = [desc[0] for desc in src_conn.execute("SELECT * FROM dms LIMIT 1").description]
            print(f"Found {len(dms)} DMs (schema: {cols[:5]})")
    except Exception:
        pass

    conn.commit()
    src_conn.close()
    conn.close()
    print(f"Ingested 1 Twitter timeline conversation, {len(tweets)} tweets.")


if __name__ == "__main__":
    ingest_sms()
    ingest_twitter()
