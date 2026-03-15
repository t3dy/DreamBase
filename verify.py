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
