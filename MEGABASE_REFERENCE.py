#!/usr/bin/env python3
"""
===============================================================================
MEGABASE — Personal Knowledge Archaeology System
Complete Annotated Reference (all scripts in one document)
===============================================================================

PROJECT OVERVIEW
================
Megabase unifies ~2 years of LLM conversations, social media, texts, emails,
and chat exports from 10+ locations into one searchable SQLite database.

ARCHITECTURE
============
Six agent roles, each a standalone Python script:

  1. ARCHITECT  (schema.py)         — Creates the unified DB schema
  2. INGESTORS  (ingest_*.py × 9)   — Parse each source into megabase.db
  3. INDEXER    (index.py)           — FTS5, VADER sentiment, keyword tagging
  4. SUMMARIZER (summarize.py)       — Deterministic excerpts + ChatGPT batch workflow
  5. CHUNKER   (chunk.py)            — Export conversations as GPT-ready .md chunks
  6. BROWSER   (app.py)              — Flask card-based browsing UI

PIPELINE
========
  schema.py → ingest_*.py (parallel) → index.py + summarize.py → chunk.py / app.py

DATA FLOW
=========
  Raw files (JSON/HTML/PDF/SQLite/mbox)
    → ingest_*.py (parse + normalize)
      → megabase.db (unified schema)
        → index.py (FTS5 + VADER + keyword tags)
          → summarize.py (auto excerpts + batch files for ChatGPT)
            → chunk.py (deep reading exports)
            → app.py (web browser UI)

DATABASE
========
  Location: megabase/megabase.db
  As of last run: 4,308 conversations, 3,949,674 messages, 1.3 GB
  Tables: sources, conversations, messages, tags, conversation_tags, ideas,
          entities, chunk_exports, messages_fts (FTS5 virtual table)

SOURCES INGESTED
================
  chatgpt       —  857 convos,   28,086 msgs  (conversations.json tree-walk)
  llm_logs_html —  982 convos,   27,190 msgs  (HTML files, two parser variants)
  llm_logs_pdf  —  653 convos,      842 msgs  (PyMuPDF text extraction)
  claude        —  212 convos,    1,326 msgs  (existing SQLite DB)
  facebook      —  767 convos,  112,066 msgs  (Messenger JSON export)
  google_chat   —    8 convos,    2,067 msgs  (Takeout JSON)
  pkd_chats     —   12 convos,      395 msgs  (PKD-themed HTML chats)
  sms           —  816 convos, 3,606,366 msgs  (SMS SQLite DB, grouped by contact)
  twitter       —    1 conv,    171,336 msgs  (full tweet timeline)
  gmail         —  (written but not run — user may have processed elsewhere)

ENRICHMENT RESULTS
==================
  FTS5 index:    3,949,674 messages indexed for full-text search
  VADER scored:  all messages with >10 chars
  Tagged:        1,825 conversations across 9 categories
  Ideas:         397 extracted (284 game, 40 app, 10 educational, 63 other)
  Summarized:    2,651 conversations (auto-excerpt from first assistant response)
  Batch files:   24 generated for ChatGPT deep summarization

===============================================================================
"""


# =============================================================================
# SCRIPT 1: schema.py — The Architect
# =============================================================================
# PURPOSE: Creates and manages the unified SQLite database. This is the
#          foundation that all other scripts depend on. Run this FIRST.
#
# USAGE:   python schema.py
#          (creates megabase.db with all tables and indexes)
#
# KEY DESIGN DECISIONS:
#   - WAL journal mode for concurrent read/write (ingestors can run in parallel)
#   - Foreign keys ON for referential integrity
#   - UNIQUE(source_id, external_id) prevents duplicate conversations per source
#   - estimated_pages = char_count / 3000 (rough approximation for "page length")
#   - All timestamps stored as ISO 8601 TEXT (SQLite has no native datetime type)
#   - Errors log to ingest_errors.log (not stdout) to save terminal tokens
#
# TABLES:
#   sources           — Registry of where data came from (chatgpt, claude, sms, etc.)
#   conversations     — One per chat thread / email thread / SMS thread
#   messages          — Individual turns / emails / texts
#   tags              — Category labels (game_idea, alchemy, pkd, etc.)
#   conversation_tags — Many-to-many: conversations ↔ tags with confidence + method
#   ideas             — Extracted game/app/edu concepts with maturity levels
#   entities          — spaCy NER entities (reserved for future use)
#   chunk_exports     — Record of which conversations have been chunked for deep reading
#   messages_fts      — FTS5 virtual table for full-text search (built by index.py)
# =============================================================================

SCHEMA_PY = """
import sqlite3
import os
import logging
from datetime import datetime

# Database lives in the same directory as this script
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "megabase.db")

# All errors go to a log file, not stdout — this saves tokens when running scripts
logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "ingest_errors.log"),
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

# ── SQL schema definition ────────────────────────────────────────────────────
# This multi-statement string creates all tables with IF NOT EXISTS guards
# so it's safe to run multiple times (idempotent).

SCHEMA_SQL = '''
-- Sources: registry of data origins
-- Each ingestor registers itself here before writing data
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,      -- e.g. 'chatgpt', 'sms', 'facebook'
    file_path TEXT,                 -- original location on disk
    ingested_at TEXT                -- ISO timestamp of last ingestion
);

-- Conversations: the core unit of organization
-- One row per chat thread, email thread, or SMS contact
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    external_id TEXT,              -- original ID from the source system
    title TEXT,                    -- conversation title or contact name
    summary TEXT,                  -- 3-sentence summary (filled by summarize.py)
    created_at TEXT,               -- ISO timestamp
    updated_at TEXT,               -- ISO timestamp of last message
    message_count INTEGER DEFAULT 0,    -- computed by update_conversation_stats()
    char_count INTEGER DEFAULT 0,       -- total characters across all messages
    estimated_pages REAL DEFAULT 0.0,   -- char_count / 3000
    folder_path TEXT,              -- original file/folder location on disk
    UNIQUE(source_id, external_id)      -- prevents duplicate imports per source
);

-- Messages: individual turns / emails / texts
-- The role field normalizes across all sources:
--   'user'      = Ted's messages (outgoing SMS, user turns in LLM chats)
--   'assistant' = LLM responses (ChatGPT, Claude)
--   'sender'    = Other people's messages (incoming SMS, Facebook, email)
--   'system'    = System prompts or tool outputs
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    role TEXT,                     -- 'user', 'assistant', 'sender', 'system'
    content TEXT,                  -- the actual message text
    created_at TEXT,               -- ISO timestamp
    char_count INTEGER DEFAULT 0,  -- length of content
    sentiment_vader REAL,          -- VADER compound score (-1 to +1)
    sentiment_label TEXT           -- 'positive', 'negative', 'neutral'
);

-- Tags: multi-label classification system
-- 9 categories: game_idea, app_project, educational, alchemy, pkd, mtg, esoteric, coding, personal
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- Many-to-many join table for conversation ↔ tag relationships
-- Tracks HOW the tag was assigned (keyword match vs LLM vs manual)
CREATE TABLE IF NOT EXISTS conversation_tags (
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    tag_id INTEGER NOT NULL REFERENCES tags(id),
    confidence REAL DEFAULT 0.7,   -- 0.7 for keyword, 0.9 for LLM-assigned
    method TEXT DEFAULT 'keyword', -- 'keyword', 'llm', 'folder_name', 'manual'
    PRIMARY KEY (conversation_id, tag_id)
);

-- Ideas: extracted game/app/edu concepts
-- Populated by index.py (keyword detection) and summarize.py (LLM batch import)
CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    name TEXT,                     -- short name for the idea
    category TEXT,                 -- 'game', 'app', 'educational', 'product', 'other'
    description TEXT,              -- 1-3 sentence description
    maturity TEXT,                 -- 'sketch', 'design', 'prototype', 'built'
    method TEXT DEFAULT 'keyword', -- how it was detected
    created_at TEXT
);

-- NER entities (reserved for future spaCy enrichment)
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY,
    message_id INTEGER REFERENCES messages(id),
    entity_text TEXT,
    entity_label TEXT,             -- 'PERSON', 'ORG', 'WORK_OF_ART', etc.
    start_char INTEGER,
    end_char INTEGER
);

-- Chunk exports: tracks which conversations have been exported for deep reading
CREATE TABLE IF NOT EXISTS chunk_exports (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    chunk_number INTEGER,
    file_path TEXT,
    char_count INTEGER,
    exported_at TEXT
);

-- Performance indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_conversations_source ON conversations(source_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);
CREATE INDEX IF NOT EXISTS idx_entities_message ON entities(message_id);
CREATE INDEX IF NOT EXISTS idx_entities_label ON entities(entity_label);
'''


def get_db(db_path=None):
    '''Get a connection to the megabase database.
    WAL mode allows concurrent readers (Flask) alongside writers (ingestors).
    Foreign keys are enforced to catch orphan records.'''
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def create_db(db_path=None):
    '''Create the database and all tables. Safe to call multiple times
    because all CREATE statements use IF NOT EXISTS.'''
    conn = get_db(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    print(f"Database created at {db_path or DB_PATH}")
    return conn


def register_source(conn, name, file_path=None):
    '''Register or update a data source. Uses UPSERT to update the
    ingested_at timestamp on re-ingestion. Returns the source_id.'''
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
    '''Recompute derived fields for a conversation.
    Called after inserting all messages for a conversation.
    estimated_pages uses ~3000 chars/page as a rough heuristic.'''
    row = conn.execute(
        "SELECT COUNT(*), COALESCE(SUM(char_count), 0) FROM messages WHERE conversation_id=?",
        (conversation_id,),
    ).fetchone()
    msg_count, total_chars = row
    conn.execute(
        "UPDATE conversations SET message_count=?, char_count=?, estimated_pages=? WHERE id=?",
        (msg_count, total_chars, total_chars / 3000.0, conversation_id),
    )
"""


