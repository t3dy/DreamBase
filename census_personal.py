"""
Agent K1: Personal Archive Census

Deterministic analysis of SMS, Facebook, Google Chat, Twitter.
For each source: top 20 threads by message count, sentiment arc
(monthly averages), named contacts, date ranges.
All from existing DB data — no reading required.

Outputs personal_census.json.
"""

import json
import os
import sqlite3
from collections import defaultdict

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "megabase.db")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personal_census.json")

PERSONAL_SOURCES = ["sms", "facebook", "google_chat", "twitter"]


def get_source_stats(conn, source_name):
    """Get overall stats for a source."""
    row = conn.execute("""
        SELECT count(c.id), sum(c.estimated_pages), sum(c.message_count),
               min(c.created_at), max(c.updated_at)
        FROM conversations c
        JOIN sources s ON c.source_id = s.id
        WHERE s.name = ?
    """, (source_name,)).fetchone()

    return {
        "conversation_count": row[0],
        "total_pages": round(row[1] or 0, 1),
        "total_messages": row[2] or 0,
        "earliest_date": row[3],
        "latest_date": row[4],
    }


def get_top_threads(conn, source_name, limit=20):
    """Get top threads by message count, deduplicated by title (keep highest message count)."""
    rows = conn.execute("""
        SELECT c.id, c.title, c.estimated_pages, c.message_count,
               c.created_at, c.updated_at, c.summary
        FROM conversations c
        JOIN sources s ON c.source_id = s.id
        WHERE s.name = ?
        ORDER BY c.message_count DESC
    """, (source_name,)).fetchall()

    # Deduplicate: keep only the first (highest msg count) per title
    seen_titles = set()
    deduped = []
    for row in rows:
        title = row[1]
        if title in seen_titles:
            continue
        seen_titles.add(title)
        deduped.append({
            "id": row[0],
            "title": title,
            "pages": round(row[2] or 0, 1),
            "message_count": row[3] or 0,
            "created_at": row[4],
            "updated_at": row[5],
            "summary_preview": (row[6] or "")[:200],
        })
        if len(deduped) >= limit:
            break

    return deduped


def get_unique_contacts(conn, source_name):
    """Extract unique contact names from conversation titles."""
    rows = conn.execute("""
        SELECT DISTINCT c.title
        FROM conversations c
        JOIN sources s ON c.source_id = s.id
        WHERE s.name = ?
    """, (source_name,)).fetchall()

    contacts = set()
    for (title,) in rows:
        if not title:
            continue
        # Strip source prefix
        name = title
        for prefix in ("SMS: ", "Facebook: "):
            if name.startswith(prefix):
                name = name[len(prefix):]
        # Split group threads
        for part in name.split(", "):
            part = part.strip()
            if part and part != "(Unknown)":
                contacts.add(part)

    return sorted(contacts)


def get_sentiment_arc(conn, source_name):
    """Monthly average sentiment for this source."""
    rows = conn.execute("""
        SELECT substr(m.created_at, 1, 7) as month,
               avg(m.sentiment_vader) as avg_sentiment,
               count(*) as msg_count
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        JOIN sources s ON c.source_id = s.id
        WHERE s.name = ?
          AND m.sentiment_vader IS NOT NULL
          AND m.created_at IS NOT NULL
          AND length(m.created_at) >= 7
        GROUP BY month
        ORDER BY month
    """, (source_name,)).fetchall()

    return [
        {"month": r[0], "avg_sentiment": round(r[1], 4), "message_count": r[2]}
        for r in rows
        if r[0] and len(r[0]) == 7  # valid YYYY-MM
    ]


def get_duplicate_report(conn, source_name):
    """Report duplicate conversation titles within this source."""
    rows = conn.execute("""
        SELECT c.title, count(*) as cnt, sum(c.message_count) as total_msgs
        FROM conversations c
        JOIN sources s ON c.source_id = s.id
        WHERE s.name = ?
        GROUP BY c.title
        HAVING cnt > 1
        ORDER BY cnt DESC
        LIMIT 20
    """, (source_name,)).fetchall()

    return [
        {"title": r[0], "duplicate_count": r[1], "total_messages_across_dupes": r[2]}
        for r in rows
    ]


def main():
    conn = sqlite3.connect(DB_PATH)
    census = {}

    for source in PERSONAL_SOURCES:
        print(f"\n{'='*60}")
        print(f"Processing: {source}")
        print(f"{'='*60}")

        stats = get_source_stats(conn, source)
        print(f"  Conversations: {stats['conversation_count']}")
        print(f"  Pages: {stats['total_pages']:,.0f}")
        print(f"  Messages: {stats['total_messages']:,}")
        print(f"  Date range: {stats['earliest_date']} to {stats['latest_date']}")

        top_threads = get_top_threads(conn, source)
        print(f"  Top threads (deduped): {len(top_threads)}")
        for t in top_threads[:5]:
            title_safe = t['title'][:40].encode('ascii', 'replace').decode()
            print(f"    {t['message_count']:>8} msgs | {t['pages']:>6.0f}p | {title_safe}")

        contacts = get_unique_contacts(conn, source)
        print(f"  Unique contacts: {len(contacts)}")

        sentiment_arc = get_sentiment_arc(conn, source)
        print(f"  Sentiment months: {len(sentiment_arc)}")
        if sentiment_arc:
            sentiments = [s["avg_sentiment"] for s in sentiment_arc]
            print(f"  Sentiment range: {min(sentiments):.3f} to {max(sentiments):.3f}")

        duplicates = get_duplicate_report(conn, source)
        if duplicates:
            print(f"  Duplicate titles: {len(duplicates)} (worst: '{duplicates[0]['title']}' x{duplicates[0]['duplicate_count']})")

        census[source] = {
            "stats": stats,
            "top_threads": top_threads,
            "contacts": contacts,
            "sentiment_arc": sentiment_arc,
            "duplicates": duplicates,
        }

    conn.close()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(census, f, indent=2, ensure_ascii=False)

    print(f"\n\nCensus written to {OUTPUT_PATH}")

    # Summary
    total_pages = sum(census[s]["stats"]["total_pages"] for s in PERSONAL_SOURCES)
    total_msgs = sum(census[s]["stats"]["total_messages"] for s in PERSONAL_SOURCES)
    total_contacts = len(set().union(*(set(census[s]["contacts"]) for s in PERSONAL_SOURCES)))
    print(f"\nPersonal archive total: {total_pages:,.0f} pages, {total_msgs:,} messages, {total_contacts} unique contacts")


if __name__ == "__main__":
    main()
