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
