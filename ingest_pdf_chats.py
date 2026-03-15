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
