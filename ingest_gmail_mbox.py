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