# =============================================================================
# SCRIPT 2: ingest_chatgpt_json.py — ChatGPT Conversations
# =============================================================================
# PURPOSE: Parse OpenAI's conversations.json export into megabase.
#
# USAGE:   python ingest_chatgpt_json.py [/path/to/conversations.json]
#          Default: ~/Desktop/GPT Data/conversations.json
#
# INPUT FORMAT: OpenAI exports conversations as a JSON array. Each conversation
#   has a "mapping" object — a tree of message nodes linked by parent pointers.
#   The "current_node" field points to the leaf (most recent message).
#
# TREE-WALKING ALGORITHM:
#   1. Start at current_node
#   2. Follow parent pointers back to root
#   3. Reverse the chain to get chronological order
#   4. Extract (role, text, timestamp) from each node's message object
#   5. Filter to text/code content types (skip images, audio, etc.)
#
# INGESTION PATTERN (shared by all ingestors):
#   1. register_source() → get source_id
#   2. Delete all previous data for this source (clean re-ingestion)
#   3. Insert conversations + messages
#   4. update_conversation_stats() for each conversation
#   5. Batch commit every N conversations for performance
#
# RESULT: 857 conversations, 28,086 messages
# =============================================================================

INGEST_CHATGPT_JSON_PY = """
import json, os, sys, logging
from datetime import datetime
from schema import get_db, create_db, register_source, update_conversation_stats, DB_PATH

logger = logging.getLogger("ingest_chatgpt")
DEFAULT_SRC = os.path.expanduser("~/Desktop/GPT Data/conversations.json")


def walk_messages(conv):
    '''Traverse OpenAI's message tree from current_node to root.

    OpenAI's conversations.json uses a tree structure where each message
    has a parent pointer. When the user edits a message, it creates a branch.
    The "current_node" points to the active branch tip.

    Algorithm:
      1. Start at current_node
      2. Follow parent pointers to root, building a chain
      3. Reverse to get chronological order
      4. Extract role + text from each node's message object
      5. Skip non-text content (images, audio, multimodal)

    Returns: list of (role, text, create_time) tuples
    '''
    mapping = conv.get("mapping", {})
    current = conv.get("current_node")
    if not current or current not in mapping:
        return []

    # Build path from leaf to root
    chain = []
    node_id = current
    while node_id and node_id in mapping:
        chain.append(node_id)
        node_id = mapping[node_id].get("parent")
    chain.reverse()  # Now root → leaf order

    msgs = []
    for nid in chain:
        node = mapping[nid]
        msg = node.get("message")
        if not msg:
            continue
        author = msg.get("author", {}).get("role", "unknown")
        content = msg.get("content", {})
        ctype = content.get("content_type", "")

        # Only keep text and code content — skip images, audio, tool calls
        if ctype not in ("text", "code", ""):
            continue

        # Parts is a list that may contain strings or dicts (for multimodal)
        parts = content.get("parts", [])
        text_parts = [p for p in parts if isinstance(p, str) and p.strip()]

        if not text_parts:
            continue

        text = "\\n\\n".join(text_parts)
        create_time = msg.get("create_time")  # Unix timestamp
        msgs.append((author, text, create_time))
    return msgs


def ts_to_iso(ts):
    '''Convert Unix timestamp (float) to ISO 8601 string.
    Returns None for invalid/missing timestamps.'''
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(ts).isoformat()
    except (ValueError, OSError, TypeError):
        return None


def ingest(src_path=None, db_path=None):
    '''Main ingestion function. Loads the full JSON, walks each conversation
    tree, and inserts normalized data into megabase.'''
    src = src_path or DEFAULT_SRC
    if not os.path.exists(src):
        print(f"ERROR: {src} not found"); sys.exit(1)

    print(f"Loading {src}...")
    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)  # ~200MB in memory for 857 conversations
    print(f"Found {len(data)} conversations.")

    conn = get_db(db_path)
    create_db(db_path)
    conn = get_db(db_path)
    source_id = register_source(conn, "chatgpt", src)

    # CLEAN RE-INGESTION: Delete all previous chatgpt data before re-importing
    # This ensures idempotent runs without duplicates
    existing = conn.execute("SELECT id FROM conversations WHERE source_id=?", (source_id,)).fetchall()
    if existing:
        ids = [r[0] for r in existing]
        ph = ",".join("?" * len(ids))
        conn.execute(f"DELETE FROM messages WHERE conversation_id IN ({ph})", ids)
        conn.execute(f"DELETE FROM conversations WHERE id IN ({ph})", ids)
        conn.commit()

    total_msgs = 0
    total_convos = 0
    for i, conv in enumerate(data):
        title = conv.get("title") or "Untitled"
        created = ts_to_iso(conv.get("create_time"))
        updated = ts_to_iso(conv.get("update_time"))
        ext_id = str(i)  # Use array index as stable external ID

        msgs = walk_messages(conv)

        cur = conn.execute(
            "INSERT INTO conversations (source_id, external_id, title, created_at, updated_at, folder_path) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (source_id, ext_id, title, created, updated, src),
        )
        conv_id = cur.lastrowid

        for role, text, msg_time in msgs:
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, created_at, char_count) "
                "VALUES (?, ?, ?, ?, ?)",
                (conv_id, role, text, ts_to_iso(msg_time), len(text)),
            )
            total_msgs += 1

        update_conversation_stats(conn, conv_id)
        total_convos += 1

        if (i + 1) % 100 == 0:
            conn.commit()  # Batch commits for performance

    conn.commit()
    conn.close()
    print(f"Ingested {total_convos} conversations, {total_msgs} messages from ChatGPT.")
"""


