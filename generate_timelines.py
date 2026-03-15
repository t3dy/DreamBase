"""
Generate timeline_entries and quotes for all showcase/scholar pages.

Timelines are built from conversation created_at dates + titles.
Quotes are extracted from conversation first messages.

Usage:
    python generate_timelines.py --generate   # Generate timelines + quotes JSON
    python generate_timelines.py --apply      # Apply to app.py
"""

import json
import os
import re
import sqlite3
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "megabase.db")
APP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "timelines_quotes.json")


def get_pages_needing_content():
    """Parse app.py for all pages with empty timeline_entries and quotes."""
    with open(APP_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    pages = {}
    pattern = re.compile(
        r'"slug":\s*"([^"]+)".*?"conversation_ids":\s*\[([^\]]*)\]',
        re.DOTALL
    )
    for match in pattern.finditer(text):
        slug = match.group(1)
        ids_str = match.group(2).strip()
        ids = [int(x.strip()) for x in ids_str.split(",") if x.strip()] if ids_str else []
        pos = match.start()
        nearby = text[pos:pos + 5000]
        if '"timeline_entries": []' in nearby:
            pages[slug] = ids
    return pages


def generate_timelines(pages):
    """Build timeline entries from conversation dates."""
    conn = sqlite3.connect(DB_PATH)
    result = {}

    for slug, ids in sorted(pages.items()):
        if not ids:
            result[slug] = {"timeline_entries": [], "quotes": []}
            continue

        ph = ",".join("?" * len(ids))
        rows = conn.execute(f"""
            SELECT c.id, c.title, c.created_at, c.estimated_pages, c.summary,
                   s.name as source
            FROM conversations c
            JOIN sources s ON s.id = c.source_id
            WHERE c.id IN ({ph})
            ORDER BY c.created_at ASC
        """, ids).fetchall()

        timeline = []
        for r in rows:
            date = (r[2] or "")[:10] if r[2] else "Unknown"
            title = r[1] or "Untitled"
            pages_count = r[3] or 0
            summary = (r[4] or "")[:200]

            # Build description from summary — sanitize for embedding in Python source
            if summary and len(summary) > 30:
                # Strip code blocks, HTML tags, markdown artifacts
                clean = re.sub(r'```[^`]*```', '', summary)
                clean = re.sub(r'`[^`]*`', '', clean)
                clean = re.sub(r'<[^>]+>', '', clean)
                clean = clean.replace('\n', ' ').replace('\r', ' ')
                clean = re.sub(r'\s+', ' ', clean).strip()
                if clean and len(clean) > 30:
                    desc = clean.split(".")[0] + "." if "." in clean[:180] else clean[:180] + "..."
                else:
                    desc = f"{pages_count:.0f} pages of exploration via {r[5]}."
            else:
                desc = f"{pages_count:.0f} pages of exploration via {r[5]}."

            timeline.append({
                "date": date,
                "title": title[:80],
                "description": desc,
                "conversation_id": r[0],
            })

        # Extract a quote from the longest conversation's summary
        quotes = []
        longest = conn.execute(f"""
            SELECT c.id, c.title, c.estimated_pages
            FROM conversations c
            WHERE c.id IN ({ph})
            ORDER BY c.estimated_pages DESC
            LIMIT 3
        """, ids).fetchall()

        for conv in longest:
            # Get first substantive assistant message
            msg = conn.execute("""
                SELECT content FROM messages
                WHERE conversation_id = ? AND role = 'assistant'
                AND length(content) > 100
                ORDER BY id ASC LIMIT 1
            """, (conv[0],)).fetchone()
            if msg:
                text_content = msg[0] or ""
                # Extract a quotable sentence (skip code, JSON, etc)
                sentences = []
                for line in text_content.split("\n"):
                    line = line.strip()
                    if (len(line) > 40 and len(line) < 300
                        and not line.startswith("{") and not line.startswith("[")
                        and not line.startswith("```") and not line.startswith("#")
                        and not line.startswith("*") and not line.startswith("-")
                        and not line.startswith("|") and "http" not in line
                        and "upload" not in line.lower()
                        and "file" not in line.lower()[:20]):
                        sentences.append(line)
                if sentences:
                    # Pick the most interesting-looking sentence
                    best = max(sentences[:10], key=lambda s: len(s)) if sentences else sentences[0]
                    # Clean up markdown
                    best = re.sub(r'\*\*([^*]+)\*\*', r'\1', best)
                    best = re.sub(r'\*([^*]+)\*', r'\1', best)
                    best = best.strip('"').strip("'").strip()
                    # Sanitize for Python source embedding
                    best = best.replace('\n', ' ').replace('\r', ' ')
                    best = re.sub(r'`[^`]*`', '', best)
                    best = re.sub(r'<[^>]+>', '', best)
                    best = re.sub(r'\s+', ' ', best).strip()
                    if len(best) > 40:
                        quotes.append({
                            "text": best[:280],
                            "role": "assistant",
                            "conversation_title": conv[1][:60],
                            "conversation_id": conv[0],
                        })

        result[slug] = {
            "timeline_entries": timeline,
            "quotes": quotes[:3],
        }

    conn.close()
    return result


def apply_content(data):
    """Inject timeline_entries and quotes into app.py."""
    with open(APP_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    applied_t = 0
    applied_q = 0

    for slug, content in data.items():
        # Apply timeline_entries
        if content["timeline_entries"]:
            timeline_json = json.dumps(content["timeline_entries"], ensure_ascii=False)
            pattern = re.compile(
                r'("slug":\s*"' + re.escape(slug) + r'".*?"timeline_entries":\s*)\[\]',
                re.DOTALL
            )
            match = pattern.search(text)
            if match:
                text = text[:match.start()] + match.group(1) + timeline_json + text[match.end():]
                applied_t += 1

        # Apply quotes
        if content["quotes"]:
            quotes_json = json.dumps(content["quotes"], ensure_ascii=False)
            pattern = re.compile(
                r'("slug":\s*"' + re.escape(slug) + r'".*?"quotes":\s*)\[\]',
                re.DOTALL
            )
            match = pattern.search(text)
            if match:
                text = text[:match.start()] + match.group(1) + quotes_json + text[match.end():]
                applied_q += 1

    with open(APP_PATH, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Applied {applied_t} timelines, {applied_q} quote sets to app.py")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python generate_timelines.py --generate")
        print("  python generate_timelines.py --apply")
        return

    if sys.argv[1] == "--generate":
        pages = get_pages_needing_content()
        print(f"Found {len(pages)} pages needing timelines/quotes")
        data = generate_timelines(pages)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        total_t = sum(len(v["timeline_entries"]) for v in data.values())
        total_q = sum(len(v["quotes"]) for v in data.values())
        print(f"Generated {total_t} timeline entries, {total_q} quotes -> {OUTPUT_PATH}")

    elif sys.argv[1] == "--apply":
        if not os.path.exists(OUTPUT_PATH):
            print(f"No data file at {OUTPUT_PATH}. Run --generate first.")
            return
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        apply_content(data)


if __name__ == "__main__":
    main()
