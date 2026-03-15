"""
Narrative Generator for Dreambase Showcase & Scholar Pages.

Extracts conversation data for each showcase/scholar page,
generates narrative HTML, and applies it to app.py.

Usage:
    python generate_narratives.py --extract          # Dump conversation data per slug
    python generate_narratives.py --apply FILE.json  # Apply narratives from JSON to app.py
    python generate_narratives.py --check            # Show which pages have/lack narratives
"""

import json
import os
import re
import sqlite3
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "megabase.db")
APP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")


def read_app_dicts():
    """Parse SHOWCASES and SCHOLARS from app.py, return slug -> conversation_ids + type."""
    with open(APP_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    pages = {}
    # Find all entries with slug, conversation_ids, and narrative: None
    pattern = re.compile(
        r'"slug":\s*"([^"]+)".*?"conversation_ids":\s*\[([^\]]*)\]',
        re.DOTALL
    )
    for match in pattern.finditer(text):
        slug = match.group(1)
        ids_str = match.group(2).strip()
        ids = [int(x.strip()) for x in ids_str.split(",") if x.strip()] if ids_str else []

        # Determine type from surrounding context
        pos = match.start()
        nearby = text[max(0, pos - 500):pos + 2000]
        has_narrative = '"narrative"' in nearby

        # Determine if game, scholar, or collection
        page_type = "collection"
        if '"pedagogy"' in nearby and '"difficulty_easy"' in nearby:
            page_type = "game"
        elif '"field"' in nearby and '"era"' in nearby:
            page_type = "scholar"
        elif '"depth_introductory"' in nearby:
            page_type = "scholar"

        if has_narrative:
            # Check if narrative is None
            narr_match = re.search(r'"narrative":\s*(None|")', nearby)
            if narr_match and narr_match.group(1) == "None":
                pages[slug] = {"ids": ids, "type": page_type}

    return pages


def extract_data(pages):
    """For each page, pull conversation summaries from DB."""
    conn = sqlite3.connect(DB_PATH)
    result = {}

    for slug, info in sorted(pages.items()):
        ids = info["ids"]
        if not ids:
            result[slug] = {"type": info["type"], "conversations": [], "total_pages": 0}
            continue

        ph = ",".join("?" * len(ids))
        rows = conn.execute(f"""
            SELECT c.id, c.title, c.summary, c.estimated_pages, c.message_count,
                   s.name as source
            FROM conversations c
            JOIN sources s ON s.id = c.source_id
            WHERE c.id IN ({ph})
            ORDER BY c.estimated_pages DESC
        """, ids).fetchall()

        convos = []
        for r in rows:
            convos.append({
                "id": r[0],
                "title": r[1],
                "summary": (r[2] or "")[:300],
                "pages": r[3] or 0,
                "messages": r[4] or 0,
                "source": r[5],
            })

        result[slug] = {
            "type": info["type"],
            "conversations": convos,
            "total_pages": sum(c["pages"] for c in convos),
        }

    conn.close()
    return result


def apply_narratives(json_path):
    """Read narratives from JSON and patch app.py."""
    with open(json_path, "r", encoding="utf-8") as f:
        narratives = json.load(f)

    with open(APP_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    applied = 0
    for slug, narrative_html in narratives.items():
        # Find the pattern: "slug": "SLUG" ... "narrative": None
        # and replace None with the narrative string
        # We need to be careful to only match within the right dict entry
        pattern = re.compile(
            r'("slug":\s*"' + re.escape(slug) + r'".*?"narrative":\s*)None',
            re.DOTALL
        )
        # Escape the narrative for Python string literal
        escaped = narrative_html.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        replacement = r'\g<1>"' + escaped + '"'

        new_text, count = pattern.subn(replacement, text, count=1)
        if count:
            text = new_text
            applied += 1
            print(f"  Applied: {slug}")
        else:
            print(f"  SKIP (not found or already set): {slug}")

    with open(APP_PATH, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"\nApplied {applied}/{len(narratives)} narratives to app.py")


def check_status():
    """Show which pages have/lack narratives."""
    with open(APP_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    has = 0
    missing = 0
    for match in re.finditer(r'"slug":\s*"([^"]+)"', text):
        slug = match.group(1)
        pos = match.start()
        nearby = text[pos:pos + 2000]
        narr_match = re.search(r'"narrative":\s*(None|")', nearby)
        if narr_match:
            if narr_match.group(1) == "None":
                print(f"  MISSING  {slug}")
                missing += 1
            else:
                print(f"  OK       {slug}")
                has += 1

    print(f"\nHas narrative: {has} | Missing: {missing}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python generate_narratives.py --extract")
        print("  python generate_narratives.py --apply narratives.json")
        print("  python generate_narratives.py --check")
        return

    if sys.argv[1] == "--extract":
        pages = read_app_dicts()
        data = extract_data(pages)
        out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "narrative_data.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Extracted data for {len(data)} pages -> {out_path}")

    elif sys.argv[1] == "--apply":
        if len(sys.argv) < 3:
            print("Usage: python generate_narratives.py --apply narratives.json")
            return
        apply_narratives(sys.argv[2])

    elif sys.argv[1] == "--check":
        check_status()


if __name__ == "__main__":
    main()