# =============================================================================
# SCRIPT 3: ingest_html_chats.py — LLM Chat HTML Files
# =============================================================================
# PURPOSE: Parse HTML chat exports from ~/Downloads/LLM logs/
#
# USAGE:   python ingest_html_chats.py [/path/to/llm/logs/]
#
# HTML FORMAT VARIANTS:
#   OLD FORMAT: <div class="msg user"><div class="role">You</div>message text</div>
#   NEW FORMAT: <div class="msg assistant"><div class="bubble">message text</div></div>
#   Both use class="msg" on the outer div with role as a CSS class.
#
# PARSER DESIGN:
#   Uses Python stdlib html.parser.HTMLParser (no BeautifulSoup dependency).
#   State machine tracks: _in_msg, _in_role_div, _in_bubble, _current_role.
#   The _is_chat flag filters out non-chat HTML (game artifacts, dashboards).
#   Only files containing at least one .msg element are treated as chats.
#
# DATE EXTRACTION:
#   1. First tries meta div text: "Created: January 09, 2025 09:24 PM"
#   2. Falls back to directory names: "2025-01-09_Title/"
#
# RESULT: 982 conversations, 27,190 messages (68 non-chat HTML files skipped)
# =============================================================================

INGEST_HTML_CHATS_PY = """
import os, sys, re, logging
from datetime import datetime
from html.parser import HTMLParser
from schema import get_db, create_db, register_source, update_conversation_stats

logger = logging.getLogger("ingest_html")
DEFAULT_SRC = os.path.expanduser("~/Downloads/LLM logs")
KNOWN_ROLES = {"user", "assistant", "system", "tool"}


class ChatHTMLParser(HTMLParser):
    '''Lightweight state-machine parser for chat HTML files.

    Handles two HTML variants from LLM chat exports:
      OLD: .msg divs with .role child divs (label like "You" / "ChatGPT")
      NEW: .msg divs with .bubble child divs (content in bubble)

    State tracking:
      _in_msg        — currently inside a <div class="msg ...">
      _in_role_div   — inside a .role div (skip this text — it's just a label)
      _in_bubble     — inside a .bubble div
      _current_role  — extracted from CSS classes: "user", "assistant", etc.
      _is_chat       — True if we found at least one .msg element

    The _is_chat flag is critical: the LLM logs folder contains game artifacts,
    dashboards, and other HTML files that are NOT chat transcripts. We detect
    chats by the presence of .msg elements.
    '''

    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_text = ""
        self.messages = []       # list of (role, text) tuples
        self._in_title = False
        self._in_meta = False
        self._in_msg = False
        self._in_role_div = False
        self._in_bubble = False
        self._current_role = None
        self._current_text = []
        self._is_chat = False

    def handle_starttag(self, tag, attrs):
        classes = dict(attrs).get("class", "").split()

        if tag == "title":
            self._in_title = True
            return
        if tag == "div" and "meta" in classes:
            self._in_meta = True
            return
        if tag == "div" and "msg" in classes:
            # This is a chat message div — mark file as a chat
            self._is_chat = True
            role = next((c for c in classes if c in KNOWN_ROLES), None)
            self._in_msg = True
            self._current_role = role
            self._current_text = []
            return
        if tag == "div" and "role" in classes and self._in_msg:
            self._in_role_div = True  # Skip label text
            return
        if tag == "div" and "bubble" in classes and self._in_msg:
            self._in_bubble = True
            return

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "div" and self._in_meta:
            self._in_meta = False
        elif tag == "div" and self._in_role_div:
            self._in_role_div = False
        elif tag == "div" and self._in_bubble:
            self._in_bubble = False
        elif tag == "div" and self._in_msg:
            # End of message div — save accumulated text
            text = "".join(self._current_text).strip()
            if text and self._current_role:
                self.messages.append((self._current_role, text))
            self._in_msg = False
            self._current_role = None
            self._current_text = []

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif self._in_meta:
            self.meta_text += data
        elif self._in_role_div:
            return  # Skip "You" / "ChatGPT" labels
        elif self._in_msg:
            self._current_text.append(data)  # Accumulate message text


def parse_meta_date(meta_text):
    '''Extract date from meta div text.
    Handles formats like "Created: January 09, 2025 09:24 PM"
    and "January 09, 2025 09:24 PM · Model: gpt-4o"'''
    patterns = [
        r"(?:Created:\\s*)?(\w+ \\d{1,2}, \\d{4} \\d{1,2}:\\d{2} [AP]M)",
        r"(\\d{4}-\\d{2}-\\d{2})",
    ]
    for pat in patterns:
        m = re.search(pat, meta_text)
        if m:
            for fmt in ("%B %d, %Y %I:%M %p", "%Y-%m-%d"):
                try:
                    return datetime.strptime(m.group(1), fmt).isoformat()
                except ValueError:
                    continue
    return None


def extract_date_from_path(filepath):
    '''Fallback: extract date from directory names like "2025-01-09_Title".'''
    for part in filepath.replace("\\\\", "/").split("/"):
        m = re.match(r"(\\d{4}-\\d{2}-\\d{2})", part)
        if m:
            return m.group(1) + "T00:00:00"
    return None
"""


# =============================================================================
# SCRIPT 4: ingest_pdf_chats.py — LLM Chat PDFs
# =============================================================================
# PURPOSE: Extract text from PDF chat exports using PyMuPDF (fitz).
#
# USAGE:   python ingest_pdf_chats.py [/path/to/llm/logs/]
#
# CHALLENGES:
#   - PDFs don't preserve message boundaries reliably
#   - split_messages() tries "You said:" / "ChatGPT said:" markers
#   - Falls back to treating entire PDF as a single assistant message
#   - MIN_TEXT_LEN = 200 filters out empty/corrupt PDFs
#
# DEPENDENCY: pip install PyMuPDF (imported as "fitz")
#
# RESULT: 653 conversations, 842 messages
# =============================================================================

INGEST_PDF_CHATS_PY = """
import os, sys, re, logging
from datetime import datetime
import fitz  # PyMuPDF — pip install PyMuPDF
from schema import get_db, create_db, register_source, update_conversation_stats

logger = logging.getLogger("ingest_pdf")
DEFAULT_SRC = os.path.expanduser("~/Downloads/LLM logs")
MIN_TEXT_LEN = 200  # Skip PDFs shorter than this (likely empty/corrupt)


def extract_pdf_text(filepath):
    '''Extract all text from a PDF, page by page, using PyMuPDF.
    Concatenates pages with double newlines.'''
    try:
        doc = fitz.open(filepath)
        pages = [page.get_text() for page in doc if page.get_text().strip()]
        doc.close()
        return "\\n\\n".join(pages)
    except Exception as e:
        logger.warning(f"Failed to extract {filepath}: {e}")
        return ""


def split_messages(text):
    '''Attempt to split PDF text into user/assistant turns.

    Looks for ChatGPT PDF export patterns:
      "You said:" / "ChatGPT said:" / "User:" / "Assistant:"

    If no markers found, returns the entire text as a single assistant message.
    This is a best-effort heuristic — PDF exports vary wildly in format.
    '''
    patterns = [
        r'\\n(?:You|User)\\s*(?:said)?:\\s*\\n',
        r'\\n(?:ChatGPT|Assistant|GPT-4|Claude)\\s*(?:said)?:\\s*\\n',
    ]
    has_markers = any(re.search(pat, text) for pat in patterns)
    if not has_markers:
        return [("assistant", text)]  # Single blob

    parts = re.split(r'\\n((?:You|User|ChatGPT|Assistant|GPT-4|Claude)\\s*(?:said)?:)\\s*\\n', text)
    messages = []
    current_role = "user"
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lower = part.lower()
        if lower.startswith(("you", "user")):
            current_role = "user"
        elif lower.startswith(("chatgpt", "assistant", "gpt", "claude")):
            current_role = "assistant"
        else:
            messages.append((current_role, part))
    return messages if messages else [("assistant", text)]
"""


