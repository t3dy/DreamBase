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
