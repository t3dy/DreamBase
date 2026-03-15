# Dreambase: Full Project Context Document
**Generated: 2026-03-14**
**Purpose:** Complete context for ChatGPT deep analysis sessions.
Contains all code, templates, design documents, and data analysis.

## Project Summary
Dreambase (formerly Megabase) is a Personal Knowledge Archaeology System that unifies
2+ years of LLM conversations, social media, texts, and emails into one searchable
SQLite database with a Flask web UI. Built across 8+ Claude Code sessions.

**Stats:** 4,308 conversations | 3.9M messages | 1.3 GB database | 15 Python scripts |
7 data visualizations | 3 showcase dream pages | 397 extracted ideas

---

## DESIGN INSTINCTS ANALYSIS (from database mining)

### Topic Prevalence (conversations tagged)
| Tag | Conversations | Total Pages | Avg Pages | User Sentiment |
|-----|--------------|-------------|-----------|----------------|
| game_idea | 628 | 25,724 | 41.0 | +0.193 |
| esoteric | 566 | 30,398 | 53.7 | +0.160 |
| personal | 549 | 20,132 | 36.7 | +0.161 |
| alchemy | 442 | 30,574 | 69.2 | +0.152 |
| educational | 337 | 15,425 | 45.8 | +0.233 |
| mtg | 261 | 11,690 | 44.8 | +0.183 |
| coding | 248 | 8,336 | 33.6 | +0.199 |
| app_project | 166 | 5,935 | 35.8 | +0.218 |
| pkd | 112 | 3,938 | 35.2 | +0.158 |

### Sentiment Patterns (what the data reveals about scholarly style)

**Most Positive Topics (by user message sentiment):**
1. Educational (+0.233) - Ted is most enthusiastic when designing things that teach
2. App Projects (+0.218) - Building functional tools generates positive energy
3. Coding (+0.199) - Technical problem-solving is satisfying

**Most Complex/Serious Topics (lower but still positive sentiment):**
1. Alchemy (+0.152) - Deepest engagement (69.2 avg pages) but most wrestling
2. PKD (+0.158) - Literary/philosophical work carries more tension
3. Esoteric (+0.160) - Intellectual depth correlates with seriousness

**Key Insight:** Ted writes most positively about EDUCATIONAL topics and most
extensively about ALCHEMY topics. The sweet spot - where passion meets depth -
is where these two overlap: games that teach through alchemical mechanics.
The Alchemy Board Game sits exactly at this intersection.

### Idea Maturity Distribution
| Category | Sketch | Design | Prototype | Built |
|----------|--------|--------|-----------|-------|
| Game | 230 | 34 | 19 | 1 |
| App | 32 | 2 | 6 | 0 |
| Educational | 0 | 5 | 3 | 2 |
| Other | 3 | 35 | 18 | 7 |

### Design Values (evidence-based)
1. **Implicit Pedagogy** - Games should teach through mechanics, not tutorials
2. **Discovery Over Instruction** - Hidden complexity reveals itself through play
3. **Data Density** - Tufte-inspired information design, no chartjunk
4. **Systems Thinking** - Everything connects; ideas cross-pollinate across domains
5. **Honest Self-Reflection** - Willing to confront what the data shows

---

## Database Schema
**File:** `schema.py` (4,384 chars)

```py
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
```

---

## Flask Web Application
**File:** `app.py` (16,748 chars)

```py
"""
Dreambase — Haunt Your Own Records.
Flask app for browsing conversations, ideas, and tags.
Card grid with search, filters, expand to full conversation view.
Showcase pages for curated dream deep-dives.
"""

import json
import os
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for
from schema import DB_PATH

# Showcase definitions — curated dream pages with tabbed sections.
# conversation_ids: de-duplicated primaries (chatgpt source preferred, then claude).
# Content fields (narrative, quotes, timeline) populated by ChatGPT batch workflow.
SHOWCASES = {
    "bubble-bog-witch": {
        "slug": "bubble-bog-witch",
        "title": "Bubble Bog Witch",
        "hook": "What if transmutation was a platformer mechanic and the swamp was alive?",
        "category": "game",
        "maturity": "sketch",
        "conversation_ids": [40, 239, 3580, 2565],
        "tags": ["game_idea", "alchemy", "platformer"],
        "pedagogy": "Environmental storytelling through movement mechanics. The player learns about the Bog Witch's world by how bubbles behave in different zones — not through cutscenes or text dumps.",
        "difficulty_easy": "Bubbles as pure traversal mechanic (bounce to reach platforms)",
        "difficulty_medium": "Bubbles as resource (limited supply, strategic popping)",
        "difficulty_hard": "Bubbles as ecosystem (witch's magic affects behavior, player reads environment)",
        "narrative": None,
        "timeline_entries": [],
        "quotes": [],
        "images": [],
    },
    "dungeon-autobattler": {
        "slug": "dungeon-autobattler",
        "title": "Dungeon Autobattler",
        "hook": "Draft your army, set the strategy, then watch the chaos unfold. The skill is in the preparation.",
        "category": "game",
        "maturity": "design",
        "conversation_ids": [4, 10, 37, 7, 2580, 2578, 2591, 2564, 2582, 2668, 2577, 3594],
        "tags": ["game_idea", "autobattler", "roguelike", "procedural"],
        "pedagogy": "Decision-making under uncertainty with incomplete information. The core loop: build a team, commit it, watch outcomes you can't control. Learning happens in the gap between expectation and result.",
        "difficulty_easy": "Rock-paper-scissors unit types — learn to read enemy composition",
        "difficulty_medium": "Synergy bonuses between unit types — balance counter-picking vs synergy",
        "difficulty_hard": "Procedural dungeon rooms with unknown encounters — build for adaptability",
        "narrative": None,
        "timeline_entries": [],
        "quotes": [],
        "images": [],
    },
    "alchemy-board-game": {
        "slug": "alchemy-board-game",
        "title": "Alchemy Board Game",
        "hook": "The Great Work as engine-building: transmutation chains, hidden knowledge, and the joy of discovery.",
        "category": "game",
        "maturity": "prototype",
        "conversation_ids": [567, 851, 2700, 347, 500, 531, 533, 511, 513, 2523, 2515],
        "tags": ["game_idea", "alchemy", "board_game", "educational"],
        "pedagogy": "Transformation systems — how inputs become outputs through rule-governed processes. The alchemical Great Work is literally an optimization problem disguised as mysticism.",
        "difficulty_easy": "Linear transmutation (lead to iron to silver to gold) — one path, learn the sequence",
        "difficulty_medium": "Branching paths (sulfur + mercury = cinnabar OR philosopher's stone) — trade-offs emerge",
        "difficulty_hard": "Competing economies (multiplayer: your waste products are my inputs) — read opponents",
        "narrative": None,
        "timeline_entries": [],
        "quotes": [],
        "images": [],
    },
}

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    conn = get_db()
    q = request.args.get("q", "").strip()
    source = request.args.get("source", "")
    tag = request.args.get("tag", "")
    sort = request.args.get("sort", "pages")
    page = int(request.args.get("page", 1))
    per_page = 48

    # Build query
    conditions = []
    params = []

    if q:
        # FTS search
        conditions.append("""c.id IN (
            SELECT m.conversation_id FROM messages m
            JOIN messages_fts ON messages_fts.rowid=m.id
            WHERE messages_fts MATCH ?
        )""")
        params.append(q)

    if source:
        conditions.append("s.name = ?")
        params.append(source)

    if tag:
        conditions.append("""c.id IN (
            SELECT ct.conversation_id FROM conversation_tags ct
            JOIN tags t ON t.id=ct.tag_id WHERE t.name=?
        )""")
        params.append(tag)

    where = " AND ".join(conditions) if conditions else "1=1"

    sort_map = {
        "pages": "c.estimated_pages DESC",
        "date": "c.created_at DESC",
        "messages": "c.message_count DESC",
        "title": "c.title ASC",
    }
    order = sort_map.get(sort, "c.estimated_pages DESC")

    total = conn.execute(f"""
        SELECT count(*) FROM conversations c JOIN sources s ON s.id=c.source_id WHERE {where}
    """, params).fetchone()[0]

    convos = conn.execute(f"""
        SELECT c.id, c.title, c.summary, c.created_at, c.estimated_pages, c.message_count,
               s.name as source_name
        FROM conversations c JOIN sources s ON s.id=c.source_id
        WHERE {where}
        ORDER BY {order}
        LIMIT ? OFFSET ?
    """, params + [per_page, (page - 1) * per_page]).fetchall()

    # Get tags for each conversation
    conv_ids = [c["id"] for c in convos]
    conv_tags = {}
    if conv_ids:
        ph = ",".join("?" * len(conv_ids))
        tag_rows = conn.execute(f"""
            SELECT ct.conversation_id, t.name
            FROM conversation_tags ct JOIN tags t ON t.id=ct.tag_id
            WHERE ct.conversation_id IN ({ph})
        """, conv_ids).fetchall()
        for tr in tag_rows:
            conv_tags.setdefault(tr["conversation_id"], []).append(tr["name"])

    # Get available sources and tags for filters
    sources = conn.execute("SELECT DISTINCT name FROM sources ORDER BY name").fetchall()
    tags = conn.execute("""
        SELECT t.name, count(*) as cnt FROM tags t
        JOIN conversation_tags ct ON ct.tag_id=t.id
        GROUP BY t.name ORDER BY cnt DESC
    """).fetchall()

    total_pages = (total + per_page - 1) // per_page

    conn.close()
    return render_template("index.html",
        convos=convos, conv_tags=conv_tags,
        sources=sources, tags=tags,
        q=q, source=source, tag=tag, sort=sort,
        page=page, total_pages=total_pages, total=total)


@app.route("/conversation/<int:conv_id>")
def conversation(conv_id):
    conn = get_db()

    conv = conn.execute("""
        SELECT c.*, s.name as source_name
        FROM conversations c JOIN sources s ON s.id=c.source_id
        WHERE c.id=?
    """, (conv_id,)).fetchone()

    if not conv:
        return "Not found", 404

    # Get messages with pagination
    msg_page = int(request.args.get("msg_page", 1))
    msgs_per_page = 50
    total_msgs = conv["message_count"] or 0

    messages = conn.execute("""
        SELECT role, content, created_at, sentiment_vader, sentiment_label, char_count
        FROM messages WHERE conversation_id=?
        ORDER BY id
        LIMIT ? OFFSET ?
    """, (conv_id, msgs_per_page, (msg_page - 1) * msgs_per_page)).fetchall()

    # Get tags
    tags = conn.execute("""
        SELECT t.name, ct.confidence, ct.method
        FROM conversation_tags ct JOIN tags t ON t.id=ct.tag_id
        WHERE ct.conversation_id=?
    """, (conv_id,)).fetchall()

    # Get ideas
    ideas = conn.execute("SELECT * FROM ideas WHERE conversation_id=?", (conv_id,)).fetchall()

    total_msg_pages = (total_msgs + msgs_per_page - 1) // msgs_per_page

    conn.close()
    return render_template("conversation.html",
        conv=conv, messages=messages, tags=tags, ideas=ideas,
        msg_page=msg_page, total_msg_pages=total_msg_pages)


@app.route("/ideas")
def ideas():
    conn = get_db()
    category = request.args.get("category", "")

    conditions = []
    params = []
    if category:
        conditions.append("i.category = ?")
        params.append(category)

    where = " AND ".join(conditions) if conditions else "1=1"

    rows = conn.execute(f"""
        SELECT i.*, c.title as conv_title, c.estimated_pages, s.name as source_name
        FROM ideas i
        JOIN conversations c ON c.id=i.conversation_id
        JOIN sources s ON s.id=c.source_id
        WHERE {where}
        ORDER BY i.category, i.name
    """, params).fetchall()

    categories = conn.execute("SELECT DISTINCT category FROM ideas ORDER BY category").fetchall()

    conn.close()
    return render_template("ideas.html", ideas=rows, categories=categories, category=category)


@app.route("/viz")
def viz():
    conn = get_db()

    # 1. Intellectual Timeline — conversations by month and source
    timeline = conn.execute("""
        SELECT substr(c.created_at,1,7) as month, s.name as source,
               count(*) as cnt, sum(c.estimated_pages) as pages
        FROM conversations c JOIN sources s ON s.id=c.source_id
        WHERE c.created_at IS NOT NULL AND c.created_at > '2007-12'
        GROUP BY month, source ORDER BY month
    """).fetchall()

    # 2. Topic Constellation — tag co-occurrence
    cooccurrence = conn.execute("""
        SELECT t1.name as tag1, t2.name as tag2, count(*) as cnt
        FROM conversation_tags ct1
        JOIN conversation_tags ct2 ON ct1.conversation_id=ct2.conversation_id AND ct1.tag_id < ct2.tag_id
        JOIN tags t1 ON t1.id=ct1.tag_id
        JOIN tags t2 ON t2.id=ct2.tag_id
        GROUP BY t1.name, t2.name ORDER BY cnt DESC
    """).fetchall()

    # Tag totals for node sizing
    tag_totals = conn.execute("""
        SELECT t.name, count(*) as cnt FROM tags t
        JOIN conversation_tags ct ON ct.tag_id=t.id
        GROUP BY t.name ORDER BY cnt DESC
    """).fetchall()

    # 3. Activity Heatmap — messages per week
    heatmap = conn.execute("""
        SELECT substr(c.created_at,1,10) as day, s.name as source, count(*) as cnt
        FROM conversations c JOIN sources s ON s.id=c.source_id
        WHERE c.created_at IS NOT NULL AND c.created_at >= '2024-01-01'
        GROUP BY day, source ORDER BY day
    """).fetchall()

    # 4. Idea Funnel — by category and maturity
    idea_funnel = conn.execute("""
        SELECT category, maturity, count(*) as cnt
        FROM ideas GROUP BY category, maturity ORDER BY category
    """).fetchall()

    # 5. Sentiment River — monthly sentiment by source
    sentiment = conn.execute("""
        SELECT substr(m.created_at,1,7) as month, s.name as source,
               round(avg(m.sentiment_vader),3) as avg_sent,
               count(*) as cnt,
               sum(CASE WHEN m.sentiment_label='positive' THEN 1 ELSE 0 END) as pos,
               sum(CASE WHEN m.sentiment_label='negative' THEN 1 ELSE 0 END) as neg,
               sum(CASE WHEN m.sentiment_label='neutral' THEN 1 ELSE 0 END) as neu
        FROM messages m
        JOIN conversations c ON c.id=m.conversation_id
        JOIN sources s ON s.id=c.source_id
        WHERE m.created_at IS NOT NULL AND m.sentiment_vader IS NOT NULL
              AND m.created_at >= '2024-01-01'
        GROUP BY month, source ORDER BY month
    """).fetchall()

    # 6. Treemap — conversation sizes by source
    treemap = conn.execute("""
        SELECT s.name as source, count(*) as convos,
               sum(c.estimated_pages) as total_pages,
               sum(c.message_count) as total_msgs,
               round(sum(c.char_count)/1e6, 1) as text_mb
        FROM conversations c JOIN sources s ON s.id=c.source_id
        GROUP BY s.name ORDER BY total_pages DESC
    """).fetchall()

    # Top conversations for treemap detail
    top_convos = conn.execute("""
        SELECT c.title, c.estimated_pages, s.name as source
        FROM conversations c JOIN sources s ON s.id=c.source_id
        WHERE c.estimated_pages > 50
        ORDER BY c.estimated_pages DESC LIMIT 60
    """).fetchall()

    # 7. Sparkline Table — per-tag stats with monthly trends
    sparkline_tags = conn.execute("""
        SELECT t.name,
               count(DISTINCT ct.conversation_id) as convos,
               (SELECT count(*) FROM ideas i
                JOIN conversation_tags ct2 ON ct2.conversation_id=i.conversation_id
                WHERE ct2.tag_id=t.id) as ideas,
               (SELECT round(avg(m2.sentiment_vader),3) FROM messages m2
                JOIN conversations c2 ON c2.id=m2.conversation_id
                JOIN conversation_tags ct3 ON ct3.conversation_id=c2.id
                WHERE ct3.tag_id=t.id AND m2.sentiment_vader IS NOT NULL) as avg_sent,
               (SELECT round(avg(c3.estimated_pages),1) FROM conversations c3
                JOIN conversation_tags ct4 ON ct4.conversation_id=c3.id
                WHERE ct4.tag_id=t.id) as avg_pages
        FROM tags t
        JOIN conversation_tags ct ON ct.tag_id=t.id
        GROUP BY t.name ORDER BY convos DESC
    """).fetchall()

    # Monthly trend per tag (for sparklines)
    tag_trends = conn.execute("""
        SELECT t.name, substr(c.created_at,1,7) as month, count(*) as cnt
        FROM conversation_tags ct
        JOIN tags t ON t.id=ct.tag_id
        JOIN conversations c ON c.id=ct.conversation_id
        WHERE c.created_at IS NOT NULL AND c.created_at >= '2024-06-01'
        GROUP BY t.name, month ORDER BY t.name, month
    """).fetchall()

    conn.close()
    return render_template("viz.html",
        timeline=[dict(r) for r in timeline],
        cooccurrence=[dict(r) for r in cooccurrence],
        tag_totals=[dict(r) for r in tag_totals],
        heatmap=[dict(r) for r in heatmap],
        idea_funnel=[dict(r) for r in idea_funnel],
        sentiment=[dict(r) for r in sentiment],
        treemap=[dict(r) for r in treemap],
        top_convos=[dict(r) for r in top_convos],
        sparkline_tags=[dict(r) for r in sparkline_tags],
        tag_trends=[dict(r) for r in tag_trends])


@app.route("/showcases")
def showcases_index():
    """List all showcase dream pages."""
    return render_template("showcases.html", showcases=list(SHOWCASES.values()))


@app.route("/dream/<slug>")
def showcase(slug):
    """Tabbed showcase page for a curated dream."""
    sc = SHOWCASES.get(slug)
    if not sc:
        return "Not found", 404

    conn = get_db()

    # Fetch the linked conversations
    conv_ids = sc["conversation_ids"]
    if conv_ids:
        ph = ",".join("?" * len(conv_ids))
        conversations = conn.execute(f"""
            SELECT c.id, c.title, c.estimated_pages, c.message_count,
                   c.created_at, s.name as source_name
            FROM conversations c JOIN sources s ON s.id=c.source_id
            WHERE c.id IN ({ph})
            ORDER BY c.estimated_pages DESC
        """, conv_ids).fetchall()
    else:
        conversations = []

    total_pages = sum(c["estimated_pages"] or 0 for c in conversations)

    # Load any JSON sidecar data (narrative, quotes, timeline) if it exists
    sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "showcases", f"{slug}.json")
    sidecar = {}
    if os.path.exists(sidecar_path):
        with open(sidecar_path, "r", encoding="utf-8") as f:
            sidecar = json.load(f)

    # Merge sidecar into showcase data (sidecar overrides defaults)
    narrative = sidecar.get("narrative") or sc.get("narrative")
    timeline_entries = sidecar.get("timeline_entries") or sc.get("timeline_entries", [])
    quotes = sidecar.get("quotes") or sc.get("quotes", [])
    images = sidecar.get("images") or sc.get("images", [])

    conn.close()
    return render_template("showcase.html",
        showcase=sc,
        conversations=[dict(c) for c in conversations],
        total_pages=int(total_pages),
        tags=sc.get("tags", []),
        timeline_entries=timeline_entries,
        quotes=quotes,
        images=images)


@app.route("/api/search")
def api_search():
    """Quick search API for autocomplete."""
    conn = get_db()
    q = request.args.get("q", "").strip()
    if not q or len(q) < 2:
        return jsonify([])

    rows = conn.execute("""
        SELECT c.id, c.title, s.name as source, c.estimated_pages
        FROM conversations c JOIN sources s ON s.id=c.source_id
        WHERE c.title LIKE ?
        ORDER BY c.estimated_pages DESC LIMIT 20
    """, (f"%{q}%",)).fetchall()

    conn.close()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    app.run(debug=True, port=5555)
```

---

## Indexer (FTS5, VADER, Keywords)
**File:** `index.py` (9,881 chars)