# =============================================================================
# SCRIPT 5: ingest_claude_db.py — Claude Conversations
# =============================================================================
# PURPOSE: Import Claude conversations from an existing SQLite database.
#
# USAGE:   python ingest_claude_db.py [/path/to/claude_data.db]
#          Default: C:/Dev/Claude Data/claude_data.db
#
# SOURCE SCHEMA (claude_data.db):
#   conversations: uuid, name, summary, created_at, updated_at
#   messages: uuid, conversation_uuid, sender, text, created_at
#
# MAPPING: sender='assistant' → role='assistant', everything else → role='user'
# The source DB already has summaries, which we preserve.
#
# RESULT: 212 conversations, 1,326 messages
# =============================================================================

INGEST_CLAUDE_DB_PY = """
import os, sys, sqlite3, logging
from schema import get_db, create_db, register_source, update_conversation_stats

logger = logging.getLogger("ingest_claude")
DEFAULT_SRC = "C:/Dev/Claude Data/claude_data.db"


def ingest(src_path=None, db_path=None):
    '''Read from existing Claude SQLite DB and map into megabase schema.
    Preserves existing summaries from the source database.'''
    src = os.path.normpath(src_path or DEFAULT_SRC)
    if not os.path.exists(src):
        src = "C:/Dev/Claude Data/claude_data.db"  # Fallback path
    if not os.path.exists(src):
        print(f"ERROR: {src} not found"); sys.exit(1)

    src_conn = sqlite3.connect(src)
    src_conn.row_factory = sqlite3.Row  # Access columns by name

    conn = get_db(db_path)
    create_db(db_path)
    conn = get_db(db_path)
    source_id = register_source(conn, "claude", src)

    # Clean re-ingestion pattern (same as all ingestors)
    existing = conn.execute("SELECT id FROM conversations WHERE source_id=?", (source_id,)).fetchall()
    if existing:
        ids = [r[0] for r in existing]
        ph = ",".join("?" * len(ids))
        conn.execute(f"DELETE FROM messages WHERE conversation_id IN ({ph})", ids)
        conn.execute(f"DELETE FROM conversations WHERE id IN ({ph})", ids)
        conn.commit()

    convos = src_conn.execute("SELECT uuid, name, summary, created_at, updated_at FROM conversations").fetchall()
    total_msgs = 0
    for conv in convos:
        cur = conn.execute(
            "INSERT INTO conversations (source_id, external_id, title, summary, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (source_id, conv["uuid"], conv["name"], conv["summary"], conv["created_at"], conv["updated_at"]),
        )
        conv_id = cur.lastrowid
        msgs = src_conn.execute(
            "SELECT sender, text, created_at FROM messages WHERE conversation_uuid=? ORDER BY created_at",
            (conv["uuid"],),
        ).fetchall()
        for msg in msgs:
            role = "assistant" if msg["sender"] == "assistant" else "user"
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, created_at, char_count) "
                "VALUES (?, ?, ?, ?, ?)",
                (conv_id, role, msg["text"] or "", msg["created_at"], len(msg["text"] or "")),
            )
            total_msgs += 1
        update_conversation_stats(conn, conv_id)
    conn.commit()
    print(f"Ingested {len(convos)} conversations, {total_msgs} messages from Claude.")
"""


# =============================================================================
# SCRIPT 6: ingest_facebook_json.py — Facebook Messenger
# =============================================================================
# PURPOSE: Parse Facebook Messenger JSON exports from Takeout.
#
# USAGE:   python ingest_facebook_json.py [/path/to/inbox/]
#          Default: ~/Downloads/your_facebook_activity/messages/inbox
#
# STRUCTURE: Each thread is a folder containing message_1.json, message_2.json, etc.
#
# ENCODING FIX: Facebook exports have a notorious mojibake bug — they encode
#   UTF-8 bytes as Latin-1 codepoints. fix_encoding() reverses this:
#   "Ren\u00c3\u00a9" → encode('latin-1') → b'\xc3\xa9' → decode('utf-8') → "René"
#
# MEDIA HANDLING: Photos, stickers, audio, videos stored as placeholder text.
#
# ROLE MAPPING: "Ted" in sender_name → role='user', otherwise → role='sender'
#
# RESULT: 767 conversations, 112,066 messages
# =============================================================================

INGEST_FACEBOOK_JSON_PY = """
import os, sys, json, logging
from datetime import datetime
from schema import get_db, create_db, register_source, update_conversation_stats

logger = logging.getLogger("ingest_facebook")
DEFAULT_SRC = os.path.expanduser("~/Downloads/your_facebook_activity/messages/inbox")


def fix_encoding(s):
    '''Fix Facebook's mojibake encoding.

    Facebook exports UTF-8 text but interprets each byte as a Latin-1 codepoint.
    Example: "René" becomes "Ren\\u00c3\\u00a9" in the JSON.
    Fix: encode as Latin-1 (gets the original bytes) → decode as UTF-8.

    Gracefully returns original string if the round-trip fails.
    '''
    if not s:
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return s


def ingest(src_path=None, db_path=None):
    '''Parse all Facebook Messenger threads.
    Each folder in inbox/ is a thread; message files are sorted and merged.'''
    src = src_path or DEFAULT_SRC
    # ... (follows standard ingest pattern: register source, clear previous, iterate)

    for thread_name in thread_dirs:
        # Collect ALL message_N.json files and merge into one sorted list
        # Facebook splits large threads across multiple files
        all_messages = []
        for mf in sorted(msg_files):
            data = json.load(...)
            all_messages.extend(data.get("messages", []))

        # Sort by timestamp (oldest first) — Facebook stores newest first
        all_messages.sort(key=lambda m: m.get("timestamp_ms", 0))

        # Build title from participants (excluding Ted)
        # Handle media: shares, photos, stickers, audio, videos → placeholder text
        for msg in all_messages:
            content = fix_encoding(msg.get("content", ""))
            if not content:
                # Check for media types and create placeholder
                if "share" in msg:
                    content = f"[Shared: {share.get('link', '')}]"
                elif "photos" in msg:
                    content = "[Photo]"
                # ... etc
"""


# =============================================================================
# SCRIPT 7: ingest_google_chat.py — Google Chat (Takeout)
# =============================================================================
# PURPOSE: Parse Google Chat messages from Google Takeout export.
#
# USAGE:   python ingest_google_chat.py [/path/to/Google Chat/]
#          Default: ~/Downloads/Takeout/Google Chat
#
# STRUCTURE: Google Chat/Groups/<DM name>/messages.json + group_info.json
#            Google Chat/Users/<user id>/messages.json
#
# DATE FORMAT: "Monday, July 22, 2013 at 6:35:25 PM UTC"
#   parse_gc_date() strips day name and "at", tries multiple strptime formats.
#
# TITLE: Built from group_info.json member names, excluding "Ted Hand".
#
# RESULT: 8 conversations, 2,067 messages
# =============================================================================

