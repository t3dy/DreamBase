"""
Megabase Schema — Personal Knowledge Archaeology System
Creates and manages the unified SQLite database.
"""

import sqlite3
import os
import logging
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "megabase.db")

logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "ingest_errors.log"),
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    file_path TEXT,
    ingested_at TEXT
);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    external_id TEXT,
    title TEXT,
    summary TEXT,
    created_at TEXT,
    updated_at TEXT,
    message_count INTEGER DEFAULT 0,
    char_count INTEGER DEFAULT 0,
    estimated_pages REAL DEFAULT 0.0,
    folder_path TEXT,
    UNIQUE(source_id, external_id)
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    role TEXT,
    content TEXT,
    created_at TEXT,
    char_count INTEGER DEFAULT 0,
    sentiment_vader REAL,
    sentiment_label TEXT
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS conversation_tags (
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    tag_id INTEGER NOT NULL REFERENCES tags(id),
    confidence REAL DEFAULT 0.7,
    method TEXT DEFAULT 'keyword',
    PRIMARY KEY (conversation_id, tag_id)
);

CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    name TEXT,
    category TEXT,
    description TEXT,
    maturity TEXT,
    method TEXT DEFAULT 'keyword',
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY,
    message_id INTEGER REFERENCES messages(id),
    entity_text TEXT,
    entity_label TEXT,
    start_char INTEGER,
    end_char INTEGER
);

CREATE TABLE IF NOT EXISTS chunk_exports (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    chunk_number INTEGER,
    file_path TEXT,
    char_count INTEGER,
    exported_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_conversations_source ON conversations(source_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);
CREATE INDEX IF NOT EXISTS idx_entities_message ON entities(message_id);
CREATE INDEX IF NOT EXISTS idx_entities_label ON entities(entity_label);
"""


def get_db(db_path=None):
    """Get a connection to the megabase database."""
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def create_db(db_path=None):
    """Create the database and all tables."""
    conn = get_db(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    print(f"Database created at {db_path or DB_PATH}")
    return conn


def register_source(conn, name, file_path=None):
    """Register or update a data source. Returns source_id."""
    now = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT INTO sources (name, file_path, ingested_at) VALUES (?, ?, ?) "
        "ON CONFLICT(name) DO UPDATE SET file_path=excluded.file_path, ingested_at=excluded.ingested_at",
        (name, file_path, now),
    )
    conn.commit()
    row = conn.execute("SELECT id FROM sources WHERE name=?", (name,)).fetchone()
    return row[0]


def update_conversation_stats(conn, conversation_id):
    """Recompute message_count, char_count, estimated_pages for a conversation."""
    row = conn.execute(
        "SELECT COUNT(*), COALESCE(SUM(char_count), 0) FROM messages WHERE conversation_id=?",
        (conversation_id,),
    ).fetchone()
    msg_count, total_chars = row
    conn.execute(
        "UPDATE conversations SET message_count=?, char_count=?, estimated_pages=? WHERE id=?",
        (msg_count, total_chars, total_chars / 3000.0, conversation_id),
    )


if __name__ == "__main__":
    create_db()