```py
"""
Megabase Indexer — deterministic enrichment pass.
Subcommands: fts, sentiment, keywords, stats, all
"""

import sqlite3
import sys
import re
import argparse
import logging
from schema import get_db, DB_PATH

logger = logging.getLogger("index")

# ── Keyword taxonomy for tagging ──────────────────────────────────────────

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
        "neoplatonism", "neoplatonic", "theurgy", "mysticism", "mystic",
        "divination", "astrology", "geomancy", "enochian",
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

# Idea detection — conversations with these patterns get an ideas table entry
IDEA_PATTERNS = [
    (r"(?:game|app|tool|platform|product)\s+idea", "sketch"),
    (r"(?:let'?s|I want to|I'd like to)\s+(?:build|make|create|develop)", "design"),
    (r"(?:prototype|mvp|proof of concept|poc)", "prototype"),
    (r"(?:here'?s the code|I built|I made|deployed|live at)", "built"),
]


def build_fts(conn):
    """Build FTS5 full-text search index on messages."""
    print("Building FTS5 index...")
    # Drop and recreate to avoid stale data
    conn.execute("DROP TABLE IF EXISTS messages_fts")
    conn.execute("""
        CREATE VIRTUAL TABLE messages_fts USING fts5(
            content,
            content=messages,
            content_rowid=id
        )
    """)
    conn.execute("INSERT INTO messages_fts(messages_fts) VALUES('rebuild')")
    count = conn.execute("SELECT count(*) FROM messages_fts").fetchone()[0]
    conn.commit()
    print(f"FTS5 index built: {count} messages indexed.")


def run_sentiment(conn):
    """Run VADER sentiment analysis on messages that don't have scores yet."""
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    analyzer = SentimentIntensityAnalyzer()

    # Only process messages without sentiment
    rows = conn.execute(
        "SELECT id, content FROM messages WHERE sentiment_vader IS NULL AND content IS NOT NULL AND char_count > 10"
    ).fetchall()

    print(f"Running VADER sentiment on {len(rows)} messages...")
    batch = []
    for i, (msg_id, content) in enumerate(rows):
        # VADER works best on short text — truncate to first 500 chars
        text = content[:500] if content else ""
        scores = analyzer.polarity_scores(text)
        compound = scores["compound"]

        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        batch.append((compound, label, msg_id))

        if len(batch) >= 5000:
            conn.executemany(
                "UPDATE messages SET sentiment_vader=?, sentiment_label=? WHERE id=?", batch
            )
            conn.commit()
            batch = []
            if (i + 1) % 100000 == 0:
                print(f"  Processed {i+1}/{len(rows)}...")

    if batch:
        conn.executemany(
            "UPDATE messages SET sentiment_vader=?, sentiment_label=? WHERE id=?", batch
        )
        conn.commit()

    print(f"Sentiment analysis complete. {len(rows)} messages scored.")


def run_keywords(conn):
    """Tag conversations based on keyword matching in titles and first messages."""
    print("Running keyword tagging...")

    # Ensure tags exist
    for tag_name in TAG_KEYWORDS:
        conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
    conn.commit()

    tag_ids = {row[0]: row[1] for row in conn.execute("SELECT name, id FROM tags").fetchall()}

    # Get all conversations with their titles and first message text
    convos = conn.execute("""
        SELECT c.id, c.title, c.folder_path,
               (SELECT content FROM messages WHERE conversation_id=c.id ORDER BY id LIMIT 1) as first_msg
        FROM conversations c
    """).fetchall()

    tagged_count = 0
    idea_count = 0

    for conv_id, title, folder, first_msg in convos:
        # Build searchable text from title + folder + first message
        search_text = " ".join(filter(None, [
            (title or "").lower(),
            (folder or "").lower().replace("/", " ").replace("\\", " "),
            (first_msg or "")[:2000].lower(),
        ]))

        # Tag matching
        for tag_name, keywords in TAG_KEYWORDS.items():
            for kw in keywords:
                if len(kw) <= 3:
                    # Short keywords: whole-word match
                    if re.search(r'\b' + re.escape(kw) + r'\b', search_text):
                        conn.execute(
                            "INSERT OR IGNORE INTO conversation_tags (conversation_id, tag_id, confidence, method) "
                            "VALUES (?, ?, 0.7, 'keyword')",
                            (conv_id, tag_ids[tag_name]),
                        )
                        tagged_count += 1
                        break
                else:
                    if kw in search_text:
                        conn.execute(
                            "INSERT OR IGNORE INTO conversation_tags (conversation_id, tag_id, confidence, method) "
                            "VALUES (?, ?, 0.7, 'keyword')",
                            (conv_id, tag_ids[tag_name]),
                        )
                        tagged_count += 1
                        break

        # Idea detection
        for pattern, maturity in IDEA_PATTERNS:
            if re.search(pattern, search_text, re.IGNORECASE):
                # Extract idea name from title
                idea_name = title or "Untitled idea"
                # Determine category
                category = "other"
                for cat in ("game_idea", "app_project", "educational"):
                    if any(kw in search_text for kw in TAG_KEYWORDS.get(cat, [])[:5]):
                        category = cat.replace("_idea", "").replace("_project", "")
                        break

                conn.execute(
                    "INSERT INTO ideas (conversation_id, name, category, maturity, method, created_at) "
                    "VALUES (?, ?, ?, ?, 'keyword', datetime('now'))",
                    (conv_id, idea_name, category, maturity),
                )
                idea_count += 1
                break  # One idea per conversation

    conn.commit()
    unique_tagged = conn.execute("SELECT count(DISTINCT conversation_id) FROM conversation_tags").fetchone()[0]
    print(f"Keyword tagging complete. {unique_tagged} conversations tagged, {idea_count} ideas extracted.")


def update_stats(conn):
    """Recompute message_count, char_count, estimated_pages for all conversations."""
    print("Updating conversation stats...")
    conn.execute("""
        UPDATE conversations SET
            message_count = (SELECT count(*) FROM messages WHERE messages.conversation_id = conversations.id),
            char_count = (SELECT COALESCE(sum(char_count), 0) FROM messages WHERE messages.conversation_id = conversations.id),
            estimated_pages = (SELECT COALESCE(sum(char_count), 0) FROM messages WHERE messages.conversation_id = conversations.id) / 3000.0
    """)
    conn.commit()
    print("Stats updated.")


def main():
    parser = argparse.ArgumentParser(description="Megabase Indexer")
    parser.add_argument("command", choices=["fts", "sentiment", "keywords", "stats", "all"],
                        help="Which indexing operation to run")
    args = parser.parse_args()

    conn = get_db()

    if args.command in ("stats", "all"):
        update_stats(conn)

    if args.command in ("fts", "all"):
        build_fts(conn)

    if args.command in ("sentiment", "all"):
        run_sentiment(conn)

    if args.command in ("keywords", "all"):
        run_keywords(conn)

    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
```

---

## Summarizer (Batch Export/Import)
**File:** `summarize.py` (9,134 chars)

```py
"""
Megabase Summarizer — hybrid deterministic + ChatGPT batch workflow.

Subcommands:
  auto          Extract first assistant response as provisional summary (instant, free)
  batch-export  Generate .md files with conversation excerpts for ChatGPT summarization
  batch-import  Parse ChatGPT's structured responses back into the DB
"""

import os
import sys
import re
import argparse
import sqlite3

from schema import get_db, DB_PATH

CHUNKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chunks", "summaries")

# How many conversations per batch file
BATCH_SIZE = 50

# How many chars of conversation to include per excerpt
EXCERPT_CHARS = 3000


def auto_summarize(conn):
    """Extract first assistant response (truncated) as provisional summary for all conversations."""
    print("Running auto-summarize (deterministic excerpts)...")

    rows = conn.execute("""
        SELECT c.id,
               (SELECT content FROM messages
                WHERE conversation_id=c.id AND role='assistant'
                ORDER BY id LIMIT 1) as first_response
        FROM conversations c
        WHERE c.summary IS NULL OR c.summary = ''
    """).fetchall()

    count = 0
    for conv_id, first_response in rows:
        if not first_response:
            continue
        # Take first 500 chars, clean up, end at sentence boundary if possible
        excerpt = first_response[:500].strip()
        # Try to end at a sentence
        last_period = excerpt.rfind(".")
        if last_period > 200:
            excerpt = excerpt[:last_period + 1]
        conn.execute("UPDATE conversations SET summary=? WHERE id=?", (excerpt, conv_id))
        count += 1

    conn.commit()
    print(f"Auto-summarized {count} conversations with first-response excerpts.")


def batch_export(conn, tag_filter=None):
    """Generate batch .md files for ChatGPT summarization.
    Groups conversations by BATCH_SIZE, includes title + first EXCERPT_CHARS of content."""

    os.makedirs(CHUNKS_DIR, exist_ok=True)

    # Build query — optionally filter by tag
    if tag_filter:
        query = """
            SELECT c.id, c.title, c.source_id, s.name as source_name, c.estimated_pages
            FROM conversations c
            JOIN sources s ON s.id=c.source_id
            JOIN conversation_tags ct ON ct.conversation_id=c.id
            JOIN tags t ON t.id=ct.tag_id
            WHERE t.name=?
            ORDER BY c.estimated_pages DESC
        """
        convos = conn.execute(query, (tag_filter,)).fetchall()
        label = tag_filter
    else:
        # All tagged conversations, prioritized by page count
        query = """
            SELECT DISTINCT c.id, c.title, c.source_id, s.name as source_name, c.estimated_pages
            FROM conversations c
            JOIN sources s ON s.id=c.source_id
            JOIN conversation_tags ct ON ct.conversation_id=c.id
            ORDER BY c.estimated_pages DESC
        """
        convos = conn.execute(query).fetchall()
        label = "all_tagged"

    print(f"Exporting {len(convos)} conversations for ChatGPT summarization (tag={label})...")

    batch_num = 0
    files_written = []

    for i in range(0, len(convos), BATCH_SIZE):
        batch = convos[i:i + BATCH_SIZE]
        batch_num += 1
        filename = f"batch_{label}_{batch_num:03d}.md"
        filepath = os.path.join(CHUNKS_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Summarization Batch {batch_num} ({label})\n\n")
            f.write("For each conversation below, provide:\n")
            f.write("- CONV_ID: (the number shown)\n")
            f.write("- SUMMARY: (exactly 3 sentences describing what was discussed and decided)\n")
            f.write("- TAGS: (comma-separated from: game_idea, app_project, educational, alchemy, pkd, mtg, esoteric, coding, personal, other)\n")
            f.write("- IDEA: (if this contains a game/app/edu product idea, describe it in 1 sentence; otherwise \"none\")\n\n")
            f.write("---\n\n")

            for conv_id, title, source_id, source_name, pages in batch:
                # Get excerpt from messages
                msgs = conn.execute(
                    "SELECT role, content FROM messages WHERE conversation_id=? ORDER BY id",
                    (conv_id,),
                ).fetchall()

                excerpt_parts = []
                total_chars = 0
                for role, content in msgs:
                    if not content:
                        continue
                    remaining = EXCERPT_CHARS - total_chars
                    if remaining <= 0:
                        break
                    chunk = content[:remaining]
                    excerpt_parts.append(f"[{role}] {chunk}")
                    total_chars += len(chunk)

                excerpt = "\n".join(excerpt_parts)

                f.write(f"## CONV_ID: {conv_id}\n")
                f.write(f"**Title:** {title}\n")
                f.write(f"**Source:** {source_name} | **Pages:** {pages:.0f}\n\n")
                f.write(f"```\n{excerpt}\n```\n\n---\n\n")

        files_written.append(filepath)

    print(f"Wrote {len(files_written)} batch files to {CHUNKS_DIR}/")
    print(f"  {BATCH_SIZE} conversations per file, {EXCERPT_CHARS} chars excerpt each")
    print(f"  Paste each file into ChatGPT and save the response as response_NNN.md")


def batch_import(response_file, conn):
    """Parse a ChatGPT response file and update conversations in the DB."""
    if not os.path.exists(response_file):
        print(f"ERROR: {response_file} not found")
        sys.exit(1)

    with open(response_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse structured responses — looking for CONV_ID, SUMMARY, TAGS, IDEA blocks
    blocks = re.split(r"(?:^|\n)(?:#+\s*)?CONV_ID:\s*(\d+)", content)

    updated = 0
    ideas_added = 0

    # blocks[0] is preamble, then alternating (id, content) pairs
    for i in range(1, len(blocks) - 1, 2):
        try:
            conv_id = int(blocks[i])
        except ValueError:
            continue
        block_text = blocks[i + 1]

        # Extract SUMMARY
        summary_match = re.search(r"SUMMARY:\s*(.+?)(?:\n(?:TAGS|IDEA)|$)", block_text, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else None

        # Extract TAGS
        tags_match = re.search(r"TAGS:\s*(.+?)(?:\n|$)", block_text)
        tags_str = tags_match.group(1).strip() if tags_match else ""

        # Extract IDEA
        idea_match = re.search(r"IDEA:\s*(.+?)(?:\n|$)", block_text)
        idea_str = idea_match.group(1).strip() if idea_match else ""

        if summary:
            conn.execute("UPDATE conversations SET summary=? WHERE id=?", (summary, conv_id))
            updated += 1

        # Update tags (add LLM-tagged ones with higher confidence)
        if tags_str and tags_str.lower() != "none":
            tag_names = [t.strip().lower().replace(" ", "_") for t in tags_str.split(",")]
            for tag_name in tag_names:
                # Ensure tag exists
                conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
                tag_id_row = conn.execute("SELECT id FROM tags WHERE name=?", (tag_name,)).fetchone()
                if tag_id_row:
                    conn.execute(
                        "INSERT OR REPLACE INTO conversation_tags (conversation_id, tag_id, confidence, method) "
                        "VALUES (?, ?, 0.9, 'llm')",
                        (conv_id, tag_id_row[0]),
                    )

        # Add idea if present
        if idea_str and idea_str.lower() not in ("none", "n/a", ""):
            title = conn.execute("SELECT title FROM conversations WHERE id=?", (conv_id,)).fetchone()
            conn.execute(
                "INSERT INTO ideas (conversation_id, name, description, method, created_at) "
                "VALUES (?, ?, ?, 'llm', datetime('now'))",
                (conv_id, title[0] if title else "Untitled", idea_str),
            )
            ideas_added += 1

    conn.commit()
    print(f"Imported {updated} summaries, {ideas_added} new ideas from {response_file}")


def main():
    parser = argparse.ArgumentParser(description="Megabase Summarizer")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("auto", help="Deterministic auto-summarize using first assistant response")

    exp = sub.add_parser("batch-export", help="Export batch files for ChatGPT summarization")
    exp.add_argument("--tag", help="Only export conversations with this tag")

    imp = sub.add_parser("batch-import", help="Import ChatGPT response file")
    imp.add_argument("file", help="Path to response .md file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    conn = get_db()

    if args.command == "auto":
        auto_summarize(conn)
    elif args.command == "batch-export":
        batch_export(conn, tag_filter=args.tag)
    elif args.command == "batch-import":
        batch_import(args.file, conn)

    conn.close()


if __name__ == "__main__":
    main()
```

---

## Chunker (GPT-ready exports)
**File:** `chunk.py` (7,495 chars)

```py
"""
Megabase Chunker — export conversations as GPT-ready .md chunk files.

Subcommands:
  export <id>        Export a single conversation
  export-tagged <tag> Export all conversations with a given tag
  export-ideas       Export all idea candidates
  list-big           Show conversations over N pages (for choosing what to deep-read)
"""

import os
import sys
import argparse
import sqlite3

from schema import get_db, DB_PATH

CHUNKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chunks", "reading")
PROMPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")

# Target chunk size in chars (~15K tokens for GPT-4)
CHUNK_SIZE = 60000


def load_prompt(prompt_name):
    """Load a prompt template from prompts/ directory."""
    path = os.path.join(PROMPTS_DIR, f"{prompt_name}.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def export_conversation(conn, conv_id, prompt_name="theme_summary"):
    """Export a conversation as chunked .md files."""
    conv = conn.execute(
        "SELECT c.id, c.title, c.created_at, c.estimated_pages, s.name "
        "FROM conversations c JOIN sources s ON s.id=c.source_id WHERE c.id=?",
        (conv_id,),
    ).fetchone()

    if not conv:
        print(f"Conversation {conv_id} not found.")
        return []

    conv_id, title, created, pages, source = conv

    msgs = conn.execute(
        "SELECT role, content, created_at FROM messages WHERE conversation_id=? ORDER BY id",
        (conv_id,),
    ).fetchall()

    if not msgs:
        print(f"No messages in conversation {conv_id}.")
        return []

    # Build full text with role markers
    full_parts = []
    for role, content, ts in msgs:
        if not content:
            continue
        header = f"[{role.upper()}]"
        if ts:
            header += f" ({ts[:10]})"
        full_parts.append(f"{header}\n{content}")

    full_text = "\n\n---\n\n".join(full_parts)

    # Load prompt template
    prompt = load_prompt(prompt_name)

    # Create output directory
    safe_title = "".join(c for c in title[:60] if c.isalnum() or c in " -_").strip()
    conv_dir = os.path.join(CHUNKS_DIR, f"{conv_id}_{safe_title}")
    os.makedirs(conv_dir, exist_ok=True)

    # Split into chunks at message boundaries
    chunks = []
    current_chunk = []
    current_size = 0

    for part in full_parts:
        part_len = len(part)
        if current_size + part_len > CHUNK_SIZE and current_chunk:
            chunks.append("\n\n---\n\n".join(current_chunk))
            current_chunk = [part]
            current_size = part_len
        else:
            current_chunk.append(part)
            current_size += part_len

    if current_chunk:
        chunks.append("\n\n---\n\n".join(current_chunk))

    total_chunks = len(chunks)
    files = []

    for i, chunk_text in enumerate(chunks):
        chunk_num = i + 1
        filename = f"chunk_{chunk_num:02d}.md"
        filepath = os.path.join(conv_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(f"**Source:** {source} | **Date:** {created or 'unknown'} | ")
            f.write(f"**Pages:** {pages:.0f} | **Chunk {chunk_num}/{total_chunks}**\n\n")

            if prompt and chunk_num == 1:
                f.write(f"## Analysis Prompt\n\n{prompt}\n\n")

            f.write(f"---\n\n")
            f.write(chunk_text)

            if chunk_num < total_chunks:
                f.write(f"\n\n---\n\n*Continue to chunk_{chunk_num+1:02d}.md for more.*\n")

        files.append(filepath)

    # Record in DB
    for i, fp in enumerate(files):
        conn.execute(
            "INSERT INTO chunk_exports (conversation_id, chunk_number, file_path, char_count, exported_at) "
            "VALUES (?, ?, ?, ?, datetime('now'))",
            (conv_id, i + 1, fp, os.path.getsize(fp)),
        )
    conn.commit()

    print(f"  [{conv_id}] {title}: {total_chunks} chunks ({pages:.0f} pages)")
    return files


def list_big(conn, min_pages=50, tag=None):
    """List conversations over a threshold, optionally filtered by tag."""
    if tag:
        rows = conn.execute("""
            SELECT c.id, c.title, s.name, c.estimated_pages, c.message_count
            FROM conversations c
            JOIN sources s ON s.id=c.source_id
            JOIN conversation_tags ct ON ct.conversation_id=c.id
            JOIN tags t ON t.id=ct.tag_id
            WHERE t.name=? AND c.estimated_pages >= ?
            ORDER BY c.estimated_pages DESC
        """, (tag, min_pages)).fetchall()
    else:
        rows = conn.execute("""
            SELECT c.id, c.title, s.name, c.estimated_pages, c.message_count
            FROM conversations c JOIN sources s ON s.id=c.source_id
            WHERE c.estimated_pages >= ?
            ORDER BY c.estimated_pages DESC
        """, (min_pages,)).fetchall()

    print(f"\n{'ID':>6} {'Pages':>6} {'Msgs':>6} {'Source':<15} Title")
    print("-" * 80)
    for cid, title, source, pages, msgs in rows:
        t = (title or "")[:45]
        print(f"{cid:>6} {pages:>6.0f} {msgs:>6} {source:<15} {t}")
    print(f"\n{len(rows)} conversations over {min_pages} pages")


def main():
    parser = argparse.ArgumentParser(description="Megabase Chunker")
    sub = parser.add_subparsers(dest="command")

    exp = sub.add_parser("export", help="Export a single conversation")
    exp.add_argument("id", type=int, help="Conversation ID")
    exp.add_argument("--prompt", default="theme_summary", help="Prompt template name")

    expt = sub.add_parser("export-tagged", help="Export all conversations with a tag")
    expt.add_argument("tag", help="Tag name")
    expt.add_argument("--min-pages", type=float, default=10, help="Minimum pages to export")
    expt.add_argument("--prompt", default="theme_summary", help="Prompt template name")

    sub.add_parser("export-ideas", help="Export all idea candidates")

    lb = sub.add_parser("list-big", help="List big conversations")
    lb.add_argument("--min-pages", type=float, default=50, help="Minimum page threshold")
    lb.add_argument("--tag", help="Filter by tag")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    conn = get_db()

    if args.command == "export":
        export_conversation(conn, args.id, args.prompt)

    elif args.command == "export-tagged":
        rows = conn.execute("""
            SELECT c.id FROM conversations c
            JOIN conversation_tags ct ON ct.conversation_id=c.id
            JOIN tags t ON t.id=ct.tag_id
            WHERE t.name=? AND c.estimated_pages >= ?
            ORDER BY c.estimated_pages DESC
        """, (args.tag, args.min_pages)).fetchall()
        print(f"Exporting {len(rows)} conversations tagged '{args.tag}' (>={args.min_pages} pages)...")
        for (cid,) in rows:
            export_conversation(conn, cid, args.prompt)

    elif args.command == "export-ideas":
        rows = conn.execute("""
            SELECT DISTINCT conversation_id FROM ideas ORDER BY conversation_id
        """).fetchall()
        print(f"Exporting {len(rows)} idea conversations...")
        for (cid,) in rows:
            export_conversation(conn, cid, "idea_extraction")

    elif args.command == "list-big":
        list_big(conn, min_pages=args.min_pages, tag=getattr(args, 'tag', None))

    conn.close()


if __name__ == "__main__":
    main()
```