INGEST_GOOGLE_CHAT_PY = """
import os, sys, json, logging
from datetime import datetime
from schema import get_db, create_db, register_source, update_conversation_stats

DEFAULT_SRC = os.path.expanduser("~/Downloads/Takeout/Google Chat")


def parse_gc_date(date_str):
    '''Parse Google Chat's verbose date format.
    Input: "Monday, July 22, 2013 at 6:35:25 PM UTC"
    Steps: Remove "at ", strip day name, try multiple strptime formats.'''
    if not date_str:
        return None
    try:
        cleaned = date_str.replace(" at ", " ")
        parts = cleaned.split(", ", 1)
        if len(parts) > 1:
            cleaned = parts[1]  # Drop "Monday, "
        for fmt in ("%B %d, %Y %I:%M:%S %p %Z", "%B %d, %Y %I:%M:%S %p"):
            try:
                return datetime.strptime(cleaned, fmt).isoformat()
            except ValueError:
                continue
    except Exception:
        pass
    return None


def ingest(src_path=None, db_path=None):
    '''Process both Groups/ and Users/ directories.
    Each subdirectory with messages.json becomes a conversation.'''
    # For each thread: read group_info.json for member names → build title
    # Read messages.json → extract sender, text, date → insert messages
    # Role: "Ted" in sender → "user", otherwise → "sender"
"""


# =============================================================================
# SCRIPT 8: ingest_gmail_mbox.py — Gmail (mbox format)
# =============================================================================
# PURPOSE: Parse Gmail from .mbox file export. WRITTEN BUT NOT YET RUN.
#
# USAGE:   python ingest_gmail_mbox.py [path.mbox] [--headers-only]
#          Default: ~/Downloads/All mail Including Spam and Trash-002 (1).mbox (14 GB)
#
# DESIGN: Two-phase approach:
#   --headers-only  Phase 1: Fast pass, extract only From/To/Subject/Date
#   (default)       Phase 2: Extract bodies for personal contacts only
#
# FILTERING: Skip automated/marketing emails using:
#   SKIP_DOMAINS:  {"noreply", "notifications", "newsletter", "marketing", ...}
#   SKIP_SENDER_PATTERNS:  regex matching common bot sender patterns
#   is_personal()  checks both patterns and domain-local parts
#
# EMAIL BODY EXTRACTION:
#   get_body() walks MIME multipart tree, prefers text/plain over text/html.
#   HTML fallback strips tags with a crude regex.
#
# STATUS: Written, not run. User said to hold off — may have processed Gmail elsewhere.
# =============================================================================

INGEST_GMAIL_MBOX_PY = """
import os, sys, mailbox, email.utils, email.header, logging, re
from datetime import datetime
from schema import get_db, create_db, register_source, update_conversation_stats

DEFAULT_SRC = os.path.expanduser("~/Downloads/All mail Including Spam and Trash-002 (1).mbox")

# Automated/marketing sender patterns to skip
SKIP_DOMAINS = {
    "noreply", "no-reply", "notifications", "notify", "mailer", "updates",
    "newsletter", "marketing", "promo", "alerts", "donotreply", "automated",
    "support", "info", "billing", "accounts", "security",
}

SKIP_SENDER_PATTERNS = re.compile(
    r"(noreply|no-reply|notifications?|newsletter|marketing|promo|automated|"
    r"mailer-daemon|postmaster|bounce|unsubscribe)", re.IGNORECASE,
)


def is_personal(from_addr):
    '''Filter: True if email appears to be from a real person.
    Checks local part against SKIP_DOMAINS and SKIP_SENDER_PATTERNS.'''
    ...

def get_body(msg):
    '''Extract plain text from email.
    Walks multipart tree: prefer text/plain, fallback to text/html (strip tags).'''
    ...

def ingest(src_path=None, db_path=None, headers_only=False):
    '''Stream through 14GB mbox without loading entirely into memory.
    Uses Python stdlib mailbox.mbox() which reads lazily via iterkeys().'''
    ...
"""


# =============================================================================
# SCRIPT 9: ingest_pkd_chats.py — PKD Chat HTML Files
# =============================================================================
# PURPOSE: Parse PKD-themed chat HTML files from Desktop/pkd chats.
#
# USAGE:   python ingest_pkd_chats.py
#
# WHY STANDALONE: This was originally implemented by importing ChatHTMLParser
#   from ingest_html_chats.py, but that caused a CATASTROPHIC BUG: calling
#   ingest_html_chats.ingest() re-registered the 'llm_logs_html' source and
#   DELETED all 982 previously ingested HTML conversations.
#
#   Fix: Duplicate the parser as a standalone script with its own source name
#   ('pkd_chats'). Never import ingest functions from other ingestors.
#
# RESULT: 12 conversations, 395 messages
# =============================================================================

INGEST_PKD_CHATS_PY = """
# Standalone duplicate of ChatHTMLParser from ingest_html_chats.py
# Registers as source 'pkd_chats' (not 'llm_logs_html')
# NEVER import from other ingest_*.py scripts — each manages its own source
"""


# =============================================================================
# SCRIPT 10: ingest_sms_twitter.py — SMS Messages + Twitter Archive
# =============================================================================
# PURPOSE: Import from two existing SQLite databases (SMS + Twitter).
#
# USAGE:   python ingest_sms_twitter.py
#
# SMS (Desktop/backup sms/db/sms.db):
#   Groups messages by contact_name into conversations.
#   external_id = f"{name}_{address}" to handle contacts sharing phone numbers.
#   direction=2 → outgoing (role='user'), otherwise → incoming (role='sender').
#   Result: 816 conversations, 3,606,366 messages
#
# TWITTER (Downloads/twitter-2026-02-09-archive/output/twitter_archive.db):
#   All tweets imported as a single "Twitter Timeline" conversation.
#   Result: 1 conversation, 171,336 tweets
#   Note: 49,388 DMs detected but NOT yet imported.
#
# GOTCHA: The SMS DB has contacts with the same phone number but different names.
#   Originally used just address as external_id → UNIQUE constraint failed.
#   Fixed by combining name + address: f"{name}_{address}".
# =============================================================================

INGEST_SMS_TWITTER_PY = """
import os, sys, sqlite3, logging
from datetime import datetime
from schema import get_db, create_db, register_source, update_conversation_stats

SMS_DB = "C:/Users/PC/Desktop/backup sms/db/sms.db"
TWITTER_DB = "C:/Users/PC/Downloads/twitter-2026-02-09-archive/output/twitter_archive.db"


def ingest_sms(db_path=None):
    '''Import SMS messages grouped by contact.

    Source schema (sms.db):
      messages: body, date_ms, direction, readable_date, contact_name, address

    Grouping: DISTINCT (contact_name, address) → one conversation per contact.
    Direction: 2 = outgoing (user), anything else = incoming (sender).
    External ID: f"{name}_{address}" (not just address — contacts share numbers).
    '''
    ...

def ingest_twitter(db_path=None):
    '''Import all tweets as a single timeline conversation.

    Source schema (twitter_archive.db):
      tweets: id, full_text, created_at

    All tweets get role='user' (they're Ted's tweets).
    Also probes for DMs table and reports count (not imported yet).
    '''
    ...
"""


