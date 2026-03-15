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