---

## Showcase Batch Chunk Generator
**File:** `showcase_chunks.py` (7,594 chars)

```py
"""
Dreambase — Showcase Batch Chunk Generator.
Produces paste-ready .md files for ChatGPT reading sessions.
Each file contains conversation excerpts + a structured extraction prompt.

Usage:
    python showcase_chunks.py                  # Generate all 3 showcases
    python showcase_chunks.py bubble-bog-witch # Generate one showcase

Output: chunks/showcases/<slug>/batch_001.md, batch_002.md, ...
"""

import os
import sqlite3
import sys
from schema import DB_PATH

CHUNK_SIZE = 50000  # ~12.5K tokens per batch — leaves room for prompt + response

# Same showcase definitions as app.py (design conversations only, no code dumps)
SHOWCASES = {
    "bubble-bog-witch": {
        "title": "Bubble Bog Witch",
        "conversation_ids": [40, 239, 3580, 2565],
    },
    "dungeon-autobattler": {
        "title": "Dungeon Autobattler",
        "conversation_ids": [4, 10, 37, 7, 2580, 2578, 2591, 2564, 2582, 2668, 2577, 3594],
    },
    "alchemy-board-game": {
        "title": "Alchemy Board Game",
        # Design conversations only — skip the 662pg Code Fix session (id=566)
        "conversation_ids": [567, 851, 2700, 347, 500, 531, 533, 511, 513, 2523, 2515],
    },
}

EXTRACTION_PROMPT = """You are reading conversations from a personal knowledge archaeology project called Dreambase.
These conversations are about the game concept: {title}.

For this batch, please extract:

1. **NARRATIVE** (3-5 paragraphs): Tell the story of this game idea — what is it, what makes it
   interesting, how did the design evolve across conversations? Write in third person present
   ("Ted explores..." not "I wanted to..."). Tone: intellectual but accessible, curious not pretentious.

2. **TIMELINE** (one entry per conversation in this batch):
   - DATE: (from conversation metadata)
   - TITLE: (conversation title)
   - DESCRIPTION: (1-2 sentences — what happened in this conversation, what design decisions were made)

3. **QUOTES** (3-5 best moments — lines that capture the creative energy):
   - QUOTE: (exact text, max 50 words)
   - ROLE: (user or assistant)
   - CONVERSATION: (which conversation it came from)

4. **DESIGN INSIGHTS** (2-3 key design decisions or innovations):
   - What mechanic or idea emerged?
   - Why is it interesting from a game design perspective?

5. **VISUAL THEMES** (for future illustration):
   - What visual imagery does this conversation suggest?
   - What art style would fit?

Format your response as clean markdown with these exact headers.
---

"""


def get_conversation_text(conn, conv_id, max_chars=None):
    """Extract conversation as readable text."""
    conv = conn.execute("""
        SELECT c.title, c.created_at, c.estimated_pages, s.name as source
        FROM conversations c JOIN sources s ON s.id=c.source_id
        WHERE c.id=?
    """, (conv_id,)).fetchone()

    if not conv:
        return "", ""

    header = f"## {conv[0]}\n**Source:** {conv[3]} | **Date:** {(conv[1] or 'unknown')[:10]} | **Pages:** {conv[2]:.0f}\n\n"

    messages = conn.execute("""
        SELECT role, content FROM messages
        WHERE conversation_id=? ORDER BY id
    """, (conv_id,)).fetchall()

    lines = []
    char_count = 0
    for msg in messages:
        role = (msg[0] or "unknown").upper()
        content = msg[1] or ""
        # Truncate very long assistant messages (likely code output)
        if len(content) > 8000 and role == "ASSISTANT":
            content = content[:4000] + "\n\n[... truncated — full message is " + str(len(content)) + " chars ...]\n\n" + content[-2000:]
        line = f"**{role}:** {content}\n\n"
        if max_chars and char_count + len(line) > max_chars:
            lines.append(f"\n[... remaining messages truncated at {max_chars} chars ...]\n")
            break
        lines.append(line)
        char_count += len(line)

    return header, "".join(lines)


def generate_chunks(slug):
    """Generate batch chunk files for a showcase."""
    sc = SHOWCASES.get(slug)
    if not sc:
        print(f"Unknown showcase: {slug}")
        return

    conn = sqlite3.connect(DB_PATH)
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "chunks", "showcases", slug)
    os.makedirs(out_dir, exist_ok=True)

    # Gather all conversation texts
    conv_texts = []
    for conv_id in sc["conversation_ids"]:
        header, body = get_conversation_text(conn, conv_id)
        if body:
            conv_texts.append((conv_id, header, body))

    conn.close()

    # Pack into batches respecting CHUNK_SIZE
    batch_num = 1
    current_batch = []
    current_size = 0
    prompt_size = len(EXTRACTION_PROMPT.format(title=sc["title"]))

    for conv_id, header, body in conv_texts:
        entry_size = len(header) + len(body)

        # If this single conversation exceeds chunk size, give it its own batch
        if entry_size > CHUNK_SIZE:
            # Flush current batch first
            if current_batch:
                write_batch(out_dir, batch_num, sc["title"], current_batch, prompt_size)
                batch_num += 1
                current_batch = []
                current_size = 0

            # Write oversized conversation as its own batch (truncated)
            truncated_body = body[:CHUNK_SIZE - len(header) - prompt_size - 500]
            truncated_body += f"\n\n[... truncated to fit batch. Full conversation is {entry_size} chars ...]\n"
            write_batch(out_dir, batch_num, sc["title"],
                       [(conv_id, header, truncated_body)], prompt_size)
            batch_num += 1
            continue

        # Would adding this overflow the batch?
        if current_size + entry_size > CHUNK_SIZE - prompt_size:
            write_batch(out_dir, batch_num, sc["title"], current_batch, prompt_size)
            batch_num += 1
            current_batch = []
            current_size = 0

        current_batch.append((conv_id, header, body))
        current_size += entry_size

    # Final batch
    if current_batch:
        write_batch(out_dir, batch_num, sc["title"], current_batch, prompt_size)
        batch_num += 1

    total = batch_num - 1
    print(f"  {sc['title']}: {total} batch files in {out_dir}")
    return total


def write_batch(out_dir, batch_num, title, entries, prompt_size):
    """Write a single batch file."""
    filename = f"batch_{batch_num:03d}.md"
    filepath = os.path.join(out_dir, filename)

    total_chars = sum(len(h) + len(b) for _, h, b in entries)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {title} — Batch {batch_num}\n")
        f.write(f"**Conversations in this batch:** {len(entries)} | **~{total_chars:,} chars**\n\n")
        f.write(EXTRACTION_PROMPT.format(title=title))

        for conv_id, header, body in entries:
            f.write(f"---\n\n")
            f.write(header)
            f.write(body)
            f.write("\n")

    print(f"    {filename}: {len(entries)} conversations, {total_chars:,} chars")


if __name__ == "__main__":
    slugs = sys.argv[1:] if len(sys.argv) > 1 else list(SHOWCASES.keys())

    print("Dreambase Showcase Chunk Generator")
    print("=" * 40)
    total_batches = 0
    for slug in slugs:
        if slug in SHOWCASES:
            n = generate_chunks(slug)
            if n:
                total_batches += n
        else:
            print(f"Unknown showcase: {slug}")

    print(f"\nTotal: {total_batches} batch files ready for ChatGPT reading sessions.")
    print("Workflow: paste each batch into ChatGPT, copy structured response,")
    print("save as chunks/showcases/<slug>/response_NNN.md")
```

---

## Verification Queries
**File:** `verify.py` (2,839 chars)

```py
"""
Megabase verification script. Run after any ingestion to check data integrity.
"""

import sqlite3
import sys
from schema import DB_PATH


def verify(db_path=None):
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)

    print("=== MEGABASE VERIFICATION ===\n")

    # Source counts
    rows = conn.execute("""
        SELECT s.name, count(c.id) as convos,
               COALESCE(sum(c.message_count),0) as msgs,
               round(COALESCE(sum(c.char_count),0)/1000000.0, 1) as text_MB
        FROM sources s LEFT JOIN conversations c ON c.source_id=s.id
        GROUP BY s.name ORDER BY msgs DESC
    """).fetchall()

    print(f"{'Source':<20} {'Convos':>8} {'Messages':>10} {'Text MB':>8}")
    print("-" * 50)
    total_c, total_m = 0, 0
    for name, convos, msgs, mb in rows:
        print(f"{name:<20} {convos:>8} {msgs:>10} {mb:>8}")
        total_c += convos
        total_m += msgs
    print("-" * 50)
    print(f"{'TOTAL':<20} {total_c:>8} {total_m:>10}")

    # Orphan check
    orphan_msgs = conn.execute(
        "SELECT count(*) FROM messages WHERE conversation_id NOT IN (SELECT id FROM conversations)"
    ).fetchone()[0]
    orphan_convos = conn.execute(
        "SELECT count(*) FROM conversations WHERE source_id NOT IN (SELECT id FROM sources)"
    ).fetchone()[0]

    print(f"\nOrphan messages: {orphan_msgs}")
    print(f"Orphan conversations: {orphan_convos}")

    # Conversations with no messages
    empty = conn.execute(
        "SELECT count(*) FROM conversations WHERE message_count = 0 OR message_count IS NULL"
    ).fetchone()[0]
    print(f"Empty conversations (0 messages): {empty}")

    # Stats check
    no_stats = conn.execute(
        "SELECT count(*) FROM conversations WHERE char_count IS NULL OR char_count = 0"
    ).fetchone()[0]
    print(f"Conversations missing char_count: {no_stats}")

    # DB file size
    import os
    size_mb = os.path.getsize(path) / (1024 * 1024)
    print(f"\nDatabase size: {size_mb:.0f} MB")

    # Summary coverage
    with_summary = conn.execute("SELECT count(*) FROM conversations WHERE summary IS NOT NULL AND summary != ''").fetchone()[0]
    print(f"Conversations with summaries: {with_summary}/{total_c}")

    # Tag coverage
    tagged = conn.execute("SELECT count(DISTINCT conversation_id) FROM conversation_tags").fetchone()[0]
    print(f"Conversations with tags: {tagged}/{total_c}")

    # FTS check
    try:
        conn.execute("SELECT count(*) FROM messages_fts").fetchone()
        print("FTS5 index: EXISTS")
    except Exception:
        print("FTS5 index: NOT YET BUILT")

    conn.close()

    if orphan_msgs > 0 or orphan_convos > 0:
        print("\n*** WARNING: Orphaned records detected! ***")
        return 1
    print("\n=== ALL CHECKS PASSED ===")
    return 0


if __name__ == "__main__":
    sys.exit(verify())
```

---

## ChatGPT JSON Ingestor
**File:** `ingest_chatgpt_json.py` (4,485 chars)

```py
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
```

---

## HTML Chat Ingestor
**File:** `ingest_html_chats.py` (7,762 chars)

```py
"""
Ingest LLM chat HTML files from Downloads/LLM logs into the megabase.
Handles two HTML variants:
  - Old: .msg divs with .role child divs (from build_chats.py)
  - New: .msg divs with .bubble child divs (from newer export)
Skips non-chat HTML files (game artifacts, dashboards, etc.) by checking for .msg elements.
"""

import os
import sys
import re
import logging
from datetime import datetime
from html.parser import HTMLParser

from schema import get_db, create_db, register_source, update_conversation_stats

logger = logging.getLogger("ingest_html")

DEFAULT_SRC = os.path.expanduser("~/Downloads/LLM logs")

# Roles we recognize
KNOWN_ROLES = {"user", "assistant", "system", "tool"}


class ChatHTMLParser(HTMLParser):
    """Lightweight parser that extracts title, meta, and messages from chat HTML."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_text = ""
        self.messages = []  # list of (role, text)

        # State tracking
        self._in_title = False
        self._in_meta = False
        self._in_msg = False
        self._in_role_div = False
        self._in_bubble = False
        self._current_role = None
        self._current_text = []
        self._tag_stack = []
        self._is_chat = False  # True if we found at least one .msg element

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        classes = attrs_dict.get("class", "").split()

        if tag == "title":
            self._in_title = True
            return

        # Detect .meta div
        if tag == "div" and "meta" in classes:
            self._in_meta = True
            return

        # Detect .msg div — extract role from class
        if tag == "div" and "msg" in classes:
            self._is_chat = True
            role = None
            for c in classes:
                if c in KNOWN_ROLES:
                    role = c
                    break
            self._in_msg = True
            self._current_role = role
            self._current_text = []
            return

        # Detect .role div (skip its text — it's just a label like "You" or "ChatGPT")
        if tag == "div" and "role" in classes and self._in_msg:
            self._in_role_div = True
            return

        # Detect .bubble div inside a .msg
        if tag == "div" and "bubble" in classes and self._in_msg:
            self._in_bubble = True
            return

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
            return

        if tag == "div" and self._in_meta:
            self._in_meta = False
            return

        if tag == "div" and self._in_role_div:
            self._in_role_div = False
            return

        if tag == "div" and self._in_bubble:
            self._in_bubble = False
            return

        # End of .msg div — save the message
        if tag == "div" and self._in_msg:
            text = "".join(self._current_text).strip()
            if text and self._current_role:
                self.messages.append((self._current_role, text))
            self._in_msg = False
            self._current_role = None
            self._current_text = []
            return

    def handle_data(self, data):
        if self._in_title:
            self.title += data
            return

        if self._in_meta:
            self.meta_text += data
            return

        # Skip role label text
        if self._in_role_div:
            return

        # Collect message text (from either direct .msg content or .bubble content)
        if self._in_msg:
            self._current_text.append(data)


def parse_meta_date(meta_text):
    """Extract date from meta text like 'Created: January 09, 2025 09:24 PM' or 'January 09, 2025 09:24 PM · Model: gpt-4o'."""
    # Try various date patterns
    patterns = [
        r"(?:Created:\s*)?(\w+ \d{1,2}, \d{4} \d{1,2}:\d{2} [AP]M)",
        r"(\d{4}-\d{2}-\d{2})",
    ]
    for pat in patterns:
        m = re.search(pat, meta_text)
        if m:
            date_str = m.group(1)
            for fmt in ("%B %d, %Y %I:%M %p", "%Y-%m-%d"):
                try:
                    return datetime.strptime(date_str, fmt).isoformat()
                except ValueError:
                    continue
    return None


def extract_date_from_path(filepath):
    """Try to extract a date from directory names like '2025-01-09_Title'."""
    parts = filepath.replace("\\", "/").split("/")
    for part in parts:
        m = re.match(r"(\d{4}-\d{2}-\d{2})", part)
        if m:
            return m.group(1) + "T00:00:00"
    return None


def ingest(src_path=None, db_path=None):
    src = src_path or DEFAULT_SRC
    if not os.path.isdir(src):
        print(f"ERROR: {src} not found")
        sys.exit(1)

    conn = get_db(db_path)
    create_db(db_path)
    conn = get_db(db_path)

    source_id = register_source(conn, "llm_logs_html", src)

    # Clear previous data for this source
    existing = conn.execute(
        "SELECT id FROM conversations WHERE source_id=?", (source_id,)
    ).fetchall()
    if existing:
        ids = [r[0] for r in existing]
        placeholders = ",".join("?" * len(ids))
        conn.execute(f"DELETE FROM messages WHERE conversation_id IN ({placeholders})", ids)
        conn.execute(f"DELETE FROM conversations WHERE id IN ({placeholders})", ids)
        conn.commit()
        print(f"Cleared {len(ids)} previous HTML conversations.")

    # Find all HTML files
    html_files = []
    for root, dirs, files in os.walk(src):
        for f in files:
            if f.endswith(".html"):
                html_files.append(os.path.join(root, f))

    print(f"Found {len(html_files)} HTML files.")

    total_convos = 0
    total_msgs = 0
    skipped = 0

    for i, filepath in enumerate(html_files):
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Failed to read {filepath}: {e}")
            continue

        parser = ChatHTMLParser()
        try:
            parser.feed(content)
        except Exception as e:
            logger.warning(f"Failed to parse {filepath}: {e}")
            continue

        # Skip non-chat HTML files
        if not parser._is_chat or not parser.messages:
            skipped += 1
            continue

        title = parser.title.strip() or os.path.splitext(os.path.basename(filepath))[0]
        created = parse_meta_date(parser.meta_text) or extract_date_from_path(filepath)

        # Use relative path from source as external_id
        rel_path = os.path.relpath(filepath, src)
        # Get the parent folder name as context
        folder = os.path.dirname(rel_path)

        cur = conn.execute(
            "INSERT INTO conversations (source_id, external_id, title, created_at, folder_path) "
            "VALUES (?, ?, ?, ?, ?)",
            (source_id, rel_path, title, created, folder),
        )
        conv_id = cur.lastrowid

        for role, text in parser.messages:
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, char_count) "
                "VALUES (?, ?, ?, ?)",
                (conv_id, role, text, len(text)),
            )
            total_msgs += 1

        update_conversation_stats(conn, conv_id)
        total_convos += 1

        if (i + 1) % 200 == 0:
            conn.commit()

    conn.commit()
    conn.close()

    print(f"Ingested {total_convos} conversations, {total_msgs} messages from HTML chats.")
    print(f"Skipped {skipped} non-chat HTML files.")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else None
    ingest(src_path=src)
```

---

## PDF Chat Ingestor
**File:** `ingest_pdf_chats.py` (5,224 chars)

```py
"""
Ingest LLM chat PDFs from Downloads/LLM logs into the megabase.
Uses PyMuPDF (fitz) to extract text. Treats entire PDF as a single conversation
with the full text as one message, since PDF chat exports don't preserve
message boundaries reliably.
"""

import os
import sys
import re
import logging
from datetime import datetime

import fitz  # PyMuPDF

from schema import get_db, create_db, register_source, update_conversation_stats

logger = logging.getLogger("ingest_pdf")

DEFAULT_SRC = os.path.expanduser("~/Downloads/LLM logs")

# Minimum text length to consider a PDF as containing chat content
MIN_TEXT_LEN = 200


def extract_pdf_text(filepath):
    """Extract all text from a PDF, page by page."""
    try:
        doc = fitz.open(filepath)
        pages = []
        for page in doc:
            text = page.get_text()
            if text.strip():
                pages.append(text)
        doc.close()
        return "\n\n".join(pages)
    except Exception as e:
        logger.warning(f"Failed to extract {filepath}: {e}")
        return ""


def extract_date_from_path(filepath):
    """Try to extract a date from directory or file names."""
    parts = filepath.replace("\\", "/").split("/")
    for part in parts:
        m = re.match(r"(\d{4}-\d{2}-\d{2})", part)
        if m:
            return m.group(1) + "T00:00:00"
    return None


def split_messages(text):
    """Attempt to split PDF text into user/assistant turns.
    Look for patterns like 'You said:', 'ChatGPT said:', or role headers."""
    # Try to split on common ChatGPT PDF export patterns
    patterns = [
        r'\n(?:You|User)\s*(?:said)?:\s*\n',
        r'\n(?:ChatGPT|Assistant|GPT-4|Claude)\s*(?:said)?:\s*\n',
    ]

    # Check if the text has these markers
    has_markers = False
    for pat in patterns:
        if re.search(pat, text):
            has_markers = True
            break

    if not has_markers:
        # No clear message boundaries — return as single assistant message
        return [("assistant", text)]

    # Split on role markers
    parts = re.split(r'\n((?:You|User|ChatGPT|Assistant|GPT-4|Claude)\s*(?:said)?:)\s*\n', text)
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
            if part:
                messages.append((current_role, part))

    return messages if messages else [("assistant", text)]


def ingest(src_path=None, db_path=None):
    src = src_path or DEFAULT_SRC
    if not os.path.isdir(src):
        print(f"ERROR: {src} not found")
        sys.exit(1)

    conn = get_db(db_path)
    create_db(db_path)
    conn = get_db(db_path)

    source_id = register_source(conn, "llm_logs_pdf", src)

    # Clear previous data for this source
    existing = conn.execute(
        "SELECT id FROM conversations WHERE source_id=?", (source_id,)
    ).fetchall()
    if existing:
        ids = [r[0] for r in existing]
        placeholders = ",".join("?" * len(ids))
        conn.execute(f"DELETE FROM messages WHERE conversation_id IN ({placeholders})", ids)
        conn.execute(f"DELETE FROM conversations WHERE id IN ({placeholders})", ids)
        conn.commit()
        print(f"Cleared {len(ids)} previous PDF conversations.")

    # Find all PDF files
    pdf_files = []
    for root, dirs, files in os.walk(src):
        for f in files:
            if f.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, f))

    print(f"Found {len(pdf_files)} PDF files.")

    total_convos = 0
    total_msgs = 0
    skipped = 0

    for i, filepath in enumerate(pdf_files):
        text = extract_pdf_text(filepath)
        if len(text) < MIN_TEXT_LEN:
            skipped += 1
            continue

        title = os.path.splitext(os.path.basename(filepath))[0]
        created = extract_date_from_path(filepath)
        rel_path = os.path.relpath(filepath, src)
        folder = os.path.dirname(rel_path)

        cur = conn.execute(
            "INSERT INTO conversations (source_id, external_id, title, created_at, folder_path) "
            "VALUES (?, ?, ?, ?, ?)",
            (source_id, rel_path, title, created, folder),
        )
        conv_id = cur.lastrowid

        messages = split_messages(text)
        for role, msg_text in messages:
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, char_count) "
                "VALUES (?, ?, ?, ?)",
                (conv_id, role, msg_text, len(msg_text)),
            )
            total_msgs += 1

        update_conversation_stats(conn, conv_id)
        total_convos += 1

        if (i + 1) % 100 == 0:
            conn.commit()

    conn.commit()
    conn.close()

    print(f"Ingested {total_convos} conversations, {total_msgs} messages from PDF chats.")
    print(f"Skipped {skipped} PDFs (too short or unreadable).")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else None
    ingest(src_path=src)
```