# =============================================================================
# SCRIPT 11: index.py — The Indexer (Deterministic Enrichment)
# =============================================================================
# PURPOSE: Build FTS5 search index, run VADER sentiment, keyword tagging.
#          All deterministic — no API calls, no LLM, runs locally and instantly.
#
# USAGE:   python index.py fts          Build full-text search index
#          python index.py sentiment    VADER sentiment scoring
#          python index.py keywords     Keyword-based tagging + idea extraction
#          python index.py stats        Recompute conversation statistics
#          python index.py all          Run everything
#
# SUBCOMMANDS:
#
#   FTS (Full-Text Search):
#     Creates SQLite FTS5 virtual table on messages.content.
#     Drops and rebuilds each time for clean state.
#     Result: 3,949,674 messages indexed.
#
#   SENTIMENT (VADER):
#     Uses vaderSentiment library for deterministic sentiment scoring.
#     Scores first 500 chars of each message (VADER works best on short text).
#     Compound score: -1 to +1 → label: positive (≥0.05), negative (≤-0.05), neutral.
#     Batches updates in groups of 5,000 for performance.
#     Dependency: pip install vaderSentiment
#
#   KEYWORDS (Tagging + Idea Detection):
#     TAG_KEYWORDS: 9 categories × ~15 keywords each.
#     Matches against: title + folder_path + first 2000 chars of first message.
#     Short keywords (≤3 chars) use word-boundary regex to avoid false positives.
#     IDEA_PATTERNS: regex patterns detect idea discussions with maturity levels.
#     Result: 1,825 tagged conversations, 397 ideas extracted.
#
#   STATS:
#     Recomputes message_count, char_count, estimated_pages for all conversations.
# =============================================================================

INDEX_PY = """
import sqlite3, sys, re, argparse, logging
from schema import get_db, DB_PATH

# ── 9-Category Keyword Taxonomy ──────────────────────────────────────────────
# Each category has a list of keywords. A conversation is tagged when ANY keyword
# matches in the title, folder path, or first 2000 chars of the first message.

TAG_KEYWORDS = {
    "game_idea": [
        "game", "roguelike", "puzzle", "tetris", "breakout", "rpg", "mancala",
        "pinball", "autobattler", "deck builder", "card game", "board game",
        "game design", "game mechanic", "prototype", "playtest", "unity",
        "pygame", "godot", "pico-8", "pico8", "twine", "text adventure",
    ],
    "app_project": [
        "app idea", "web app", "mobile app", "prototype", "mvp", "saas",
        "dashboard", "calculator", "generator", "planner", "tracker",
        "automation", "api", "chrome extension", "browser extension",
    ],
    "educational": [
        "learning", "teaching", "pedagogy", "curriculum", "course",
        "educational", "lesson", "tutorial", "training", "academy",
        "instructional design", "assessment", "quiz", "flashcard",
        "game-based learning", "gamification",
    ],
    "alchemy": [
        "alchemy", "alchemical", "alchemist", "philosopher's stone",
        "transmutation", "hermetic", "hermeticism", "paracelsus",
        "atalanta fugiens", "splendor solis", "mutus liber", "emblem",
        "prima materia", "magnum opus", "azoth", "vitriol",
    ],
    "pkd": [
        "philip k. dick", "philip k dick", "pkd", "valis", "ubik",
        "do androids dream", "electric sheep", "scanner darkly",
        "exegesis", "dick's", "dickian",
    ],
    "mtg": [
        "magic the gathering", "mtg", "commander", "edh", "deckbuilding",
        "draft", "sealed", "mana", "planeswalker", "scryfall",
        "arena", "liliana", "moxfield",
    ],
    "esoteric": [
        "esoteric", "occult", "tarot", "kabbalah", "kabbalistic",
        "tree of life", "sephiroth", "sigil", "gnostic", "gnosticism",
        "neoplatonism", "neoplatonic", "theurgy", "mysticism",
        "giordano bruno", "agrippa", "ficino", "pico della mirandola",
        "dee", "iamblichus", "plotinus",
    ],
    "coding": [
        "python", "javascript", "typescript", "react", "flask", "django",
        "sqlite", "database", "html", "css", "api", "github", "git",
        "deploy", "server", "docker", "npm", "pip",
    ],
    "personal": [
        "divorce", "therapy", "anxiety", "depression", "relationship",
        "moving", "job", "career", "money", "health", "family",
        "dream", "goals", "plan", "future",
    ],
}

# ── Idea Detection Patterns ──────────────────────────────────────────────────
# Regex patterns that suggest a conversation contains a project idea.
# Each pattern maps to a maturity level.

IDEA_PATTERNS = [
    (r"(?:game|app|tool|platform|product)\\s+idea", "sketch"),      # "I have a game idea"
    (r"(?:let'?s|I want to|I'd like to)\\s+(?:build|make|create)", "design"),  # "let's build X"
    (r"(?:prototype|mvp|proof of concept|poc)", "prototype"),       # "here's a prototype"
    (r"(?:here'?s the code|I built|I made|deployed|live at)", "built"),  # "I deployed it"
]


def build_fts(conn):
    '''Build SQLite FTS5 full-text search index.
    Drops and recreates to avoid stale data from deleted conversations.
    The content= parameter creates a "contentless" index that reads from messages table.'''
    conn.execute("DROP TABLE IF EXISTS messages_fts")
    conn.execute('''
        CREATE VIRTUAL TABLE messages_fts USING fts5(
            content,
            content=messages,       -- read content from messages table
            content_rowid=id        -- use messages.id as the rowid
        )
    ''')
    conn.execute("INSERT INTO messages_fts(messages_fts) VALUES('rebuild')")
    # 'rebuild' is a special FTS5 command that re-indexes all content
    conn.commit()


def run_sentiment(conn):
    '''VADER sentiment analysis on all unscored messages.
    VADER (Valence Aware Dictionary for sEntiment Reasoning) is a
    lexicon-based tool tuned for social media text.

    Scoring: compound score from -1 (most negative) to +1 (most positive).
    Labels: positive (≥0.05), negative (≤-0.05), neutral (between).
    Truncates to 500 chars because VADER works best on short text.
    Batches updates in groups of 5000 for SQLite write performance.'''
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    ...


def run_keywords(conn):
    '''Tag conversations using keyword matching.

    Search text = title + folder_path + first 2000 chars of first message.
    Short keywords (≤3 chars like "pkd", "mtg", "api") use word-boundary
    regex (\\b) to avoid false positives ("rapid" matching "api").

    Also runs IDEA_PATTERNS to detect project ideas and classify maturity.
    Categories prioritized: game > app > educational > other.
    '''
    ...
"""


