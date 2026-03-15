"""Fix image paths in app.py: use local files, remove entries for missing images."""

import json
import os
import re

APP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
ART_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "art")

# Map slug -> list of local images with captions
LOCAL_IMAGES = {
    "pico-della-mirandola": [
        {"url": "/static/art/pico-portrait.jpg", "caption": "Giovanni Pico della Mirandola — portrait by Cristofano dell'Altissimo (Uffizi Gallery)"},
    ],
    "giordano-bruno": [
        {"url": "/static/art/bruno-statue.jpg", "caption": "Statue of Giordano Bruno at Campo de' Fiori, Rome — erected at the site of his execution in 1600"},
        {"url": "/static/art/bruno-portrait.jpg", "caption": "Portrait of Giordano Bruno (19th century engraving)"},
    ],
    "john-dee": [
        {"url": "/static/art/dee-portrait.jpg", "caption": "Portrait of John Dee (16th century, Ashmolean Museum)"},
    ],
    "paracelsus": [
        {"url": "/static/art/paracelsus-portrait.jpg", "caption": "Paracelsus — portrait attributed to Quentin Matsys (16th century)"},
    ],
    "isaac-newton": [
        {"url": "/static/art/newton-portrait.jpg", "caption": "Isaac Newton — portrait by Godfrey Kneller (1689)"},
    ],
    "thomas-aquinas": [
        {"url": "/static/art/aquinas-portrait.jpg", "caption": "Thomas Aquinas — detail from the Demidoff Altarpiece by Carlo Crivelli (1476)"},
    ],
    "heinrich-khunrath": [
        {"url": "/static/art/khunrath-lab.jpg", "caption": "The Alchemist's Laboratory — Amphitheatrum Sapientiae Aeternae (Khunrath, 1595)"},
    ],
    "hereward-tilton": [
        {"url": "/static/art/khunrath-lab.jpg", "caption": "Khunrath's Amphitheatre — the alchemist's oratory and laboratory united"},
    ],
    "michael-maier": [
        {"url": "/static/art/khunrath-lab.jpg", "caption": "An alchemist's laboratory — the visual world of Maier's Atalanta Fugiens"},
    ],
    "peter-forshaw": [
        {"url": "/static/art/khunrath-lab.jpg", "caption": "The alchemical laboratory — the visual culture Forshaw studies"},
    ],
    "gershom-scholem": [
        {"url": "/static/art/tree-of-life.jpg", "caption": "The Kabbalistic Tree of Life — medieval manuscript illustration"},
    ],
    "dion-fortune": [
        {"url": "/static/art/tree-of-life.jpg", "caption": "The Tree of Life — central to Fortune's Kabbalistic magical system"},
    ],
    "alchemy-board-game": [
        {"url": "/static/art/khunrath-lab.jpg", "caption": "An alchemist at work — the world the board game brings to life"},
    ],
    "carl-jung": [
        {"url": "/static/art/khunrath-lab.jpg", "caption": "The alchemical laboratory — the imagery Jung interpreted as symbols of individuation"},
    ],
    "allen-debus": [
        {"url": "/static/art/khunrath-lab.jpg", "caption": "An alchemist's workspace — the kind of laboratory Debus studied historically"},
    ],
    "lawrence-principe": [
        {"url": "/static/art/khunrath-lab.jpg", "caption": "Alchemical apparatus — the equipment Principe reproduces in modern labs"},
    ],
    "marsilio-ficino": [
        {"url": "/static/art/pico-portrait.jpg", "caption": "Pico della Mirandola — Ficino's student and intellectual heir"},
    ],
    "frances-yates": [
        {"url": "/static/art/bruno-portrait.jpg", "caption": "Giordano Bruno — the figure at the center of Yates's Hermetic Tradition thesis"},
    ],
}


def fix_paths():
    with open(APP_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    fixed = 0
    for slug, images in LOCAL_IMAGES.items():
        images_json = json.dumps(images, ensure_ascii=False)
        # Replace existing images array for this slug
        pattern = re.compile(
            r'("slug":\s*"' + re.escape(slug) + r'".*?"images":\s*)\[[^\]]*\]',
            re.DOTALL
        )
        match = pattern.search(text)
        if match:
            text = text[:match.start()] + match.group(1) + images_json + text[match.end():]
            fixed += 1
            print(f"  Fixed: {slug} ({len(images)} images)")
        else:
            print(f"  SKIP: {slug}")

    # For slugs NOT in LOCAL_IMAGES that still have wikimedia URLs, reset to []
    # Find all slugs with images containing "wikimedia"
    for m in re.finditer(r'"slug":\s*"([^"]+)"', text):
        slug = m.group(1)
        if slug in LOCAL_IMAGES:
            continue
        pos = m.start()
        nearby = text[pos:pos + 5000]
        if "wikimedia" in nearby and '"images":' in nearby:
            img_match = re.search(r'"images":\s*\[[^\]]+wikimedia[^\]]*\]', nearby)
            if img_match:
                abs_start = pos + img_match.start()
                abs_end = pos + img_match.end()
                text = text[:abs_start] + '"images": []' + text[abs_end:]
                print(f"  Cleared broken URLs: {slug}")

    with open(APP_PATH, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"\nFixed {fixed} pages with local images")


if __name__ == "__main__":
    fix_paths()