---

## Claude DB Ingestor
**File:** `ingest_claude_db.py` (2,802 chars)

```py
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
```

---

## Facebook JSON Ingestor
**File:** `ingest_facebook_json.py` (5,382 chars)

```py
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
```

---

## Google Chat Ingestor
**File:** `ingest_google_chat.py` (4,935 chars)

```py
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
```

---

## Gmail Mbox Ingestor
**File:** `ingest_gmail_mbox.py` (7,210 chars)

```py
"""
Ingest Gmail from mbox file into the megabase.
Phase 1: Parse headers only (sender, recipient, date, subject) — fast, ~14 GB streamed.
Phase 2: Extract bodies for personal contacts only (skip marketing/spam).

Uses Python stdlib mailbox module for streaming without loading entire file.
"""

import os
import sys
import mailbox
import email.utils
import email.header
import logging
import re
from datetime import datetime

from schema import get_db, create_db, register_source, update_conversation_stats

logger = logging.getLogger("ingest_gmail")

DEFAULT_SRC = os.path.expanduser("~/Downloads/All mail Including Spam and Trash-002 (1).mbox")

# Domains to skip (marketing, automated, no-reply)
SKIP_DOMAINS = {
    "noreply", "no-reply", "notifications", "notify", "mailer", "updates",
    "newsletter", "marketing", "promo", "alerts", "donotreply", "automated",
    "support", "info", "billing", "accounts", "security",
}

SKIP_SENDER_PATTERNS = re.compile(
    r"(noreply|no-reply|notifications?|newsletter|marketing|promo|automated|"
    r"mailer-daemon|postmaster|bounce|unsubscribe)",
    re.IGNORECASE,
)


def decode_header(raw):
    """Decode an email header value."""
    if not raw:
        return ""
    decoded_parts = email.header.decode_header(raw)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            try:
                result.append(part.decode(charset or "utf-8", errors="replace"))
            except (LookupError, UnicodeDecodeError):
                result.append(part.decode("utf-8", errors="replace"))
        else:
            result.append(part)
    return " ".join(result)


def parse_email_date(date_str):
    """Parse email date header to ISO format."""
    if not date_str:
        return None
    try:
        parsed = email.utils.parsedate_to_datetime(date_str)
        return parsed.isoformat()
    except Exception:
        return None


def is_personal(from_addr):
    """Check if an email address looks personal (not automated/marketing)."""
    if not from_addr:
        return False
    addr = from_addr.lower()
    # Check local part against skip patterns
    if SKIP_SENDER_PATTERNS.search(addr):
        return False
    # Check if local part matches common automated prefixes
    local = addr.split("@")[0] if "@" in addr else addr
    if local in SKIP_DOMAINS:
        return False
    return True


def get_body(msg):
    """Extract plain text body from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
        # Fallback to HTML if no plain text
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    text = payload.decode(charset, errors="replace")
                    # Strip HTML tags crudely
                    text = re.sub(r"<[^>]+>", " ", text)
                    text = re.sub(r"\s+", " ", text).strip()
                    return text
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            return payload.decode(charset, errors="replace")
    return ""


def ingest(src_path=None, db_path=None, headers_only=False):
    src = src_path or DEFAULT_SRC
    if not os.path.exists(src):
        print(f"ERROR: {src} not found")
        sys.exit(1)

    print(f"Opening mbox: {src}")
    print(f"Mode: {'headers only' if headers_only else 'full (personal contacts)'}")

    conn = get_db(db_path)
    create_db(db_path)
    conn = get_db(db_path)

    source_id = register_source(conn, "gmail", src)

    # Clear previous
    existing = conn.execute("SELECT id FROM conversations WHERE source_id=?", (source_id,)).fetchall()
    if existing:
        ids = [r[0] for r in existing]
        ph = ",".join("?" * len(ids))
        conn.execute(f"DELETE FROM messages WHERE conversation_id IN ({ph})", ids)
        conn.execute(f"DELETE FROM conversations WHERE id IN ({ph})", ids)
        conn.commit()

    mbox = mailbox.mbox(src)
    total = 0
    ingested = 0
    skipped_automated = 0

    for key in mbox.iterkeys():
        total += 1
        if total % 5000 == 0:
            conn.commit()
            print(f"  Processed {total} emails, ingested {ingested}...")

        try:
            msg = mbox[key]
        except Exception as e:
            logger.warning(f"Failed to read message {key}: {e}")
            continue

        from_raw = msg.get("From", "")
        to_raw = msg.get("To", "")
        subject = decode_header(msg.get("Subject", ""))
        date_str = msg.get("Date", "")
        message_id = msg.get("Message-ID", str(key))

        # Parse sender
        from_name, from_addr = email.utils.parseaddr(from_raw)
        from_name = decode_header(from_name) if from_name else from_addr

        # Skip automated/marketing emails
        if not is_personal(from_addr):
            skipped_automated += 1
            continue

        created = parse_email_date(date_str)

        # Determine role
        is_sent = from_addr and "ted.hand" in from_addr.lower()
        role = "user" if is_sent else "sender"

        # Get body if not headers-only mode
        body = ""
        if not headers_only:
            body = get_body(msg)

        # Create as individual conversation (one email = one conversation)
        # Thread grouping could be done later via subject/In-Reply-To
        display_title = subject or "(no subject)"
        if not is_sent:
            display_title = f"Email from {from_name}: {display_title}"

        cur = conn.execute(
            "INSERT INTO conversations (source_id, external_id, title, created_at) "
            "VALUES (?, ?, ?, ?)",
            (source_id, message_id, display_title, created),
        )
        conv_id = cur.lastrowid

        # Store the email content
        content = body if body else f"[Subject: {subject}] From: {from_name}"
        conn.execute(
            "INSERT INTO messages (conversation_id, role, content, created_at, char_count) "
            "VALUES (?, ?, ?, ?, ?)",
            (conv_id, role, content, created, len(content)),
        )

        update_conversation_stats(conn, conv_id)
        ingested += 1

    conn.commit()
    mbox.close()
    conn.close()
    print(f"Processed {total} emails total.")
    print(f"Ingested {ingested} personal emails, skipped {skipped_automated} automated/marketing.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("src", nargs="?", help="Path to mbox file")
    parser.add_argument("--headers-only", action="store_true", help="Only parse headers, skip bodies")
    args = parser.parse_args()
    ingest(src_path=args.src, headers_only=args.headers_only)
```

---

## PKD Chats Ingestor
**File:** `ingest_pkd_chats.py` (4,468 chars)

```py
"""
Ingest PKD chat HTML files from Desktop/pkd chats into the megabase.
Standalone parser to avoid source conflicts with ingest_html_chats.py.
"""

import os
import sys
import re
import logging
from html.parser import HTMLParser

from schema import get_db, create_db, register_source, update_conversation_stats

logger = logging.getLogger("ingest_pkd")

DEFAULT_SRC = "C:/Users/PC/Desktop/pkd chats"
KNOWN_ROLES = {"user", "assistant", "system", "tool"}


class ChatHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.messages = []
        self._in_title = False
        self._in_msg = False
        self._in_role_div = False
        self._current_role = None
        self._current_text = []
        self._is_chat = False

    def handle_starttag(self, tag, attrs):
        classes = dict(attrs).get("class", "").split()
        if tag == "title":
            self._in_title = True
        elif tag == "div" and "msg" in classes:
            self._is_chat = True
            self._in_msg = True
            self._current_role = next((c for c in classes if c in KNOWN_ROLES), None)
            self._current_text = []
        elif tag == "div" and "role" in classes and self._in_msg:
            self._in_role_div = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "div" and self._in_role_div:
            self._in_role_div = False
        elif tag == "div" and self._in_msg:
            text = "".join(self._current_text).strip()
            if text and self._current_role:
                self.messages.append((self._current_role, text))
            self._in_msg = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif self._in_role_div:
            return
        elif self._in_msg:
            self._current_text.append(data)


def ingest(src_path=None, db_path=None):
    src = src_path or DEFAULT_SRC
    if not os.path.isdir(src):
        print(f"ERROR: {src} not found")
        sys.exit(1)

    conn = get_db(db_path)
    create_db(db_path)
    conn = get_db(db_path)

    source_id = register_source(conn, "pkd_chats", src)

    existing = conn.execute("SELECT id FROM conversations WHERE source_id=?", (source_id,)).fetchall()
    if existing:
        ids = [r[0] for r in existing]
        ph = ",".join("?" * len(ids))
        conn.execute(f"DELETE FROM messages WHERE conversation_id IN ({ph})", ids)
        conn.execute(f"DELETE FROM conversations WHERE id IN ({ph})", ids)
        conn.commit()

    html_files = []
    for root, dirs, files in os.walk(src):
        for f in files:
            if f.endswith(".html"):
                html_files.append(os.path.join(root, f))

    print(f"Found {len(html_files)} PKD chat HTML files.")
    total_convos = 0
    total_msgs = 0

    for filepath in html_files:
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Failed to read {filepath}: {e}")
            continue

        parser = ChatHTMLParser()
        try:
            parser.feed(content)
        except Exception:
            continue

        if not parser._is_chat or not parser.messages:
            continue

        title = parser.title.strip() or os.path.basename(os.path.dirname(filepath))
        rel_path = os.path.relpath(filepath, src)
        created = None
        m = re.match(r"(\d{4}-\d{2}-\d{2})", os.path.basename(os.path.dirname(filepath)))
        if m:
            created = m.group(1) + "T00:00:00"

        cur = conn.execute(
            "INSERT INTO conversations (source_id, external_id, title, created_at, folder_path) "
            "VALUES (?, ?, ?, ?, ?)",
            (source_id, rel_path, title, created, os.path.dirname(filepath)),
        )
        conv_id = cur.lastrowid

        for role, text in parser.messages:
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content, char_count) VALUES (?, ?, ?, ?)",
                (conv_id, role, text, len(text)),
            )
            total_msgs += 1

        update_conversation_stats(conn, conv_id)
        total_convos += 1

    conn.commit()
    conn.close()
    print(f"Ingested {total_convos} conversations, {total_msgs} messages from PKD chats.")


if __name__ == "__main__":
    ingest()
```

---

## SMS + Twitter Ingestor
**File:** `ingest_sms_twitter.py` (5,694 chars)

```py
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
```

---

## Browse Page Template
**File:** `templates/index.html` (3,207 chars)

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dreambase — Haunt Your Own Records</title>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<header>
  <h1><a href="/">Dreambase</a></h1>
  <nav>
    <a href="/">Browse</a>
    <a href="/viz">Viz</a>
    <a href="/ideas">Ideas ({{ total }})</a>
    <a href="/showcases">Showcases</a>
  </nav>
</header>

<div class="controls">
  <form method="get" class="search-form">
    <input type="text" name="q" value="{{ q }}" placeholder="Full-text search across all messages..." class="search-input">
    <select name="source">
      <option value="">All sources</option>
      {% for s in sources %}
      <option value="{{ s.name }}" {{ 'selected' if source == s.name }}>{{ s.name }}</option>
      {% endfor %}
    </select>
    <select name="tag">
      <option value="">All tags</option>
      {% for t in tags %}
      <option value="{{ t.name }}" {{ 'selected' if tag == t.name }}>{{ t.name }} ({{ t.cnt }})</option>
      {% endfor %}
    </select>
    <select name="sort">
      <option value="pages" {{ 'selected' if sort == 'pages' }}>Biggest</option>
      <option value="date" {{ 'selected' if sort == 'date' }}>Newest</option>
      <option value="messages" {{ 'selected' if sort == 'messages' }}>Most messages</option>
      <option value="title" {{ 'selected' if sort == 'title' }}>A-Z</option>
    </select>
    <button type="submit">Search</button>
  </form>
  <div class="tag-pills">
    {% for t in tags[:12] %}
    <a href="/?tag={{ t.name }}" class="pill {{ 'active' if tag == t.name }}">{{ t.name }} <span>{{ t.cnt }}</span></a>
    {% endfor %}
  </div>
</div>

<div class="results-info">
  Showing {{ convos|length }} of {{ total }} conversations
  {% if q %} matching "{{ q }}"{% endif %}
  {% if tag %} tagged {{ tag }}{% endif %}
  {% if source %} from {{ source }}{% endif %}
</div>

<div class="card-grid">
  {% for c in convos %}
  <a href="/conversation/{{ c.id }}" class="card">
    <div class="card-header">
      <span class="source-badge {{ c.source_name }}">{{ c.source_name }}</span>
      <span class="pages">{{ "%.0f"|format(c.estimated_pages) }}p</span>
    </div>
    <h3>{{ c.title or 'Untitled' }}</h3>
    <p class="summary">{{ (c.summary or '')[:200] }}{{ '...' if (c.summary or '')|length > 200 }}</p>
    <div class="card-footer">
      <span class="date">{{ (c.created_at or '')[:10] }}</span>
      <span class="msg-count">{{ c.message_count }} msgs</span>
    </div>
    {% if conv_tags.get(c.id) %}
    <div class="card-tags">
      {% for t in conv_tags[c.id][:4] %}
      <span class="mini-pill">{{ t }}</span>
      {% endfor %}
    </div>
    {% endif %}
  </a>
  {% endfor %}
</div>

{% if total_pages > 1 %}
<div class="pagination">
  {% if page > 1 %}
  <a href="?q={{ q }}&source={{ source }}&tag={{ tag }}&sort={{ sort }}&page={{ page-1 }}">← Prev</a>
  {% endif %}
  <span>Page {{ page }} of {{ total_pages }}</span>
  {% if page < total_pages %}
  <a href="?q={{ q }}&source={{ source }}&tag={{ tag }}&sort={{ sort }}&page={{ page+1 }}">Next →</a>
  {% endif %}
</div>
{% endif %}

</body>
</html>
```

---

## Conversation View Template
**File:** `templates/conversation.html` (2,655 chars)

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ conv.title }} — Dreambase</title>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<header>
  <h1><a href="/">Dreambase</a></h1>
  <nav>
    <a href="/">← Back</a>
    <a href="/viz">Viz</a>
    <a href="/ideas">Ideas</a>
    <a href="/showcases">Showcases</a>
  </nav>
</header>

<div class="conv-header">
  <h2>{{ conv.title or 'Untitled' }}</h2>
  <div class="conv-meta">
    <span class="source-badge {{ conv.source_name }}">{{ conv.source_name }}</span>
    <span>{{ (conv.created_at or '')[:10] }}</span>
    <span>{{ conv.message_count }} messages</span>
    <span>{{ "%.0f"|format(conv.estimated_pages or 0) }} pages</span>
  </div>

  {% if tags %}
  <div class="conv-tags">
    {% for t in tags %}
    <a href="/?tag={{ t.name }}" class="pill">{{ t.name }} <span class="method">{{ t.method }}</span></a>
    {% endfor %}
  </div>
  {% endif %}

  {% if conv.summary %}
  <div class="conv-summary">
    <strong>Summary:</strong> {{ conv.summary }}
  </div>
  {% endif %}

  {% if ideas %}
  <div class="ideas-section">
    <h3>Ideas in this conversation</h3>
    {% for idea in ideas %}
    <div class="idea-card">
      <strong>{{ idea.name }}</strong>
      <span class="pill mini">{{ idea.category }}</span>
      <span class="pill mini">{{ idea.maturity }}</span>
      {% if idea.description %}<p>{{ idea.description }}</p>{% endif %}
    </div>
    {% endfor %}
  </div>
  {% endif %}
</div>

<div class="messages">
  {% for msg in messages %}
  <div class="msg {{ msg.role }}">
    <div class="msg-header">
      <span class="role-label">{{ msg.role }}</span>
      {% if msg.created_at %}<span class="msg-date">{{ msg.created_at[:16] }}</span>{% endif %}
      {% if msg.sentiment_label %}
      <span class="sentiment {{ msg.sentiment_label }}">{{ msg.sentiment_label }} ({{ "%.2f"|format(msg.sentiment_vader or 0) }})</span>
      {% endif %}
    </div>
    <div class="msg-body">{{ msg.content[:5000] }}{% if (msg.content or '')|length > 5000 %}<span class="truncated">... [truncated, {{ msg.char_count }} chars total]</span>{% endif %}</div>
  </div>
  {% endfor %}
</div>

{% if total_msg_pages > 1 %}
<div class="pagination">
  {% if msg_page > 1 %}
  <a href="/conversation/{{ conv.id }}?msg_page={{ msg_page-1 }}">← Prev</a>
  {% endif %}
  <span>Messages page {{ msg_page }} of {{ total_msg_pages }}</span>
  {% if msg_page < total_msg_pages %}
  <a href="/conversation/{{ conv.id }}?msg_page={{ msg_page+1 }}">Next →</a>
  {% endif %}
</div>
{% endif %}

</body>
</html>
```

---

## Ideas Page Template
**File:** `templates/ideas.html` (1,514 chars)

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ideas — Dreambase</title>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<header>
  <h1><a href="/">Dreambase</a></h1>
  <nav>
    <a href="/">Browse</a>
    <a href="/viz">Viz</a>
    <a href="/ideas" class="active">Ideas</a>
    <a href="/showcases">Showcases</a>
  </nav>
</header>

<div class="controls">
  <div class="tag-pills">
    <a href="/ideas" class="pill {{ 'active' if not category }}">All ({{ ideas|length }})</a>
    {% for cat in categories %}
    <a href="/ideas?category={{ cat.category }}" class="pill {{ 'active' if category == cat.category }}">{{ cat.category }}</a>
    {% endfor %}
  </div>
</div>

<div class="card-grid">
  {% for idea in ideas %}
  <a href="/conversation/{{ idea.conversation_id }}" class="card idea-card">
    <div class="card-header">
      <span class="pill mini {{ idea.category }}">{{ idea.category }}</span>
      <span class="pill mini maturity-{{ idea.maturity }}">{{ idea.maturity }}</span>
    </div>
    <h3>{{ idea.name or idea.conv_title }}</h3>
    {% if idea.description %}
    <p class="summary">{{ idea.description[:200] }}</p>
    {% endif %}
    <div class="card-footer">
      <span class="source-badge {{ idea.source_name }}">{{ idea.source_name }}</span>
      <span class="pages">{{ "%.0f"|format(idea.estimated_pages or 0) }}p</span>
    </div>
  </a>
  {% endfor %}
</div>