# =============================================================================
# SCRIPT 12: summarize.py — The Summarizer
# =============================================================================
# PURPOSE: Generate conversation summaries using two strategies:
#   1. Deterministic auto-summarize (free, instant, covers everything)
#   2. ChatGPT batch workflow (human-in-the-loop, for deep summaries)
#
# USAGE:   python summarize.py auto                 Auto-summarize all unsummarized
#          python summarize.py batch-export [--tag]  Generate batch .md files
#          python summarize.py batch-import <file>   Parse ChatGPT response back
#
# AUTO-SUMMARIZE:
#   Extracts first assistant response, truncated to 500 chars, cut at sentence
#   boundary if possible. Covers ALL conversations instantly at zero cost.
#   Result: 2,651 conversations summarized.
#
# BATCH-EXPORT:
#   Groups conversations into .md files (BATCH_SIZE=50 each, EXCERPT_CHARS=3000).
#   Each file includes a structured prompt asking ChatGPT for:
#     CONV_ID, SUMMARY (3 sentences), TAGS (from taxonomy), IDEA (1 sentence or "none")
#   Can filter by tag (e.g. --tag game_idea) for prioritized batches.
#   Result: 24 batch files (13 game_idea, 4 app_project, 7 educational).
#
# BATCH-IMPORT:
#   Parses ChatGPT's response using regex to extract CONV_ID/SUMMARY/TAGS/IDEA blocks.
#   Updates conversations.summary, adds LLM tags (confidence=0.9, method='llm'),
#   and creates ideas table entries.
#
# WORKFLOW:
#   1. Run batch-export → files appear in chunks/summaries/
#   2. Paste each file into ChatGPT → get structured response
#   3. Run batch-import response.md → updates megabase.db
#
# NO API COST: Uses existing ChatGPT Plus subscription, not API calls.
# =============================================================================

SUMMARIZE_PY = """
import os, sys, re, argparse, sqlite3
from schema import get_db, DB_PATH

CHUNKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chunks", "summaries")
BATCH_SIZE = 50       # Conversations per batch file (user requested bigger batches)
EXCERPT_CHARS = 3000  # Characters of conversation text to include per excerpt


def auto_summarize(conn):
    '''Deterministic auto-summarize: extract first assistant response as summary.
    Truncates to 500 chars. Tries to end at a sentence boundary (last period > char 200).
    Only processes conversations that don't already have a summary.
    This is the "free tier" — covers everything instantly.'''
    rows = conn.execute('''
        SELECT c.id,
               (SELECT content FROM messages
                WHERE conversation_id=c.id AND role='assistant'
                ORDER BY id LIMIT 1) as first_response
        FROM conversations c
        WHERE c.summary IS NULL OR c.summary = ''
    ''').fetchall()
    for conv_id, first_response in rows:
        if not first_response:
            continue
        excerpt = first_response[:500].strip()
        last_period = excerpt.rfind(".")
        if last_period > 200:
            excerpt = excerpt[:last_period + 1]  # Cut at sentence boundary
        conn.execute("UPDATE conversations SET summary=? WHERE id=?", (excerpt, conv_id))
    conn.commit()


def batch_export(conn, tag_filter=None):
    '''Generate batch .md files for ChatGPT summarization.
    Each file contains BATCH_SIZE conversation excerpts with structured prompt.
    Prioritized by estimated_pages DESC (biggest conversations first).'''
    # Build query — optionally filter by tag for focused batches
    if tag_filter:
        query = '''SELECT c.id, c.title, ... WHERE t.name=? ORDER BY c.estimated_pages DESC'''
    else:
        query = '''SELECT DISTINCT c.id, c.title, ... ORDER BY c.estimated_pages DESC'''

    # Write batch files with this structure:
    # ## CONV_ID: {id}
    # **Title:** {title}
    # **Source:** {source} | **Pages:** {pages}
    # ```
    # [user] First message text...
    # [assistant] Response text...
    # ```


def batch_import(response_file, conn):
    '''Parse ChatGPT's structured response and update the database.

    Expected format from ChatGPT:
      CONV_ID: 123
      SUMMARY: Three sentences about the conversation...
      TAGS: game_idea, coding
      IDEA: A roguelike game with alchemical mechanics

    Parsing: regex splits on "CONV_ID: N" headers, then extracts SUMMARY/TAGS/IDEA.
    Tags get confidence=0.9, method='llm' (higher confidence than keyword=0.7).
    Ideas get method='llm' and the conversation title as the idea name.
    '''
    content = open(response_file).read()
    blocks = re.split(r"(?:^|\\n)(?:#+\\s*)?CONV_ID:\\s*(\\d+)", content)
    # blocks[0] is preamble, then alternating (id, content) pairs
    for i in range(1, len(blocks) - 1, 2):
        conv_id = int(blocks[i])
        block_text = blocks[i + 1]
        # Extract SUMMARY, TAGS, IDEA with regex
        ...
"""


# =============================================================================
# SCRIPT 13: chunk.py — The Chunker (Deep Reading Export)
# =============================================================================
# PURPOSE: Export conversations as GPT-ready .md chunk files sized for
#          ChatGPT's context window (~60K chars ≈ 15K tokens).
#
# USAGE:   python chunk.py export <id> [--prompt theme_summary]
#          python chunk.py export-tagged <tag> [--min-pages 10]
#          python chunk.py export-ideas
#          python chunk.py list-big [--min-pages 50] [--tag game_idea]
#
# CHUNK STRATEGY:
#   - Target: 60,000 chars per chunk (~15K tokens, fits in GPT-4 with room for prompts)
#   - Split on message boundaries (never mid-message)
#   - Each chunk includes: title, source, date, page count, chunk N of M
#   - First chunk includes the analysis prompt template
#   - Last message of each chunk: "Continue to chunk_02.md for more"
#
# PROMPT TEMPLATES (in prompts/ directory):
#   theme_summary.md    — Topics, decisions, ideas, emotional arc, follow-ups
#   idea_extraction.md  — Extract game/app/edu ideas with name, category, maturity
#   sentiment_deep.md   — Opening mood, turning points, hopes, anxieties, resolution
#   evolution.md        — Starting position, new info, changed assumptions, final position
#
# OUTPUT: chunks/reading/{conv_id}_{title}/chunk_01.md, chunk_02.md, ...
# Records in chunk_exports table for tracking.
#
# USER WORKFLOW:
#   1. Browse megabase in Flask UI → find interesting conversation
#   2. Run: python chunk.py export 566 --prompt idea_extraction
#   3. Paste each chunk file into ChatGPT
#   4. Get deep analysis back
# =============================================================================

CHUNK_PY = """
import os, sys, argparse, sqlite3
from schema import get_db, DB_PATH

CHUNKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chunks", "reading")
PROMPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")
CHUNK_SIZE = 60000  # ~15K tokens


def export_conversation(conn, conv_id, prompt_name="theme_summary"):
    '''Export one conversation as chunked .md files.

    Algorithm:
      1. Fetch all messages for the conversation
      2. Format each as "[ROLE] (date)\\ncontent"
      3. Accumulate into chunks up to CHUNK_SIZE
      4. When adding a message would exceed the limit, start a new chunk
      5. Write each chunk to disk with header + prompt (chunk 1 only)
      6. Record in chunk_exports table
    '''
    msgs = conn.execute(
        "SELECT role, content, created_at FROM messages WHERE conversation_id=? ORDER BY id",
        (conv_id,),
    ).fetchall()

    # Build message parts
    full_parts = []
    for role, content, ts in msgs:
        header = f"[{role.upper()}]"
        if ts:
            header += f" ({ts[:10]})"
        full_parts.append(f"{header}\\n{content}")

    # Split into chunks at message boundaries
    chunks = []
    current_chunk, current_size = [], 0
    for part in full_parts:
        if current_size + len(part) > CHUNK_SIZE and current_chunk:
            chunks.append("\\n\\n---\\n\\n".join(current_chunk))
            current_chunk, current_size = [part], len(part)
        else:
            current_chunk.append(part)
            current_size += len(part)
    if current_chunk:
        chunks.append("\\n\\n---\\n\\n".join(current_chunk))

    # Write chunk files
    for i, chunk_text in enumerate(chunks):
        filepath = f"chunks/reading/{conv_id}_title/chunk_{i+1:02d}.md"
        # Header: title, source, date, pages, chunk N of M
        # Chunk 1 gets the analysis prompt
        # Last chunk gets "Continue to chunk_N+1.md" footer
"""


# =============================================================================
# SCRIPT 14: verify.py — Data Integrity Checker
# =============================================================================
# PURPOSE: Run after any ingestion to verify data integrity.
#
# USAGE:   python verify.py
#
# CHECKS:
#   1. Source counts (convos, messages, text MB per source)
#   2. Orphan messages (messages referencing deleted conversations)
#   3. Orphan conversations (conversations referencing deleted sources)
#   4. Empty conversations (0 messages)
#   5. Missing char_count statistics
#   6. Database file size
#   7. Summary coverage (how many have summaries)
#   8. Tag coverage (how many are tagged)
#   9. FTS5 index existence
#
# Exit code: 0 = all checks pass, 1 = orphans detected
# =============================================================================

VERIFY_PY = """
import sqlite3, sys
from schema import DB_PATH


def verify(db_path=None):
    conn = sqlite3.connect(db_path or DB_PATH)

    # Source breakdown table
    rows = conn.execute('''
        SELECT s.name, count(c.id), sum(c.message_count), round(sum(c.char_count)/1e6, 1)
        FROM sources s LEFT JOIN conversations c ON c.source_id=s.id
        GROUP BY s.name ORDER BY sum(c.message_count) DESC
    ''').fetchall()

    # Orphan checks — these should always be 0
    orphan_msgs = conn.execute(
        "SELECT count(*) FROM messages WHERE conversation_id NOT IN (SELECT id FROM conversations)"
    ).fetchone()[0]

    # Empty conversations, FTS5 status, summary/tag coverage
    ...

    if orphan_msgs > 0 or orphan_convos > 0:
        print("*** WARNING: Orphaned records detected! ***")
        return 1
    return 0
"""


# =============================================================================
# SCRIPT 15: app.py — The Browser (Flask Web UI)
# =============================================================================
# PURPOSE: Card-based web UI for browsing the megabase.
#
# USAGE:   python app.py       (runs on http://localhost:5555)
#
# ROUTES:
#   /                           Card grid (home page)
#   /conversation/<id>          Full conversation view
#   /ideas                      Ideas catalog
#   /api/search                 JSON autocomplete endpoint
#
# HOME PAGE (/):
#   - Search bar → FTS5 full-text search across all messages
#   - Source dropdown → filter by data source
#   - Tag dropdown → filter by tag category
#   - Sort options → pages (biggest first), date, messages, title
#   - 48 cards per page with pagination
#   - Each card shows: source badge, title, summary excerpt, date, messages, tags, pages
#
# CONVERSATION VIEW (/conversation/<id>):
#   - Header: title, source, dates, page count, tag pills, summary, ideas
#   - Messages: role-colored (purple=user, green=assistant, cyan=sender, orange=system)
#   - Sentiment badges per message
#   - Message pagination (50 per page)
#   - Truncation at 5000 chars with "show more" indicator
#
# IDEAS CATALOG (/ideas):
#   - Category filter pills (game, app, educational, other)
#   - Card grid: idea name, category, maturity badge, source conversation link
#
# DESIGN: Dark theme, responsive grid, no JavaScript dependencies.
# =============================================================================

APP_PY = """
import os, sqlite3
from flask import Flask, render_template, request, jsonify
from schema import DB_PATH

app = Flask(__name__)


def get_db():
    '''Thread-local database connection with Row factory
    for dict-like access to query results.'''
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    '''Home page: card grid with search, filters, sort, pagination.

    Query building:
      - q (search): Uses FTS5 MATCH on messages_fts virtual table,
        then joins back to conversations via message.conversation_id
      - source: Exact match on sources.name
      - tag: Subquery through conversation_tags ↔ tags join
      - sort: Maps to ORDER BY clause (pages/date/messages/title)
      - Pagination: LIMIT/OFFSET with 48 per page
    '''
    ...

@app.route("/conversation/<int:conv_id>")
def conversation(conv_id):
    '''Full conversation view with message-level display.
    Includes tags, ideas, sentiment badges, and message pagination.'''
    ...

@app.route("/ideas")
def ideas():
    '''Ideas catalog with category filtering.
    Joins ideas → conversations → sources for full context.'''
    ...

@app.route("/api/search")
def api_search():
    '''JSON autocomplete: LIKE search on conversation titles.
    Returns top 20 matches sorted by page count.'''
    ...


if __name__ == "__main__":
    app.run(debug=True, port=5555)
"""


# =============================================================================
# PROMPT TEMPLATES (in prompts/ directory)
# =============================================================================
# These are included as the first chunk of deep reading exports.
# User pastes chunk into ChatGPT, the prompt guides the analysis.

PROMPT_THEME_SUMMARY = """
Analyze this conversation and provide:
1. **Main Topics** (3-5 bullet points): What subjects were discussed?
2. **Key Decisions**: What was decided or concluded?
3. **Ideas Generated**: List any game, app, product, or project ideas that emerged.
4. **Emotional Arc**: How did the tone/energy shift through the conversation?
5. **Follow-up Questions**: What threads were left open or unresolved?
"""

PROMPT_IDEA_EXTRACTION = """
Extract every game, app, educational product, or creative project idea.
For each: Name, Category (game/app/educational/product/other),
Description (2-3 sentences), Maturity (sketch/design/prototype/built),
Key Features (bullet list).
"""

PROMPT_SENTIMENT_DEEP = """
Analyze the emotional arc:
1. Opening mood
2. Turning points (where does tone shift?)
3. Hopes and dreams expressed
4. Anxieties and concerns
5. Resolution (how does it end emotionally?)
6. Overall sentiment: -5 (very negative) to +5 (very positive)
"""

PROMPT_EVOLUTION = """
Track how thinking evolves:
1. Starting position (what did the user believe at the start?)
2. New information (what did they learn?)
3. Changed assumptions (which initial ideas were modified?)
4. Final position (where did they end up?)
5. Unresolved tensions (what contradictions remain?)
"""


# =============================================================================
# DEPENDENCIES
# =============================================================================
# pip install flask              — Web framework for app.py
# pip install PyMuPDF            — PDF text extraction (imported as fitz)
# pip install vaderSentiment     — VADER sentiment analysis
#
# Python stdlib (no install needed):
#   html.parser    — HTML parsing for chat files
#   mailbox        — mbox streaming for Gmail
#   sqlite3        — Database
#   json, re, os   — Standard utilities
# =============================================================================


# =============================================================================
# HOW TO RUN THE FULL PIPELINE
# =============================================================================
# Phase 1: Create schema
#   python schema.py
#
# Phase 2: Ingest all sources (can run in parallel)
#   python ingest_chatgpt_json.py
#   python ingest_html_chats.py
#   python ingest_pdf_chats.py
#   python ingest_claude_db.py
#   python ingest_facebook_json.py
#   python ingest_google_chat.py
#   python ingest_pkd_chats.py
#   python ingest_sms_twitter.py
#   # python ingest_gmail_mbox.py    # (deferred)
#
# Phase 3: Enrich
#   python index.py all
#   python summarize.py auto
#   python summarize.py batch-export --tag game_idea
#
# Phase 4: Verify
#   python verify.py
#
# Phase 5: Browse and deep-read
#   python app.py                    # localhost:5555
#   python chunk.py list-big
#   python chunk.py export 566
# =============================================================================


if __name__ == "__main__":
    print(__doc__)
    print("This is a reference document. Run individual scripts from C:\\Dev\\megabase\\")