</body>
</html>
```

---

## Visualizations Dashboard Template
**File:** `templates/viz.html` (21,694 chars)

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Viz — Dreambase</title>
<link rel="stylesheet" href="/static/style.css">
<style>
.viz-controls {
  padding: 1rem 2rem;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.viz-toggle {
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  background: var(--bg);
  border: 1px solid var(--border);
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
  user-select: none;
}
.viz-toggle:hover { border-color: var(--accent); color: var(--text); }
.viz-toggle.active { background: var(--accent); color: white; border-color: var(--accent); }
.viz-pane {
  margin: 1rem 2rem;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  transition: all 0.3s;
}
.viz-pane.hidden { display: none; }
.viz-pane-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  cursor: pointer;
}
.viz-pane-header h3 { font-size: 0.95rem; color: var(--accent); }
.viz-pane-header .subtitle { font-size: 0.7rem; color: var(--text-muted); font-style: italic; }
.viz-pane-body { padding: 1rem; overflow-x: auto; }
.viz-pane-body canvas { width: 100%; }

/* Timeline */
.timeline-row { display: flex; align-items: center; margin-bottom: 2px; }
.timeline-label { width: 110px; font-size: 0.7rem; color: var(--text-muted); text-align: right; padding-right: 8px; flex-shrink: 0; }
.timeline-bar-area { flex: 1; display: flex; height: 18px; gap: 1px; }
.timeline-cell {
  height: 100%;
  border-radius: 2px;
  min-width: 2px;
  position: relative;
}
.timeline-cell:hover { opacity: 0.8; }
.timeline-cell .tt {
  display: none; position: absolute; bottom: 100%; left: 0; background: #000;
  color: #fff; padding: 2px 6px; font-size: 0.65rem; border-radius: 4px;
  white-space: nowrap; z-index: 5;
}
.timeline-cell:hover .tt { display: block; }
.timeline-month-labels { display: flex; margin-left: 110px; }
.timeline-month-labels span { font-size: 0.55rem; color: var(--text-muted); flex: 1; text-align: center; }

/* Constellation */
.constellation-svg { width: 100%; min-height: 400px; }
.constellation-svg text { font-family: 'Segoe UI', system-ui; }
.constellation-svg .node-label { font-size: 11px; fill: var(--text); text-anchor: middle; }
.constellation-svg .edge { stroke: var(--border); stroke-opacity: 0.6; }
.constellation-svg .node { cursor: pointer; }
.constellation-svg .node:hover { opacity: 0.8; }

/* Heatmap */
.heatmap-grid { display: flex; flex-direction: column; gap: 1px; }
.heatmap-row { display: flex; gap: 1px; align-items: center; }
.heatmap-cell {
  width: 10px; height: 10px; border-radius: 2px;
  background: var(--bg); position: relative;
}
.heatmap-cell:hover .tt { display: block; }
.heatmap-label { width: 30px; font-size: 0.55rem; color: var(--text-muted); text-align: right; padding-right: 4px; }
.heatmap-month-labels { display: flex; margin-left: 34px; gap: 1px; }
.heatmap-month-labels span { font-size: 0.5rem; color: var(--text-muted); }

/* Funnel */
.funnel-row { display: flex; align-items: center; margin-bottom: 6px; }
.funnel-label { width: 90px; font-size: 0.75rem; color: var(--text-muted); text-align: right; padding-right: 10px; }
.funnel-bars { flex: 1; display: flex; gap: 2px; height: 24px; }
.funnel-bar { height: 100%; border-radius: 3px; display: flex; align-items: center; padding: 0 6px; font-size: 0.65rem; color: white; font-weight: 600; min-width: 20px; }

/* Sentiment */
.sentiment-chart { width: 100%; min-height: 200px; }

/* Treemap */
.treemap-container { display: flex; flex-wrap: wrap; gap: 2px; }
.treemap-block {
  border-radius: 4px; padding: 4px 6px; font-size: 0.6rem;
  color: white; display: flex; flex-direction: column;
  justify-content: center; overflow: hidden; min-height: 30px;
  position: relative;
}
.treemap-block strong { font-size: 0.7rem; }
.treemap-block span { opacity: 0.7; font-size: 0.55rem; }

/* Sparkline table */
.spark-table { width: 100%; border-collapse: collapse; }
.spark-table th { font-size: 0.7rem; color: var(--text-muted); text-align: left; padding: 4px 8px; border-bottom: 1px solid var(--border); }
.spark-table td { font-size: 0.8rem; padding: 6px 8px; border-bottom: 1px solid #222; }
.spark-table .tag-name { color: var(--accent); font-weight: 600; }
.spark-table .num { text-align: right; font-variant-numeric: tabular-nums; }
.spark-table .sent-pos { color: var(--green); }
.spark-table .sent-neg { color: var(--red); }
.spark-table .sent-neu { color: var(--text-muted); }
.sparkline { display: inline-block; vertical-align: middle; }
</style>
</head>
<body>
<header>
  <h1><a href="/">Dreambase</a></h1>
  <nav>
    <a href="/">Browse</a>
    <a href="/viz" class="active">Viz</a>
    <a href="/ideas">Ideas</a>
  </nav>
</header>

<div class="viz-controls" id="toggles">
  <span style="color:var(--text-muted);font-size:0.75rem;padding:0.3rem 0">Show:</span>
  <button class="viz-toggle active" data-pane="timeline">Timeline</button>
  <button class="viz-toggle active" data-pane="constellation">Topics</button>
  <button class="viz-toggle active" data-pane="heatmap">Activity</button>
  <button class="viz-toggle active" data-pane="funnel">Ideas</button>
  <button class="viz-toggle active" data-pane="sentiment">Sentiment</button>
  <button class="viz-toggle active" data-pane="treemap">Scale</button>
  <button class="viz-toggle active" data-pane="sparklines">Sparklines</button>
  <button class="viz-toggle" onclick="toggleAll()" style="margin-left:auto; border-style:dashed">All / None</button>
</div>

<!-- 1. INTELLECTUAL TIMELINE -->
<div class="viz-pane" id="pane-timeline">
  <div class="viz-pane-header">
    <div>
      <h3>Intellectual Timeline</h3>
      <span class="subtitle">every conversation you ever had, arranged by when you had it</span>
    </div>
  </div>
  <div class="viz-pane-body" id="timeline-body"></div>
</div>

<!-- 2. TOPIC CONSTELLATION -->
<div class="viz-pane" id="pane-constellation">
  <div class="viz-pane-header">
    <div>
      <h3>Topic Constellation</h3>
      <span class="subtitle">your brain's wiring diagram (some connections may surprise you)</span>
    </div>
  </div>
  <div class="viz-pane-body">
    <svg id="constellation-svg" class="constellation-svg" viewBox="0 0 700 420"></svg>
  </div>
</div>

<!-- 3. ACTIVITY HEATMAP -->
<div class="viz-pane" id="pane-heatmap">
  <div class="viz-pane-header">
    <div>
      <h3>Activity Heatmap</h3>
      <span class="subtitle">the days you couldn't stop talking to computers (and the days you touched grass)</span>
    </div>
  </div>
  <div class="viz-pane-body" id="heatmap-body"></div>
</div>

<!-- 4. IDEA FUNNEL -->
<div class="viz-pane" id="pane-funnel">
  <div class="viz-pane-header">
    <div>
      <h3>Idea Maturity Funnel</h3>
      <span class="subtitle">397 ideas entered. 10 survived to "built." darwin would be proud.</span>
    </div>
  </div>
  <div class="viz-pane-body" id="funnel-body"></div>
</div>

<!-- 5. SENTIMENT RIVER -->
<div class="viz-pane" id="pane-sentiment">
  <div class="viz-pane-header">
    <div>
      <h3>Sentiment River</h3>
      <span class="subtitle">your emotional weather report, month by month</span>
    </div>
  </div>
  <div class="viz-pane-body">
    <canvas id="sentiment-canvas" height="220"></canvas>
  </div>
</div>

<!-- 6. SCALE TREEMAP -->
<div class="viz-pane" id="pane-treemap">
  <div class="viz-pane-header">
    <div>
      <h3>Conversation Scale</h3>
      <span class="subtitle">if every conversation were a room, some would be closets and one would be a stadium</span>
    </div>
  </div>
  <div class="viz-pane-body">
    <div class="treemap-container" id="treemap-body"></div>
  </div>
</div>

<!-- 7. SPARKLINE TABLE -->
<div class="viz-pane" id="pane-sparklines">
  <div class="viz-pane-header">
    <div>
      <h3>Tag Dashboard</h3>
      <span class="subtitle">tufte's favorite: maximum data, minimum ink, zero chartjunk</span>
    </div>
  </div>
  <div class="viz-pane-body">
    <table class="spark-table">
      <thead>
        <tr><th>Tag</th><th class="num">Convos</th><th class="num">Ideas</th><th class="num">Avg Sent</th><th class="num">Avg Pages</th><th>Trend (6mo)</th></tr>
      </thead>
      <tbody id="sparkline-tbody"></tbody>
    </table>
  </div>
</div>

<script>
// Data from Flask
const timelineData = {{ timeline | tojson }};
const cooccurrence = {{ cooccurrence | tojson }};
const tagTotals = {{ tag_totals | tojson }};
const heatmapData = {{ heatmap | tojson }};
const ideaFunnel = {{ idea_funnel | tojson }};
const sentimentData = {{ sentiment | tojson }};
const treemapData = {{ treemap | tojson }};
const topConvos = {{ top_convos | tojson }};
const sparklineTags = {{ sparkline_tags | tojson }};
const tagTrends = {{ tag_trends | tojson }};

// Source colors
const SRC_COLORS = {
  chatgpt: '#4caf50', llm_logs_html: '#7c6fe0', llm_logs_pdf: '#9c7fe0',
  claude: '#ff9800', sms: '#00bcd4', twitter: '#1da1f2',
  facebook: '#4267b2', google_chat: '#34a853', pkd_chats: '#e74c3c', gmail: '#ea4335'
};
const TAG_COLORS = {
  game_idea: '#4caf50', esoteric: '#9c27b0', personal: '#ff9800',
  alchemy: '#ffd700', educational: '#00bcd4', mtg: '#e74c3c',
  coding: '#2196f3', app_project: '#8bc34a', pkd: '#ff5722'
};

// Toggle logic
document.querySelectorAll('.viz-toggle[data-pane]').forEach(btn => {
  btn.addEventListener('click', () => {
    btn.classList.toggle('active');
    const pane = document.getElementById('pane-' + btn.dataset.pane);
    pane.classList.toggle('hidden', !btn.classList.contains('active'));
  });
});
function toggleAll() {
  const btns = document.querySelectorAll('.viz-toggle[data-pane]');
  const anyActive = [...btns].some(b => b.classList.contains('active'));
  btns.forEach(btn => {
    if (anyActive) { btn.classList.remove('active'); }
    else { btn.classList.add('active'); }
    const pane = document.getElementById('pane-' + btn.dataset.pane);
    pane.classList.toggle('hidden', anyActive);
  });
}

// 1. TIMELINE
(function() {
  const body = document.getElementById('timeline-body');
  // Group by source, then by month
  const sources = [...new Set(timelineData.map(d => d.source))];
  const months = [...new Set(timelineData.map(d => d.month))].sort();
  const lookup = {};
  timelineData.forEach(d => { lookup[d.source + '|' + d.month] = d; });
  const maxPages = Math.max(...timelineData.map(d => d.pages || 0), 1);

  let html = '';
  sources.forEach(src => {
    html += `<div class="timeline-row"><div class="timeline-label">${src}</div><div class="timeline-bar-area">`;
    months.forEach(m => {
      const d = lookup[src + '|' + m];
      if (d) {
        const h = Math.max(2, Math.round((d.pages / maxPages) * 18));
        const w = Math.max(2, Math.round(Math.sqrt(d.cnt) * 2));
        html += `<div class="timeline-cell" style="width:${w}px;height:${h}px;background:${SRC_COLORS[src]||'#666'};align-self:flex-end"><span class="tt">${m}: ${d.cnt} convos, ${Math.round(d.pages)}p</span></div>`;
      } else {
        html += `<div class="timeline-cell" style="width:2px;background:transparent"></div>`;
      }
    });
    html += '</div></div>';
  });
  // Month labels (show every 6th)
  html += '<div class="timeline-month-labels">';
  months.forEach((m, i) => {
    html += (i % 6 === 0) ? `<span>${m}</span>` : '<span></span>';
  });
  html += '</div>';
  body.innerHTML = html;
})();

// 2. CONSTELLATION
(function() {
  const svg = document.getElementById('constellation-svg');
  const W = 700, H = 420;
  // Position tags in a circle
  const tags = tagTotals.map(t => t.name);
  const tagMap = {};
  tagTotals.forEach(t => tagMap[t.name] = t.cnt);
  const cx = W/2, cy = H/2, R = 160;
  const positions = {};
  tags.forEach((t, i) => {
    const angle = (i / tags.length) * Math.PI * 2 - Math.PI/2;
    positions[t] = { x: cx + R * Math.cos(angle), y: cy + R * Math.sin(angle) };
  });
  // Draw edges
  const maxEdge = Math.max(...cooccurrence.map(c => c.cnt), 1);
  cooccurrence.forEach(c => {
    const p1 = positions[c.tag1], p2 = positions[c.tag2];
    if (!p1 || !p2) return;
    const w = Math.max(0.5, (c.cnt / maxEdge) * 8);
    const opacity = Math.max(0.15, c.cnt / maxEdge);
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', p1.x); line.setAttribute('y1', p1.y);
    line.setAttribute('x2', p2.x); line.setAttribute('y2', p2.y);
    line.setAttribute('stroke', '#555');
    line.setAttribute('stroke-width', w);
    line.setAttribute('stroke-opacity', opacity);
    svg.appendChild(line);
    // Edge label for strong connections
    if (c.cnt > 80) {
      const tx = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      tx.setAttribute('x', (p1.x + p2.x)/2);
      tx.setAttribute('y', (p1.y + p2.y)/2 - 4);
      tx.setAttribute('fill', '#666');
      tx.setAttribute('font-size', '9');
      tx.setAttribute('text-anchor', 'middle');
      tx.textContent = c.cnt;
      svg.appendChild(tx);
    }
  });
  // Draw nodes
  const maxTag = Math.max(...tagTotals.map(t => t.cnt), 1);
  tags.forEach(t => {
    const p = positions[t];
    const r = Math.max(12, Math.sqrt(tagMap[t] / maxTag) * 35);
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', p.x); circle.setAttribute('cy', p.y);
    circle.setAttribute('r', r);
    circle.setAttribute('fill', TAG_COLORS[t] || '#666');
    circle.setAttribute('fill-opacity', '0.7');
    circle.setAttribute('class', 'node');
    svg.appendChild(circle);
    const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    label.setAttribute('x', p.x); label.setAttribute('y', p.y + r + 14);
    label.setAttribute('class', 'node-label');
    label.textContent = `${t} (${tagMap[t]})`;
    svg.appendChild(label);
  });
})();

// 3. HEATMAP
(function() {
  const body = document.getElementById('heatmap-body');
  // Aggregate by day
  const dayMap = {};
  heatmapData.forEach(d => {
    dayMap[d.day] = (dayMap[d.day] || 0) + d.cnt;
  });
  const days = Object.keys(dayMap).sort();
  if (!days.length) { body.innerHTML = '<em>No data</em>'; return; }

  const startDate = new Date(days[0]);
  const endDate = new Date(days[days.length - 1]);
  const maxVal = Math.max(...Object.values(dayMap));

  // Build weeks
  const weeks = [];
  let current = new Date(startDate);
  current.setDate(current.getDate() - current.getDay()); // Start on Sunday
  while (current <= endDate) {
    const week = [];
    for (let d = 0; d < 7; d++) {
      const key = current.toISOString().slice(0, 10);
      week.push({ day: key, val: dayMap[key] || 0, dow: d });
      current.setDate(current.getDate() + 1);
    }
    weeks.push(week);
  }

  const dayNames = ['S','M','T','W','T','F','S'];
  let html = '<div class="heatmap-grid">';
  for (let dow = 0; dow < 7; dow++) {
    html += `<div class="heatmap-row"><div class="heatmap-label">${dayNames[dow]}</div>`;
    weeks.forEach(week => {
      const cell = week[dow];
      if (!cell) { html += '<div class="heatmap-cell"></div>'; return; }
      const intensity = cell.val ? Math.max(0.15, Math.min(1, cell.val / (maxVal * 0.4))) : 0;
      const bg = cell.val ? `rgba(124,111,224,${intensity})` : 'rgba(255,255,255,0.03)';
      html += `<div class="heatmap-cell" style="background:${bg}" title="${cell.day}: ${cell.val} convos"></div>`;
    });
    html += '</div>';
  }
  html += '</div>';

  // Month labels
  html += '<div class="heatmap-month-labels">';
  let lastMonth = '';
  weeks.forEach((week, i) => {
    const m = week[0].day.slice(0, 7);
    if (m !== lastMonth) { html += `<span style="width:${11}px">${m.slice(5)}</span>`; lastMonth = m; }
  });
  html += '</div>';
  body.innerHTML = html;
})();

// 4. IDEA FUNNEL
(function() {
  const body = document.getElementById('funnel-body');
  const categories = [...new Set(ideaFunnel.map(d => d.category))];
  const maturities = ['sketch', 'design', 'prototype', 'built'];
  const matColors = { sketch: '#555', design: '#00bcd4', prototype: '#4caf50', built: '#8bc34a' };
  const lookup = {};
  ideaFunnel.forEach(d => { lookup[d.category + '|' + d.maturity] = d.cnt; });
  const maxCnt = Math.max(...ideaFunnel.map(d => d.cnt));

  let html = '<div style="display:flex;gap:0.5rem;margin-bottom:8px">';
  maturities.forEach(m => {
    html += `<span style="font-size:0.7rem;color:${matColors[m]}">\u25CF ${m}</span>`;
  });
  html += '</div>';

  categories.forEach(cat => {
    html += `<div class="funnel-row"><div class="funnel-label">${cat}</div><div class="funnel-bars">`;
    maturities.forEach(mat => {
      const cnt = lookup[cat + '|' + mat] || 0;
      if (cnt > 0) {
        const w = Math.max(20, (cnt / maxCnt) * 400);
        html += `<div class="funnel-bar" style="width:${w}px;background:${matColors[mat]}">${cnt}</div>`;
      }
    });
    html += '</div></div>';
  });
  body.innerHTML = html;
})();

// 5. SENTIMENT RIVER
(function() {
  const canvas = document.getElementById('sentiment-canvas');
  const ctx = canvas.getContext('2d');
  canvas.width = canvas.parentElement.clientWidth || 800;
  const W = canvas.width, H = 220;

  // Aggregate by month
  const monthMap = {};
  sentimentData.forEach(d => {
    if (!monthMap[d.month]) monthMap[d.month] = { pos: 0, neg: 0, neu: 0, cnt: 0 };
    monthMap[d.month].pos += d.pos || 0;
    monthMap[d.month].neg += d.neg || 0;
    monthMap[d.month].neu += d.neu || 0;
    monthMap[d.month].cnt += d.cnt || 0;
  });
  const months = Object.keys(monthMap).sort();
  if (!months.length) return;

  const maxCnt = Math.max(...months.map(m => monthMap[m].cnt));
  const midY = H / 2;
  const barW = Math.max(2, (W - 40) / months.length);

  // Axis
  ctx.strokeStyle = '#333';
  ctx.beginPath();
  ctx.moveTo(30, midY);
  ctx.lineTo(W, midY);
  ctx.stroke();

  ctx.font = '9px system-ui';
  ctx.fillStyle = '#666';
  ctx.fillText('+pos', 2, 15);
  ctx.fillText('-neg', 2, H - 5);

  months.forEach((m, i) => {
    const d = monthMap[m];
    const x = 30 + i * barW;
    const scale = (H * 0.45) / maxCnt;

    // Positive (above axis)
    const posH = d.pos * scale;
    ctx.fillStyle = 'rgba(76, 175, 80, 0.7)';
    ctx.fillRect(x, midY - posH, barW - 1, posH);

    // Neutral (stacked above positive)
    const neuH = d.neu * scale * 0.3;
    ctx.fillStyle = 'rgba(136, 136, 136, 0.3)';
    ctx.fillRect(x, midY - posH - neuH, barW - 1, neuH);

    // Negative (below axis)
    const negH = d.neg * scale;
    ctx.fillStyle = 'rgba(231, 76, 60, 0.7)';
    ctx.fillRect(x, midY, barW - 1, negH);

    // Month label (every 3rd)
    if (i % 3 === 0) {
      ctx.fillStyle = '#666';
      ctx.fillText(m.slice(2), x, H - 1);
    }
  });
})();

// 6. TREEMAP
(function() {
  const body = document.getElementById('treemap-body');
  const totalPages = treemapData.reduce((s, d) => s + (d.total_pages || 0), 0);
  const containerW = body.parentElement.clientWidth - 32 || 800;

  let html = '';
  treemapData.forEach(d => {
    const frac = (d.total_pages || 0) / totalPages;
    const area = frac * containerW * 200;
    const w = Math.max(60, Math.sqrt(area) * 1.6);
    const h = Math.max(40, area / w);
    const color = SRC_COLORS[d.source] || '#666';
    html += `<div class="treemap-block" style="width:${w}px;height:${h}px;background:${color}">
      <strong>${d.source}</strong>
      <span>${d.convos} convos</span>
      <span>${Math.round(d.total_pages)}p / ${d.text_mb}MB</span>
    </div>`;
  });

  // Top conversations as tiny blocks
  html += '<div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:1px">';
  topConvos.forEach(c => {
    const w = Math.max(3, Math.sqrt(c.estimated_pages) * 0.8);
    const color = SRC_COLORS[c.source] || '#666';
    html += `<div style="width:${w}px;height:${w}px;background:${color};border-radius:1px;opacity:0.7" title="${c.title}: ${Math.round(c.estimated_pages)}p"></div>`;
  });
  html += '</div>';

  body.innerHTML = html;
})();

// 7. SPARKLINE TABLE
(function() {
  const tbody = document.getElementById('sparkline-tbody');
  // Build trend lookup
  const trendMap = {};
  tagTrends.forEach(d => {
    if (!trendMap[d.name]) trendMap[d.name] = [];
    trendMap[d.name].push({ month: d.month, cnt: d.cnt });
  });

  function miniSparkline(data) {
    if (!data || !data.length) return '';
    const max = Math.max(...data.map(d => d.cnt), 1);
    const w = 80, h = 20;
    const step = w / Math.max(data.length - 1, 1);
    let path = '';
    data.forEach((d, i) => {
      const x = i * step;
      const y = h - (d.cnt / max) * h;
      path += (i === 0 ? 'M' : 'L') + x.toFixed(1) + ',' + y.toFixed(1);
    });
    return `<svg class="sparkline" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
      <path d="${path}" fill="none" stroke="var(--accent)" stroke-width="1.5"/>
    </svg>`;
  }

  let html = '';
  sparklineTags.forEach(t => {
    const sentClass = (t.avg_sent || 0) > 0.05 ? 'sent-pos' : (t.avg_sent || 0) < -0.05 ? 'sent-neg' : 'sent-neu';
    const trend = trendMap[t.name] || [];
    html += `<tr>
      <td class="tag-name">${t.name}</td>
      <td class="num">${t.convos}</td>
      <td class="num">${t.ideas}</td>
      <td class="num ${sentClass}">${(t.avg_sent || 0).toFixed(3)}</td>
      <td class="num">${(t.avg_pages || 0).toFixed(0)}p</td>
      <td>${miniSparkline(trend)}</td>
    </tr>`;
  });
  tbody.innerHTML = html;
})();
</script>
</body>
</html>
```

---

## Showcase Page Template (Tabbed)
**File:** `templates/showcase.html` (10,505 chars)

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ showcase.title }} — Dreambase</title>
<link rel="stylesheet" href="/static/style.css">
<style>
/* Showcase page styles */
.showcase-hero {
  padding: 2rem 2rem 1.5rem;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}
.showcase-hero h2 {
  font-size: 1.8rem;
  margin-bottom: 0.4rem;
  color: var(--text);
}
.showcase-hook {
  font-size: 1.1rem;
  color: var(--accent);
  font-style: italic;
  margin-bottom: 1rem;
  line-height: 1.5;
}
.showcase-meta {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  color: var(--text-muted);
  font-size: 0.85rem;
}
.showcase-meta .stat {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}
.showcase-meta .stat strong {
  color: var(--orange);
}

/* Tab navigation */
.showcase-tabs {
  display: flex;
  gap: 0;
  padding: 0 2rem;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  overflow-x: auto;
}
.tab-btn {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  color: var(--text-muted);
  font-size: 0.9rem;
  cursor: pointer;
  white-space: nowrap;
  transition: color 0.2s, border-color 0.2s;
}
.tab-btn:hover {
  color: var(--text);
  background: none;
}
.tab-btn.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
  background: none;
}

/* Tab content panels */
.tab-panel {
  display: none;
  padding: 2rem;
  max-width: 900px;
}
.tab-panel.active {
  display: block;
}

/* Overview tab */
.narrative {
  font-size: 0.95rem;
  line-height: 1.8;
  color: var(--text);
}
.narrative p {
  margin-bottom: 1rem;
}
.narrative h3 {
  color: var(--accent);
  margin: 1.5rem 0 0.5rem;
  font-size: 1.1rem;
}

/* Design Evolution tab */
.timeline-entry {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}
.timeline-date {
  min-width: 90px;
  font-size: 0.8rem;
  color: var(--text-muted);
  padding-top: 0.2rem;
}
.timeline-body h4 {
  font-size: 0.95rem;
  margin-bottom: 0.3rem;
}
.timeline-body p {
  font-size: 0.88rem;
  color: var(--text-muted);
  line-height: 1.5;
}
.timeline-body .conv-link {
  font-size: 0.75rem;
  margin-top: 0.3rem;
  display: inline-block;
}

/* Key Quotes tab */
.quote-card {
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
  background: var(--bg);
  border-left: 3px solid var(--accent);
  border-radius: 0 8px 8px 0;
}
.quote-card blockquote {
  font-size: 0.95rem;
  line-height: 1.6;
  font-style: italic;
  color: var(--text);
  margin-bottom: 0.5rem;
}
.quote-card .quote-source {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Gallery tab */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}
.gallery-item {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}
.gallery-item img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
}
.gallery-item .caption {
  padding: 0.75rem;
  font-size: 0.8rem;
  color: var(--text-muted);
}
.gallery-placeholder {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  color: var(--text-muted);
  font-style: italic;
}

/* Source Conversations tab */
.source-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.source-conv {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  transition: border-color 0.2s;
}
.source-conv:hover {
  border-color: var(--accent);
  text-decoration: none;
}
.source-conv .title {
  flex: 1;
  font-size: 0.9rem;
}
.source-conv .pages {
  font-size: 0.85rem;
  color: var(--orange);
  font-weight: 600;
  min-width: 50px;
  text-align: right;
}

/* Pedagogy section (within overview or its own tab) */
.pedagogy-box {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.25rem;
  margin-top: 1.5rem;
}
.pedagogy-box h4 {
  color: var(--orange);
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}
.pedagogy-box .difficulty {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 0.75rem;
}
.difficulty-level {
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  line-height: 1.4;
}
.difficulty-level.easy { background: #1a3a1a; color: var(--green); }
.difficulty-level.medium { background: #3a2a1a; color: var(--orange); }
.difficulty-level.hard { background: #3a1a1a; color: var(--red); }
.difficulty-level strong { display: block; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.2rem; }

/* Tags */
.showcase-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 1rem;
}

/* Empty state */
.placeholder-note {
  color: var(--text-muted);
  font-style: italic;
  font-size: 0.9rem;
  padding: 2rem;
  text-align: center;
}
</style>
</head>
<body>
<header>
  <h1><a href="/">Dreambase</a></h1>
  <nav>
    <a href="/">Browse</a>
    <a href="/viz">Viz</a>
    <a href="/ideas">Ideas</a>
    <a href="/showcases">Showcases</a>
  </nav>
</header>

<!-- Hero -->
<div class="showcase-hero">
  <h2>{{ showcase.title }}</h2>
  <div class="showcase-hook">{{ showcase.hook }}</div>
  <div class="showcase-meta">
    <span class="stat"><strong>{{ conversations|length }}</strong> conversations</span>
    <span class="stat"><strong>{{ total_pages }}</strong> pages of design</span>
    <span class="stat"><strong>{{ showcase.category }}</strong></span>
    {% if showcase.maturity %}
    <span class="pill mini maturity-{{ showcase.maturity }}">{{ showcase.maturity }}</span>
    {% endif %}
  </div>
  {% if tags %}
  <div class="showcase-tags">
    {% for t in tags %}
    <a href="/?tag={{ t }}" class="pill">{{ t }}</a>
    {% endfor %}
  </div>
  {% endif %}
</div>

<!-- Tabs -->
<div class="showcase-tabs">
  <button class="tab-btn active" onclick="showTab('overview')">Overview</button>
  <button class="tab-btn" onclick="showTab('evolution')">Design Evolution</button>
  <button class="tab-btn" onclick="showTab('quotes')">Key Quotes</button>
  <button class="tab-btn" onclick="showTab('gallery')">Gallery</button>
  <button class="tab-btn" onclick="showTab('sources')">Source Conversations</button>
</div>

<!-- TAB: Overview -->
<div class="tab-panel active" id="tab-overview">
  {% if showcase.narrative %}
  <div class="narrative">
    {{ showcase.narrative|safe }}
  </div>
  {% else %}
  <p class="placeholder-note">
    Narrative summary pending. Generate by running the ChatGPT batch reading workflow
    on this dream's source conversations, then import with showcase_import.py.
  </p>
  {% endif %}

  {% if showcase.pedagogy %}
  <div class="pedagogy-box">
    <h4>What This Dream Teaches</h4>
    <p style="font-size:0.88rem; color:var(--text-muted); line-height:1.5;">{{ showcase.pedagogy }}</p>
    {% if showcase.difficulty_easy or showcase.difficulty_medium or showcase.difficulty_hard %}
    <div class="difficulty">
      {% if showcase.difficulty_easy %}
      <div class="difficulty-level easy"><strong>Easy</strong>{{ showcase.difficulty_easy }}</div>
      {% endif %}
      {% if showcase.difficulty_medium %}
      <div class="difficulty-level medium"><strong>Medium</strong>{{ showcase.difficulty_medium }}</div>
      {% endif %}
      {% if showcase.difficulty_hard %}
      <div class="difficulty-level hard"><strong>Hard</strong>{{ showcase.difficulty_hard }}</div>
      {% endif %}
    </div>
    {% endif %}
  </div>
  {% endif %}
</div>

<!-- TAB: Design Evolution -->
<div class="tab-panel" id="tab-evolution">
  {% if timeline_entries %}
  {% for entry in timeline_entries %}
  <div class="timeline-entry">
    <div class="timeline-date">{{ entry.date }}</div>
    <div class="timeline-body">
      <h4>{{ entry.title }}</h4>
      <p>{{ entry.description }}</p>
      {% if entry.conversation_id %}
      <a href="/conversation/{{ entry.conversation_id }}" class="conv-link">View conversation</a>
      {% endif %}
    </div>
  </div>
  {% endfor %}
  {% else %}
  <p class="placeholder-note">
    Design evolution timeline pending. Will be populated after ChatGPT batch reading.
  </p>
  {% endif %}
</div>

<!-- TAB: Key Quotes -->
<div class="tab-panel" id="tab-quotes">
  {% if quotes %}
  {% for q in quotes %}
  <div class="quote-card">
    <blockquote>"{{ q.text }}"</blockquote>
    <div class="quote-source">
      — {{ q.role }}, {{ q.conversation_title }}
      {% if q.conversation_id %}
      <a href="/conversation/{{ q.conversation_id }}">view</a>
      {% endif %}
    </div>
  </div>
  {% endfor %}
  {% else %}
  <p class="placeholder-note">
    Key quotes will be extracted during the ChatGPT batch reading workflow.
    The best moments from {{ conversations|length }} conversations, curated.
  </p>
  {% endif %}
</div>

<!-- TAB: Gallery -->
<div class="tab-panel" id="tab-gallery">
  {% if images %}
  <div class="gallery-grid">
    {% for img in images %}
    <div class="gallery-item">
      <img src="{{ img.url }}" alt="{{ img.caption }}" loading="lazy"
           onerror="this.parentElement.innerHTML='<div class=gallery-placeholder>Image unavailable</div>'">
      <div class="caption">{{ img.caption }}</div>
    </div>
    {% endfor %}
  </div>
  {% else %}
  <p class="placeholder-note">
    Gallery pending. Sources: DALL-E images from ChatGPT conversations,
    public domain art from Wikimedia Commons, AI-generated concept art (v2).
  </p>
  {% endif %}
</div>

<!-- TAB: Source Conversations -->
<div class="tab-panel" id="tab-sources">
  <div class="source-list">
    {% for c in conversations %}
    <a href="/conversation/{{ c.id }}" class="source-conv">
      <span class="source-badge {{ c.source_name }}">{{ c.source_name }}</span>
      <span class="title">{{ c.title }}</span>
      <span class="pages">{{ "%.0f"|format(c.estimated_pages or 0) }}p</span>
    </a>
    {% endfor %}
  </div>
</div>

<script>
function showTab(name) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  event.target.classList.add('active');
}
</script>

</body>
</html>
```

---

## Showcases Index Template
**File:** `templates/showcases.html` (2,534 chars)

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Showcases — Dreambase</title>
<link rel="stylesheet" href="/static/style.css">
<style>
.showcase-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
  padding: 2rem;
}
.showcase-card {
  display: block;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  color: var(--text);
  transition: border-color 0.2s, transform 0.1s;
}
.showcase-card:hover {
  border-color: var(--accent);
  transform: translateY(-3px);
  text-decoration: none;
}
.showcase-card h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}
.showcase-card .hook {
  font-style: italic;
  color: var(--accent);
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 0.75rem;
}
.showcase-card .pedagogy {
  font-size: 0.82rem;
  color: var(--text-muted);
  line-height: 1.5;
  margin-bottom: 0.75rem;
}
.showcase-card .meta {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
}
.page-intro {
  padding: 2rem 2rem 0;
  max-width: 700px;
}
.page-intro h2 { margin-bottom: 0.5rem; }
.page-intro p { color: var(--text-muted); font-size: 0.95rem; line-height: 1.6; }
</style>
</head>
<body>
<header>
  <h1><a href="/">Dreambase</a></h1>
  <nav>
    <a href="/">Browse</a>
    <a href="/viz">Viz</a>
    <a href="/ideas">Ideas</a>
    <a href="/showcases" class="active">Showcases</a>
  </nav>
</header>

<div class="page-intro">
  <h2>Dream Showcases</h2>
  <p>Deep dives into the most developed creative dreams — games, tools, and
  ideas that span dozens of conversations and hundreds of pages of design work.
  Each showcase tells the story of how an idea evolved.</p>
</div>

<div class="showcase-grid">
  {% for sc in showcases %}
  <a href="/dream/{{ sc.slug }}" class="showcase-card">
    <div class="card-header">
      <span class="pill mini {{ sc.category }}">{{ sc.category }}</span>
      <span class="pill mini maturity-{{ sc.maturity }}">{{ sc.maturity }}</span>
    </div>
    <h3>{{ sc.title }}</h3>
    <div class="hook">{{ sc.hook }}</div>
    <div class="pedagogy">{{ sc.pedagogy[:150] }}{% if sc.pedagogy|length > 150 %}...{% endif %}</div>
    <div class="meta">
      <span>{{ sc.conversation_ids|length }} conversations</span>
      {% for t in sc.tags[:3] %}
      <span class="pill mini">{{ t }}</span>
      {% endfor %}
    </div>
  </a>
  {% endfor %}
</div>

</body>
</html>
```

---

## CSS Stylesheet
**File:** `static/style.css` (6,668 chars)

```css
/* Dreambase — Haunt Your Own Records */
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --bg: #0d0d0d;
  --surface: #1a1a1a;
  --card: #1e1e2e;
  --border: #333;
  --text: #e0e0e0;
  --text-muted: #888;
  --accent: #7c6fe0;
  --green: #4caf50;
  --orange: #ff9800;
  --cyan: #00bcd4;
  --red: #e74c3c;
}

body {
  font-family: 'Segoe UI', system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}

a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

/* Header */
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 10;
}
header h1 a { color: var(--accent); font-size: 1.3rem; }
header nav { display: flex; gap: 1.5rem; }
header nav a { color: var(--text-muted); }
header nav a.active, header nav a:hover { color: var(--accent); }

/* Controls */
.controls { padding: 1rem 2rem; background: var(--surface); border-bottom: 1px solid var(--border); }
.search-form { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.75rem; }
.search-input {
  flex: 1; min-width: 200px; padding: 0.5rem 0.75rem;
  background: var(--bg); border: 1px solid var(--border); border-radius: 6px;
  color: var(--text); font-size: 0.9rem;
}
select {
  padding: 0.5rem; background: var(--bg); border: 1px solid var(--border);
  border-radius: 6px; color: var(--text); font-size: 0.85rem;
}
button {
  padding: 0.5rem 1rem; background: var(--accent); border: none;
  border-radius: 6px; color: white; cursor: pointer; font-size: 0.9rem;
}
button:hover { opacity: 0.9; }

/* Tag pills */
.tag-pills { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.pill {
  display: inline-block; padding: 0.2rem 0.6rem; border-radius: 12px;
  background: var(--surface); border: 1px solid var(--border);
  color: var(--text-muted); font-size: 0.75rem; white-space: nowrap;
}
.pill:hover, .pill.active { background: var(--accent); color: white; border-color: var(--accent); }
.pill span { opacity: 0.6; }
.mini-pill {
  display: inline-block; padding: 0.1rem 0.4rem; border-radius: 8px;
  background: #2a2a3e; color: var(--text-muted); font-size: 0.65rem;
}

/* Results info */
.results-info { padding: 0.5rem 2rem; color: var(--text-muted); font-size: 0.85rem; }

/* Card grid */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  padding: 1rem 2rem 2rem;
}
.card {
  display: block; background: var(--card); border: 1px solid var(--border);
  border-radius: 10px; padding: 1rem; color: var(--text);
  transition: border-color 0.2s, transform 0.1s;
}
.card:hover { border-color: var(--accent); transform: translateY(-2px); text-decoration: none; }
.card h3 { font-size: 0.95rem; margin: 0.5rem 0; line-height: 1.3; }
.card .summary { font-size: 0.8rem; color: var(--text-muted); line-height: 1.4; margin-bottom: 0.5rem; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-footer { display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); }
.card-tags { margin-top: 0.5rem; display: flex; flex-wrap: wrap; gap: 0.3rem; }
.pages { font-weight: 600; color: var(--orange); }

/* Source badges */
.source-badge {
  font-size: 0.65rem; padding: 0.15rem 0.5rem; border-radius: 8px;
  text-transform: uppercase; letter-spacing: 0.03em; font-weight: 600;
}
.source-badge.chatgpt { background: #1a3a1a; color: #4caf50; }
.source-badge.llm_logs_html, .source-badge.llm_logs_pdf { background: #1a1a3a; color: #7c6fe0; }
.source-badge.claude { background: #3a2a1a; color: #ff9800; }
.source-badge.sms { background: #1a2a3a; color: #00bcd4; }
.source-badge.twitter { background: #1a2a3a; color: #1da1f2; }
.source-badge.facebook { background: #1a1a3a; color: #4267b2; }
.source-badge.google_chat { background: #1a3a1a; color: #34a853; }
.source-badge.pkd_chats { background: #3a1a2a; color: #e74c3c; }

/* Conversation view */
.conv-header { padding: 1.5rem 2rem; background: var(--surface); border-bottom: 1px solid var(--border); }
.conv-header h2 { margin-bottom: 0.5rem; }
.conv-meta { display: flex; gap: 1rem; flex-wrap: wrap; color: var(--text-muted); font-size: 0.85rem; margin-bottom: 0.75rem; }
.conv-tags { margin: 0.75rem 0; display: flex; flex-wrap: wrap; gap: 0.4rem; }
.conv-summary { padding: 0.75rem; background: var(--bg); border-radius: 8px; font-size: 0.9rem; margin-top: 0.75rem; }
.ideas-section { margin-top: 1rem; }
.ideas-section h3 { font-size: 0.9rem; margin-bottom: 0.5rem; color: var(--orange); }
.idea-card { padding: 0.5rem; background: var(--bg); border-radius: 6px; margin-bottom: 0.5rem; }

/* Messages */
.messages { padding: 1rem 2rem 2rem; max-width: 900px; }
.msg { margin-bottom: 1rem; padding: 0.75rem 1rem; border-radius: 10px; }
.msg.user { background: #1a1a2e; border-left: 3px solid var(--accent); }
.msg.assistant { background: #1a2e1a; border-left: 3px solid var(--green); }
.msg.sender { background: #1a2e2e; border-left: 3px solid var(--cyan); }
.msg.system, .msg.tool { background: #2e2a1a; border-left: 3px solid var(--orange); font-size: 0.85rem; }
.msg-header { display: flex; gap: 1rem; align-items: center; margin-bottom: 0.4rem; }
.role-label { font-weight: 700; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.03em; }
.msg.user .role-label { color: var(--accent); }
.msg.assistant .role-label { color: var(--green); }
.msg.sender .role-label { color: var(--cyan); }
.msg-date { font-size: 0.7rem; color: var(--text-muted); }
.msg-body { white-space: pre-wrap; word-wrap: break-word; font-size: 0.88rem; line-height: 1.5; }
.truncated { color: var(--orange); font-style: italic; font-size: 0.8rem; }
.sentiment { font-size: 0.65rem; padding: 0.1rem 0.4rem; border-radius: 6px; }
.sentiment.positive { background: #1a3a1a; color: var(--green); }
.sentiment.negative { background: #3a1a1a; color: var(--red); }
.sentiment.neutral { background: #2a2a2a; color: var(--text-muted); }
.method { font-size: 0.6rem; opacity: 0.5; }

/* Maturity badges */
.maturity-sketch { background: #2a2a3e; }
.maturity-design { background: #1a2a3a; color: var(--cyan); }
.maturity-prototype { background: #2a3a1a; color: var(--green); }
.maturity-built { background: #1a3a1a; color: #8bc34a; }

/* Pagination */
.pagination {
  display: flex; justify-content: center; gap: 1rem; padding: 1.5rem;
  align-items: center; color: var(--text-muted);
}
.pagination a {
  padding: 0.4rem 1rem; background: var(--surface); border: 1px solid var(--border);
  border-radius: 6px;
}
```

---

## Rabbit Hole Web Design Template
**File:** `DREAMBASE_DESIGN_TEMPLATE.md` (10,878 chars)

```md
# Dreambase: Rabbit Hole Web Design Template

## Concept
A card-based "dream catalog" website where each card represents a creative dream,
idea, or intellectual obsession mined from 2+ years of personal data. Users navigate
by clicking theme buttons to descend deeper into interconnected rabbit holes.

Think: xkcd's visual wit meets Tufte's data density meets a Renaissance cabinet of curiosities.

---

## INFORMATION ARCHITECTURE

### Level 0: The Dream Wall
- All 100 (or N) dream cards visible at once as a mosaic
- Each card: illustration + title + 1-sentence hook
- Theme buttons along top or side for filtering (alchemy, games, esoteric, etc.)
- Cards resize/reflow based on active filters
- Subtle animation: cards not matching a filter fade rather than disappear

### Level 1: The Dream Card (expanded)
- Full card view with: title, 3-sentence summary, illustration, source badge
- "Down the rabbit hole" section with theme buttons specific to THIS dream
- Related dreams sidebar (connected by shared tags/topics)
- Key quotes or moments pulled from the original conversation
- Maturity badge: sketch / design / prototype / built
- Timeline: when this dream first appeared, how it evolved

### Level 2: The Rabbit Hole
- Filtered view showing ALL dreams connected by a theme
- Theme header with description and visual motif
- Dreams arranged by: chronological, maturity, or interconnection
- Visualization: mini constellation showing how dreams in this theme connect
- "Adjacent themes" links to other rabbit holes

### Level 3: The Conversation (existing /conversation/<id> view)
- Full original conversation with sentiment and message-level detail
- "Other dreams born in this conversation" links

---

## VISUAL DESIGN PRINCIPLES

### The xkcd Spirit
- Captions and labels should have personality, not be sterile
- Occasional self-deprecating humor in empty states
  ("No dreams here yet. You were probably touching grass that week.")
- Hand-drawn or sketch aesthetic for borders/arrows/annotations
- Stick-figure-style mascot or recurring visual character?
- Alt-text / tooltips with bonus commentary (xkcd's signature move)

### The Tufte Discipline
- No chartjunk: every visual element encodes data
- Small multiples over animation
- High information density per screen
- Direct labeling (no legends floating off to the side)
- Minimal chrome, maximum content

### The Cabinet of Curiosities
- Each dream card feels like a physical artifact
- Illustrations sourced from: ChatGPT DALL-E outputs, public domain
  historical art (Wikimedia, Met Open Access, British Library, Wellcome)
- Visual texture: parchment, manuscript margins, alchemical diagrams
- But not cosplay — modern typography, dark theme, clean grid

---

## CONTENT GUIDELINES

### Dream Card Copy
- Title: 3-7 words, evocative not descriptive
  GOOD: "The Alchemy Board Game"
  BAD: "Conversation about making a board game with alchemy theme"
- Hook: 1 sentence that makes someone want to click
  GOOD: "What if transmutation was a game mechanic?"
  BAD: "This conversation discusses alchemy-themed board games."
- Summary: 3 sentences — what is it, why does it matter, where did it go
- Tags: 2-4 theme tags for rabbit hole navigation

### Theme Descriptions
- Each theme (alchemy, games, esoteric, etc.) gets a 2-sentence description
- Tone: intellectual but accessible, curious not pretentious
- Include a "why this matters to me" personal angle

### Rabbit Hole Navigation Copy
- Button labels should be inviting: "Go deeper" not "View more"
- Theme transitions: "This dream also touches on..." not "Related tags:"
- Dead ends acknowledged: "This rabbit hole loops back to [X]"

---

## TECHNICAL ARCHITECTURE

### Data Source
- SQLite megabase.db (4,308 conversations, 397 ideas, 1,825 tagged)
- Ideas table: name, category, maturity, description, conversation_id
- Tags for theme routing
- Summaries for card copy
- Sentiment for emotional context

### Image Pipeline
- Tier 1: Extract DALL-E URLs from conversations.json (already on disk)
- Tier 2: Wikimedia Commons API for public domain historical art
  (search by: "alchemy engraving", "medieval manuscript illumination", etc.)
- Tier 3: AI-generated themed headers using conversation summary as prompt
- Store in static/images/ or serve from CDN
- Fallback: colored gradient with icon per theme

### Routing
- / — Dream Wall (card mosaic)
- /dream/<id> — Expanded dream card
- /theme/<tag> — Rabbit hole view
- /viz — Data visualizations (already built)
- /conversation/<id> — Full conversation (already built)

### Deployment Target
- Static export possible (for GitHub Pages / Netlify)
- Or keep as Flask app for dynamic queries
- Consider: pre-render dream cards as static HTML for speed

---

## PRODUCT VISION (for selling the workflow)

### What You're Selling
Not the website. The PROCESS:
1. Export your social media data (ChatGPT, Facebook, SMS, Gmail, etc.)
2. Run Dreambase ingestion pipeline
3. Get: searchable archive + idea catalog + sentiment analysis + visualizations
4. Browse your own intellectual history as a beautiful artifact

### Target Users
- Prolific LLM users who want to mine their chat history
- Digital humanities researchers
- People going through life transitions who want to understand their own patterns
- Creators who have 1000 ideas scattered across 10 apps

### Differentiator
- Not a backup tool (you already have the data)
- Not an AI wrapper (the value is in YOUR data, not another chatbot)
- It's a MIRROR — "here's what you've been thinking about for 2 years"

---

## 20 QUESTIONS FOR TED

### Visual Identity
1. **Color mood**: The current dark theme is functional. Do you want to keep it dark
   (night sky / observatory vibe), go warm dark (parchment-on-dark / manuscript vibe),
   or something else entirely?

2. **Typography character**: Should headings feel modern-clean (Inter, Helvetica),
   literary-bookish (Georgia, Garamond), or hand-drawn-playful (xkcd's font is
   actually a handwriting font called "xkcd Script")?

3. **Illustration style**: For dream cards, what's the mix?
   a) Mostly historical art (engravings, manuscripts, alchemical diagrams)
   b) Mostly AI-generated themed images
   c) Abstract/geometric (colored shapes encoding data)
   d) Hand-drawn sketch style (xkcd-adjacent)

4. **Mascot or no?** xkcd has stick figures. Do you want a recurring character
   (a little alchemist? a PKD android? a pixel sprite?) or keep it character-free?

### Navigation & UX
5. **Entry point**: When someone first arrives, do they see ALL dreams at once
   (wall of cards), a curated "top 10" highlights, or a single featured dream
   with navigation to browse?

6. **Theme navigation**: Buttons along the top (horizontal tabs), a sidebar tree,
   floating filter pills, or something more unusual (a constellation map you
   click into)?

7. **Depth model**: How deep should rabbit holes go?
   a) 2 levels (theme -> dream card -> conversation)
   b) 3 levels (theme -> sub-theme -> dream card -> conversation)
   c) Infinite (every dream links to related dreams, no fixed hierarchy)

8. **Search prominence**: Is full-text search a primary feature (big search bar)
   or secondary (hidden behind an icon, since browsing is the point)?

### Content Curation
9. **How many dream cards for v1?** Your database has 397 ideas. Do you want:
   a) All 397 as cards (comprehensive but possibly overwhelming)
   b) Top 100 hand-curated (your original vision)
   c) Start with 50, grow over time
   d) Let the user configure a threshold

10. **Curation method**: Will you hand-pick the top 100, or should the system
    auto-rank by some signal (most pages discussed, highest maturity, most
    tag connections)?

11. **Personal vs. public**: Some dreams involve personal topics (therapy, anxiety,
    relationships). Should the product version:
    a) Include everything (radical transparency)
    b) Auto-filter personal tags
    c) Let the user mark cards as private/public

12. **Conversation excerpts**: When showing the source conversation on a dream card,
    how much?
    a) Just the 3-sentence summary
    b) Key quotes (auto-extracted or hand-picked)
    c) Full conversation available behind a click
    d) Chunked deep reading (existing chunk.py output)

### Tone & Humor
13. **Humor density**: xkcd puts a joke in every panel. How much humor do you want?
    a) Witty subtitles on every section (like the viz pane subtitles)
    b) Occasional easter eggs and empty-state jokes
    c) Dedicated "commentary" layer (like xkcd alt-text)
    d) Keep it serious — let the data speak

14. **Voice**: Who's narrating the dream cards?
    a) First person ("I wanted to build a game where...")
    b) Third person observer ("Ted explored the idea of...")
    c) The dream itself speaks ("I am a game that never got built...")
    d) No narrator — just title, tags, summary, data

15. **Self-awareness level**: How much meta-commentary?
    a) "397 ideas, 10 built. The graveyard of ambition."
    b) "Here's what I was thinking about in October 2024."
    c) No meta — just the content
    d) Full xkcd: every section has a self-aware subtitle

### Data & Visualization
16. **Viz integration**: Should visualizations live on their own page (/viz)
    or be embedded within dream cards and theme pages?
    a) Separate page (current design)
    b) Mini-viz on each theme page (e.g., sentiment river for alchemy conversations)
    c) Both — full dashboard + contextual mini-viz
    d) Viz IS the navigation (click a node in the constellation to enter a theme)

17. **Sentiment display**: How prominent should emotional data be?
    a) Subtle (colored dots, background tints)
    b) Explicit (sentiment scores, emotional arc charts)
    c) Narrative ("this conversation started anxious and ended hopeful")
    d) Hidden by default, available on demand

18. **Temporal dimension**: Should the dream wall show WHEN dreams happened?
    a) Yes — arrange cards chronologically
    b) No — arrange by theme/category
    c) Toggle between both views
    d) Timeline as a separate visualization (current approach)

### Product & Distribution
19. **Target format for v1 of the sellable product**:
    a) Open-source Python toolkit (run locally, keep your data private)
    b) Hosted web app (upload your data, get a Dreambase)
    c) Desktop app (Electron/Tauri)
    d) Just the methodology + template (a guide, not software)

20. **What's the one screenshot that sells this?** If you could show ONE view
    to a potential user and have them say "I want that for MY data" — which
    visualization or page is it?
    a) The dream wall with beautiful card illustrations
    b) The topic constellation showing their brain's wiring
    c) The sentiment river showing their emotional arc over years
    d) The sparkline table showing all their themes at a glance
    e) Something else entirely
```

---

## Writing Templates and Style Guides
**File:** `DREAMBASE_TEMPLATES.md` (15,809 chars)

```md
# Dreambase: Writing Templates, Style Guides & Narrative Design Patterns

**Mary Anne Dominic Template System** — structured templates for every content type
in the Dreambase ecosystem, plus a narrative designer's guide to using the database
as a storytelling engine.

---

## TEMPLATE 1: Dream Card (Compact)

**AUDIENCE:** Browser/visitor scanning the Dream Wall
**TOTAL TARGET:** 50-80 words
**TONE:** Evocative, curious, inviting

### Required Elements
- **Title** (3-7 words, evocative not descriptive)
- **Hook** (1 sentence that makes someone want to click)
- **Summary** (3 sentences: what is it, why does it matter, where did it go)
- **Tags** (2-4 theme tags)
- **Maturity badge** (sketch / design / prototype / built)

### Template
```
TITLE: [verb-noun or mystery-phrase, e.g. "The Alchemy Board Game"]
HOOK: [question or provocative claim, e.g. "What if transmutation was a game mechanic?"]
SUMMARY:
  Sentence 1: [WHAT — describe the core idea in plain language]
  Sentence 2: [WHY — why this matters or what makes it interesting]
  Sentence 3: [WHERE — where did it go? Still a sketch? Built? Abandoned?]
TAGS: [tag1, tag2, tag3]
MATURITY: [sketch | design | prototype | built]
```

### Anti-Patterns
- "This conversation discusses..." (boring, passive — write like a curator, not an indexer)
- Tags that are too generic ("coding", "ideas") — be specific ("procedural_generation", "alchemy")
- Summaries that describe the conversation instead of the idea

### Example Opening
GOOD: "The Alchemy Board Game" / "What if transmutation was a game mechanic?"
BAD: "Conversation about making a board game with alchemy theme" / "This discusses alchemy-themed games."

---

## TEMPLATE 2: Showcase Page (Tabbed Deep Dive)

**AUDIENCE:** Someone who clicked a dream card and wants the full story
**TOTAL TARGET:** 1,500-3,000 words across all tabs
**TONE:** Intellectual but accessible, xkcd humor in margins, Tufte density in data

### Tab: Overview (500-800 words)

```
NARRATIVE:
  Paragraph 1: [THE HOOK — what is this dream and why should anyone care?
    Write in third person present. "Ted explores the idea of..." not
    "I wanted to build..."]

  Paragraph 2: [THE DESIGN — what makes the core mechanic interesting?
    Connect to game design principles. Reference specific conversations
    where key decisions were made.]

  Paragraph 3: [THE EVOLUTION — how did this idea change over time?
    What started as X became Y when Z happened. Show the intellectual
    journey, not just the endpoint.]

  Paragraph 4: [THE PEDAGOGY — what does this game teach? Not what it
    teaches ABOUT, but what cognitive skill the mechanic develops.
    "The player learns X by doing Y" not "The game is about X."]

  Paragraph 5 (optional): [THE VISION — where could this go? What would
    a finished version look like? What's the one-screenshot pitch?]

PEDAGOGY BOX:
  Concept: [what the game teaches]
  Mechanic: [which game mechanic maps to the concept]
  Difficulty Easy: [simplified version]
  Difficulty Medium: [standard version]
  Difficulty Hard: [full complexity]
```

**Required:** Paragraphs 1-3, Pedagogy Box
**Optional:** Paragraphs 4-5
**Anti-pattern:** Don't write a feature list. Write a story.

### Tab: Design Evolution (timeline entries)

```
For each significant conversation:

DATE: [YYYY-MM-DD]
TITLE: [conversation title]
DESCRIPTION: [1-2 sentences — what happened, what decision was made.
  Use active voice: "Introduced the transmutation chain mechanic" not
  "The transmutation chain mechanic was discussed."]
CONVERSATION_ID: [database ID for link]
```

**Anti-pattern:** Don't list every conversation. Pick the 5-8 that represent
genuine evolution points. Skip conversations that just refined existing ideas
without changing direction.

### Tab: Key Quotes (3-8 quotes)

```
QUOTE: "[exact text, max 50 words — pick moments of creative energy,
  surprising insight, or design breakthrough]"
ROLE: [user | assistant]
CONVERSATION: [title]
CONVERSATION_ID: [database ID]
```

**Selection criteria:**
- Moments where the design clicked ("what if we...")
- Surprising connections between domains
- Self-aware humor or meta-commentary
- Honest doubt or creative tension

**Anti-pattern:** Don't pick quotes that are just descriptions. Pick quotes
that show thinking-in-progress.

### Tab: Gallery

```
For each image:

URL: [path or external URL]
CAPTION: [1 sentence describing what this shows and why it matters]
SOURCE: [dall-e | wikimedia | concept-art | screenshot]
```

**Sources in priority order:**
1. DALL-E images extracted from ChatGPT conversations (already generated)
2. Public domain art from Wikimedia Commons (alchemical diagrams, medieval manuscripts)
3. Screenshots of any prototypes or mockups
4. AI-generated concept art (v2)

### Tab: Source Conversations

Auto-populated from database. No template needed.

---

## TEMPLATE 3: Theme Description (Rabbit Hole Header)

**AUDIENCE:** Someone navigating by theme (alchemy, games, esoteric, etc.)
**TOTAL TARGET:** 40-60 words
**TONE:** Intellectual but accessible, curious not pretentious

```
THEME: [theme name]
DESCRIPTION:
  Sentence 1: [What this theme covers — be specific, not generic]
  Sentence 2: [Why this matters to Ted / "why this matters to me" personal angle]
DREAM_COUNT: [auto-populated]
CONVERSATION_COUNT: [auto-populated]
```

### Examples

GOOD:
```
THEME: Alchemy
DESCRIPTION: The art of transformation — not just lead-into-gold, but
  the deeper question of how systems change state. Ted keeps returning
  to alchemy because it's the oldest framework for thinking about
  game mechanics, learning progressions, and creative process.
```

BAD:
```
THEME: Alchemy
DESCRIPTION: Conversations about alchemy topics. Various discussions
  related to alchemical themes.
```

---

## TEMPLATE 4: Database Entry Templates

### Idea Record

```sql
-- Template for manually adding an idea to the database
INSERT INTO ideas (conversation_id, name, category, description, maturity, method, created_at)
VALUES (
  [conversation_id],     -- Link to source conversation
  '[idea name]',         -- 3-7 words, evocative
  '[category]',          -- game | app | educational | product
  '[description]',       -- 1-2 sentences: what is it, what makes it interesting
  '[maturity]',          -- sketch | design | prototype | built
  'manual',              -- method: manual curation
  '[YYYY-MM-DD]'         -- when the idea first appeared
);
```

### Showcase JSON Sidecar

After ChatGPT batch reading, save responses as `showcases/<slug>.json`:

```json
{
  "narrative": "<p>Paragraph 1...</p><p>Paragraph 2...</p>",
  "timeline_entries": [
    {
      "date": "2025-01-03",
      "title": "First conversation title",
      "description": "What happened and what was decided.",
      "conversation_id": 40
    }
  ],
  "quotes": [
    {
      "text": "The exact quote from the conversation.",
      "role": "user",
      "conversation_title": "Conversation Title",
      "conversation_id": 40
    }
  ],
  "images": [
    {
      "url": "/static/images/showcase/bubble-bog-witch-01.png",
      "caption": "DALL-E concept art of the Bog Witch emerging from bubbles."
    }
  ]
}
```

### Tag Record

```sql
-- When tagging conversations manually or adding new themes
INSERT OR IGNORE INTO tags (name) VALUES ('[tag_name]');

INSERT OR REPLACE INTO conversation_tags (conversation_id, tag_id, confidence, method)
VALUES (
  [conv_id],
  (SELECT id FROM tags WHERE name='[tag_name]'),
  0.9,        -- confidence: 0.7 for keyword, 0.9 for manual/LLM
  'manual'    -- method: keyword | llm | folder_name | manual
);
```

---

## STYLE GUIDE: Dreambase Voice

### The Three Registers

**1. Curator Voice** (dream cards, theme descriptions, showcase narratives)
- Third person present: "Ted explores..." not "I wanted..."
- Intellectual but warm — a museum placard written by someone who cares
- Show the thinking, not just the result
- Never explain what a conversation "discusses" — describe what it DISCOVERS

**2. xkcd Voice** (subtitles, empty states, tooltips, UI microcopy)
- Self-deprecating humor about the absurdity of the data
- "397 ideas, 10 built. The graveyard of ambition."
- "No dreams here yet. You were probably touching grass that week."
- Every subtitle should make the reader smile without undermining the data
- Alt-text/tooltips with bonus commentary (xkcd's signature move)

**3. Data Voice** (visualizations, sparkline tables, statistics)
- Tufte discipline: every word encodes information
- Direct labeling, no legends floating off to the side
- Numbers speak for themselves — "662 pages" hits harder than "a very long conversation"
- Context makes numbers meaningful: "662 pages — longer than War and Peace"

### Rabbit Hole Navigation Copy

Per DREAMBASE_DESIGN_TEMPLATE.md:
- Button labels should be inviting: **"Go deeper"** not "View more"
- Theme transitions: **"This dream also touches on..."** not "Related tags:"
- Dead ends acknowledged: **"This rabbit hole loops back to [X]"**
- Connections between dreams: **"Born in the same conversation as..."**

### Words to Use
- discover, explore, haunt, unearth, trace, evolve, emerge, converge
- dream, vision, obsession, rabbit hole, constellation
- transmute, transform, iterate, prototype

### Words to Avoid
- discuss, conversation (too meta — the user knows they're reading conversations)
- interesting (show, don't tell)
- various, multiple, several (be specific: "7 conversations across 3 months")
- simple, just, basically (dismissive of the work)

---

## TEMPLATE 5: Narrative Designer's Guide to Dreambase

**How a narrative designer would use this database to build story-driven projects.**

### The Premise

You have 4,308 conversations, 397 ideas, 1,825 tagged threads, and 3.9 million
messages spanning 2+ years of one person's intellectual life. This isn't a
database — it's a primary source archive. Here's how a narrative designer
would mine it.

### Strategy 1: Character Arc Through Data

The database contains a protagonist (Ted) whose interests, skills, and
creative ambitions evolved over time. A narrative designer would:

1. **Pull the sentiment river** for emotional arc across months
2. **Track topic frequency** to see what obsessions wax and wane
3. **Find convergence points** — months where alchemy + games + coding
   all peak simultaneously = creative breakthroughs
4. **Identify "dark periods"** — gaps in activity, negative sentiment runs,
   abandoned ideas = tension in the narrative

**Query pattern:**
```sql
-- Find the month with the most diverse creative activity
SELECT substr(c.created_at,1,7) as month,
       count(DISTINCT t.name) as unique_tags,
       count(DISTINCT c.id) as conversations
FROM conversations c
JOIN conversation_tags ct ON ct.conversation_id=c.id
JOIN tags t ON t.id=ct.tag_id
WHERE c.created_at >= '2024-01-01'
GROUP BY month ORDER BY unique_tags DESC LIMIT 10;
```

### Strategy 2: Idea Genealogy

Every idea has ancestors. The Alchemy Board Game didn't appear from nothing —
it descended from conversations about:
- Alchemy as a system of transformation (esoteric interest)
- Game mechanics that teach through play (pedagogy interest)
- Board games as physical artifacts (craft interest)

A narrative designer traces these genealogies:

1. **Find the first mention** of each idea's key concepts
2. **Map the cross-pollination** — which conversations from different domains
   fed into the same idea?
3. **Build the "creative DNA"** — each idea is a recombination of 2-3 themes

**Query pattern:**
```sql
-- Find conversations that share tags with a specific idea's conversation
SELECT c2.title, c2.created_at, t.name as shared_tag
FROM conversation_tags ct1
JOIN conversation_tags ct2 ON ct1.tag_id=ct2.tag_id
  AND ct1.conversation_id != ct2.conversation_id
JOIN conversations c2 ON c2.id=ct2.conversation_id
JOIN tags t ON t.id=ct1.tag_id
WHERE ct1.conversation_id = [idea_conversation_id]
ORDER BY c2.created_at;
```

### Strategy 3: The Unreliable Narrator

Ted's memory of his own creative history is incomplete and sometimes wrong
(see: "I could have sworn I already did work on gmail"). A narrative designer
would exploit this:

1. **Compare what Ted says he worked on** vs **what the data shows**
2. **Find forgotten ideas** — things discussed passionately in 2024 that
   never appear again in 2025
3. **Find false memories** — ideas Ted attributes to one period that
   actually originated elsewhere
4. **Find the idea that won't die** — concepts that keep reappearing
   across different projects under different names

### Strategy 4: The Showcase as Narrative Structure

Each showcase page IS a short story:
- **Act 1 (Overview):** Meet the idea. What is it? Why does it matter?
- **Act 2 (Design Evolution):** Watch it struggle. Pivots, dead ends, breakthroughs.
- **Act 3 (Key Quotes):** Hear the protagonist's voice in the moment.
- **Epilogue (Gallery):** See what it looks like. Or what it COULD look like.
- **Appendix (Sources):** The primary sources, for the reader who wants to
  go deeper than the narrator went.

The tabbed structure isn't just UI convenience — it's narrative pacing.
The reader chooses their own depth. Some will skim the overview. Others
will read every source conversation. The showcase page accommodates both
without forcing either.

### Strategy 5: The Product Narrative

If Dreambase becomes a product ("help people mine their own social media data"),
the narrative designer's job is to answer: **what story does YOUR data tell?**

The template:
1. **Ingest** — "Here's everything you've said for 2 years"
2. **Discover** — "Here are the 10 ideas you kept coming back to"
3. **Confront** — "Here's how much time you spent on X vs Y"
4. **Decide** — "Here's which dreams are still alive and which you abandoned"

This is the emotional arc of the product: curiosity, discovery, honest
self-reflection, and then action. The database isn't the product.
The MIRROR is the product.

---

## TEMPLATE 6: Values Evidence Card

For the proposed Values tab — summarizing scholarly and engineering values
with evidence links that rabbit-hole into the database.

**AUDIENCE:** Ted (self-reflection) or potential collaborators/clients
**TOTAL TARGET:** 100-150 words per value
**TONE:** Curator voice, evidence-first

```
VALUE: [name, 3-5 words, e.g. "Games That Teach Themselves"]

CLAIM: [1 sentence — what Ted believes about this topic.
  Not "I value X" but "X works because Y."]

EVIDENCE: [2-3 specific database references]
  - [conversation title] ([pages]p, [date]) — [what it demonstrates]
  - [conversation title] ([pages]p, [date]) — [what it demonstrates]
  - [idea name] ([maturity]) — [what it demonstrates]

RABBIT HOLE: [which theme or tag to explore for more]

COUNTER-EVIDENCE (optional): [honest acknowledgment of tension
  or contradiction in the data — shows intellectual honesty]
```

### Example

```
VALUE: Implicit Pedagogy Over Explicit Tutorial

CLAIM: The best game mechanics teach through play, not through text boxes.
  If you need a tutorial popup to explain the mechanic, the level design failed.

EVIDENCE:
  - "Bubble Witch Platformer Ideas" (30p, 2025-01) — 122 messages designing
    bubble mechanics that communicate zone properties without text
  - "Games Learning Alchemy Board Game" (241p) — transmutation discovery
    as the core loop, deliberately hiding the complete transformation graph
  - "Snake Autobattler Concept" (29p, 2025-01) — post-battle replay as
    the teaching mechanism, not pre-battle instructions

RABBIT HOLE: game_idea + educational tags (47 conversations)

COUNTER-EVIDENCE: "Alchemy Game Tutorial Design" (137p) exists — sometimes
  even implicit-pedagogy advocates need to write a tutorial. The tension
  between these positions IS the design challenge.
```
```

---

## Prompting Methodology Evaluation
**File:** `PROMPTING_EVALUATION.md` (15,743 chars)

```md
# Dreambase Build: Prompting Methodology Evaluation

## Overview

Ted used a structured "PKD Planning Protocol" — a system of 33 named slash
commands organized by role (scope, slice, boundary, tokens, audit, etc.) — to
plan and build a personal knowledge archaeology system across 8+ sessions.
This is notably more methodical than typical conversational prompting.

**Overall assessment: 8.5/10** — The planning discipline prevented scope creep
and produced a working system with 15 scripts, 4,308 conversations ingested,
and 7 data visualizations. The main cost was token overhead from planning
prompts that sometimes overlapped or triggered unnecessary ceremony.

---

## Prompt-by-Prompt Narrative

### Prompt 1: "Find everything database on my computer"
**Score: 9/10**

The opening move was excellent — an open-ended exploration request that let
Claude discover the actual data landscape rather than Ted guessing what
existed. This produced the crucial inventory of 10+ data sources across
Desktop, Downloads, and Dev.

**What worked:** Gave Claude permission to search broadly. Didn't
pre-constrain the scope.
**Minor issue:** The phrase "everything database" was slightly ambiguous
(databases? or everything + data?), but context made it clear enough.

---

### Prompt 2: "I've also got pdf and html file collections..."
**Score: 8/10**

Good follow-up that expanded the discovery to non-database formats. This
surfaced the LLM logs HTML/PDF collection (1,703 files) that became a
major data source.

**What worked:** Explicitly named the formats Ted remembered.
**Could improve:** Could have said "check these specific directories" to
speed up the search.

---

### Prompt 3: `/plan-joe-chip-scope` — "how feasible is a megafile + idea catalog"
**Score: 9/10**

This was the key disciplined moment. Instead of saying "build it," Ted invoked
the scope-freeze skill FIRST. This forced explicit feasibility analysis and
prevented the classic "just start coding" trap.

**What worked:** The skill invocation made Claude produce a structured scope
document rather than diving into code. Established the 8-session plan, the
agent roles, and the unified schema before a single line was written.
**Result:** The plan survived nearly intact across all sessions.

---

### Prompt 4: `/plan-isidore-tokens` — "plan for doing this without running out of tokens"
**Score: 9/10**

Brilliant meta-prompt. Ted recognized that the project's biggest risk wasn't
technical — it was running out of context window. Isidore produced the
token budget analysis that shaped the entire build strategy: scripts write
to DB not stdout, errors go to log files, test with samples then bulk-run
in background.

**What worked:** Addressed the real constraint (context window, not
computation). Produced actionable rules that were followed throughout.
**Result:** The project completed without context exhaustion until the
very end (session 8+), which is remarkable for a project of this scope.

---

### Prompt 5: "the gmail data exists in some converted form"
**Score: 7/10**

A good intuition-based redirect that saved time — Ted suspected he'd already
processed Gmail elsewhere and flagged it. This prevented wasting a session
on 14GB mbox parsing that might have been redundant.

**Problem:** The memory was vague. "I might have used Antigravity" — this
turned out to be a false lead. The actual Gmail processing was `mbox_to_csv.py`
in Downloads. More precision would have helped: "search for any gmail or
mbox scripts I already wrote."

---

### Prompt 6: "card with the topic sketched in three sentences..."
**Score: 10/10**

The highest-scoring prompt. Ted articulated the EXACT user experience he
wanted: cards with 3-sentence summaries, click to expand, rabbit hole
navigation, distant reading for 1000-page conversations. This became the
north star for the entire Flask UI.

**What worked:** Specific enough to implement, abstract enough to leave
room for design. The "distant reading" framing showed Claude the
intellectual context. "Some conversations are a thousand pages" — this
single detail shaped the chunker's 60K-char design and the page-count
sorting.

---

### Prompt 7: `/plan-pris-pedagogy` — "what I want to learn from reviewing"
**Score: 7/10**

Invoked the pedagogy skill to reflect on learning goals. This was
intellectually valuable but didn't translate directly into code artifacts.
The sentiment analysis and personal message mining features came from this
prompt, but they would have emerged anyway from the scope document.

**Token cost concern:** This was the first prompt where skill ceremony
consumed context without proportional output. The pedagogy skill produced
a thoughtful analysis, but the actionable items (VADER sentiment,
emotional arc prompts) were already in the plan.

---

### Prompt 8: `/plan-deckard-boundary` — "deterministic and probabilistic hybrid"
**Score: 8/10**

Smart architectural prompt. Deckard's deterministic/probabilistic boundary
analysis produced the core design decision: keyword tagging + VADER + FTS5
first (free, instant), then targeted LLM for summaries/classification.
This directly shaped the token-budget tiers.

**What worked:** The "help me think about" framing was collaborative, not
prescriptive. Produced the tiered approach that let Ted control costs.
**Could improve:** Some overlap with Isidore's token analysis. Could have
been combined.

---

### Prompt 9: "8 sessions is not too much"
**Score: 8/10**

A simple but crucial approval prompt. Ted confirmed the scope was acceptable,
which locked in the session plan. Short, decisive, no wasted tokens.

---

### Prompt 10: `/plan-eldritch-swarm` — "break down into different roles"
**Score: 8/10**

The Eldritch Swarm skill produced the 6-agent architecture (Architect,
Ingestors, Indexer, Summarizer, Chunker, Browser) with a clear dependency
graph. This was genuinely useful — the parallel ingestor design and the
phase-gated pipeline came from this.

**What worked:** The agent decomposition prevented monolithic script design.
**Slight excess:** The swarm metaphor added flavor but the actual output was
a standard pipeline diagram. A simpler "break this into scripts" might have
produced the same architecture.

---

### Prompt 11: "I don't want to use the API I'm on the 100/mo plan"
**Score: 10/10**

A critical constraint injection at exactly the right time. This single
sentence rewrote the entire summarization strategy from "call Haiku API"
to "ChatGPT batch workflow." It also prevented any future API-cost
assumptions.

**What worked:** Short, clear, constraint-first. Didn't ask for permission
or hedge — just stated the boundary.

---

### Prompt 12: "125 paste-and-copy interactions is too much work"
**Score: 9/10**

Excellent pushback on a proposed workflow. Ted identified that the batch
summarization plan (125 ChatGPT paste sessions) was impractical and demanded
optimization. This led to bigger batches (50 per file instead of 20),
prioritized by tags, reducing the workload to ~24 focused sessions.

**What worked:** Quantified the complaint. "125 is too much" is more
actionable than "this seems like a lot of work."

---

### Prompt 13: "bigger batches, prioritized and I'll tell you what to have claude do"
**Score: 8/10**

Good follow-up that established the human-in-the-loop pattern: Ted decides
WHAT gets deep-read, Claude generates the batch files, Ted pastes into
ChatGPT. Clean division of labor.

---

### Prompt 14: "100 creative dreams as a website of cards..."
**Score: 7/10**

This was the first scope-expansion prompt. Ted described the dream catalog
website with theme buttons and rabbit holes. It was a great vision but
violated the Joe Chip scope freeze.

**Problem:** This should have triggered `/plan-abendsen-parking` (parking
lot) immediately, but Ted described it in enough detail that it became a
de facto commitment. The discipline would have been: state the vision in
one sentence, park it, continue building.

**What helped:** Ted self-corrected: "Let's be careful to plan before building."

---

### Prompt 15: `/plan-buckman-critic` — evaluate process for flaws
**Score: 8/10**

Good meta-reflection. Using the critic skill mid-build caught several
potential issues and validated the approach. This is the kind of
checkpoint prompt that most users skip.

---

### Prompt 16: `/failure-audit` — "concerned about stuff getting wiped"
**Score: 9/10**

This was triggered by a REAL incident — the PKD ingestor accidentally
deleted all 982 HTML conversations by importing from the wrong module.
Ted's response was exactly right: pause, audit for failure modes, tighten
before continuing.

**What worked:** Reacted to a concrete problem rather than abstract anxiety.
Led to the backup strategy (`cp megabase.db megabase_label.db`) and the
rule against importing ingest functions across scripts.
**Problem in the prompt:** "don't want to hear about wasted effort" was
slightly defensive. The wasted effort had already happened — what mattered
was preventing recurrence.

---

### Prompt 17: "hold off on gmail"
**Score: 8/10**

Correct prioritization call. Gmail was the biggest and riskiest ingestor
(14GB mbox), and Ted's instinct that he'd already processed it elsewhere
was partly right (the CSV existed). Deferring it saved a session.

---

### Prompt 18: "go"
**Score: 10/10**

The most efficient prompt in the entire project. One word. Meaning: "I've
reviewed everything, the plan is good, continue building." Maximum signal,
minimum tokens.

---

### Prompt 19: "change the name from Megabase to Dreambase"
**Score: 9/10**

Good rebranding prompt with context: "the concept is to haunt my records
to learn about what I want and eventually sell this workflow as a product."
This wasn't just a rename — it reframed the entire project from a personal
tool to a potential product.

**What worked:** Gave the WHY alongside the WHAT.

---

### Prompt 20: "let's try all the visualizations"
**Score: 8/10**

Ambitious scope expansion but well-timed — the core was built, the UI was
working, and visualizations are high-impact/low-risk. The "separate panes,
easily hideable" specification was perfect for implementation.

**Could improve:** Didn't specify which visualizations mattered most. "All 7"
is a lot — prioritizing 3 would have been more Tufte.

---

### Prompt 21: "xkcd comic meets infographic sense of humor"
**Score: 9/10**

Excellent creative direction delivered as a single sentence. This immediately
shaped the subtitle copy on every visualization pane ("the days you couldn't
stop talking to computers") and will guide the entire Dreambase tone.

---

### Prompt 22: Images from ChatGPT + historical sources
**Score: 7/10**

Good vision but came at the wrong time — mid-build of visualizations. This
is a classic Abendsen Parking moment. The question was worth asking, but
should have been flagged as "v2" rather than explored immediately.

---

### Prompt 23: "rabbit hole web design template + 20 questions"
**Score: 8/10**

Smart meta-prompt: instead of making all the design decisions himself, Ted
asked Claude to generate the decision space as questions. This is a good
"diverge before converge" strategy.

**What worked:** "20 questions" forced comprehensive coverage of visual,
UX, content, and product dimensions.
**Could improve:** 20 is a lot of questions to answer at once. Grouping
into "answer these 5 first" would make it more actionable.

---

### Prompt 24: This evaluation prompt
**Score: 9/10**

Asking for a retrospective evaluation of your own prompting methodology is
unusually self-aware. Most users never reflect on HOW they prompted, only
on WHAT they got. This kind of meta-analysis is how you improve the skill.

---

## PATTERNS OBSERVED

### What Ted Does Well
1. **Constraint injection** — "no API," "8 sessions is fine," "hold off on gmail."
   These short boundary statements saved more tokens than any planning skill.
2. **Skill-first planning** — Using Joe Chip scope freeze before coding prevented
   the most common failure mode: building the wrong thing.
3. **Quantified pushback** — "125 interactions is too much" is more useful than
   "this seems hard." Numbers enable optimization.
4. **The one-word prompt** — "go" is underrated. It communicates trust + approval
   + urgency in minimum tokens.
5. **Mid-build audits** — The failure-audit and Buckman-critic calls caught real
   issues before they compounded.

### What Could Improve
1. **Skill overlap** — Isidore (tokens) + Deckard (boundary) + Pris (pedagogy)
   all ran in the planning phase and produced partially overlapping outputs.
   Cost: ~3000-5000 tokens of redundant analysis. Fix: combine related skills
   into a single planning pass.
2. **Scope creep via enthusiasm** — The dream catalog, images, rabbit holes,
   and product vision all entered mid-build. Each was individually reasonable
   but collectively they expanded the project from "unified database + browser"
   to "productizable dream visualization platform." The parking lot skill
   existed but wasn't used aggressively enough.
3. **Vague memory references** — "I could have sworn I already did work on
   gmail in some kind of converted form or llm reading it" — this cost a
   search and a deferred task. More precise: "search Downloads for any
   gmail or mbox python scripts."
4. **All-at-once vs. prioritized** — "try all the visualizations" and
   "20 questions" are comprehensive but produce a lot of output to process.
   Batching in groups of 3-5 would make each round more actionable.

### The PKD Skill System's Value
The named skills (Joe Chip, Isidore, Deckard, Eldritch Swarm, Buckman,
Abendsen) provided genuine value as COGNITIVE TRIGGERS — they forced
Ted to think about scope, tokens, boundaries, and failure modes at the
right moments. The actual skill instructions were secondary to the ACT
of invoking them, which created deliberate pause points in what would
otherwise be a continuous stream of "build build build."

**Estimated token savings from planning discipline: 30-50%** compared to
an unplanned approach that would have required more backtracking,
re-ingestion, and architectural rework.

---

## SCORE SUMMARY

| # | Prompt | Score | Key Strength |
|---|--------|-------|-------------|
| 1 | "find everything database" | 9 | Open exploration |
| 2 | "pdf and html collections" | 8 | Format awareness |
| 3 | /plan-joe-chip-scope | 9 | Scope discipline |
| 4 | /plan-isidore-tokens | 9 | Meta-constraint |
| 5 | "gmail in converted form" | 7 | Intuition (vague) |
| 6 | "card with 3 sentences" | 10 | Perfect UX spec |
| 7 | /plan-pris-pedagogy | 7 | Intellectually rich, low ROI |
| 8 | /plan-deckard-boundary | 8 | Architecture |
| 9 | "8 sessions is fine" | 8 | Decisive approval |
| 10 | /plan-eldritch-swarm | 8 | Agent decomposition |
| 11 | "no API, 100/mo plan" | 10 | Critical constraint |
| 12 | "125 is too much work" | 9 | Quantified pushback |
| 13 | "bigger batches, I'll direct" | 8 | Human-in-the-loop |
| 14 | "100 creative dreams website" | 7 | Vision (scope creep) |
| 15 | /plan-buckman-critic | 8 | Mid-build checkpoint |
| 16 | /failure-audit | 9 | Incident response |
| 17 | "hold off on gmail" | 8 | Correct deferral |
| 18 | "go" | 10 | Maximum efficiency |
| 19 | "rename to Dreambase" | 9 | Vision + context |
| 20 | "all 7 visualizations" | 8 | Ambitious (unprioritized) |
| 21 | "xkcd humor" | 9 | Creative direction |
| 22 | "images + historical sources" | 7 | Wrong timing |
| 23 | "template + 20 questions" | 8 | Diverge-before-converge |
| 24 | "evaluate my prompting" | 9 | Meta-reflection |

**Average: 8.4/10**
**Weighted by impact: 8.7/10** (the high-scoring constraint prompts
mattered more than the lower-scoring exploratory ones)
```

---

