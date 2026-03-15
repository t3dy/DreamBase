"""
Download public domain art from Wikimedia Commons for Dreambase gallery pages.
Saves to static/art/ with slug-based filenames.
Updates image URLs in app.py to use local paths.
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse

ART_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "art")
APP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")

# Map: filename -> Wikimedia Commons file title (without "File:" prefix)
# These are all public domain works (pre-1900 or PD-US)
ARTWORKS = {
    # Michael Maier - Atalanta Fugiens
    "maier-emblem21.jpg": "Atalanta Fugiens Emblem 21.jpeg",
    "maier-emblem01.jpg": "Michael Maier Atalanta Fugiens Emblem 01.jpeg",

    # Heinrich Khunrath
    "khunrath-lab.jpg": "Amphitheatrum sapientiae aeternae - Alchemist's Laboratory.jpg",

    # Giordano Bruno
    "bruno-statue.jpg": "Giordano Bruno Campo dei Fiori.jpg",
    "bruno-portrait.jpg": "Giordano Bruno.jpg",

    # Pico della Mirandola
    "pico-portrait.jpg": "Pico1.jpg",

    # John Dee
    "dee-portrait.jpg": "John Dee Ashmolean.jpg",

    # Paracelsus
    "paracelsus-portrait.jpg": "Paracelsus.jpg",

    # Agrippa
    "agrippa-portrait.png": "Agrippa.png",

    # Isaac Newton
    "newton-portrait.jpg": "GodfreyKneller-IsaacNewton-1689.jpg",

    # Thomas Aquinas
    "aquinas-portrait.jpg": "St-thomas-aquinas.jpg",

    # PKD
    "pkd-portrait.jpg": "Philip K Dick photo portrait.jpg",

    # Alchemical lab (shared)
    "alchemy-lab.jpg": "Fotothek df tg 0006097 Alchemie.jpg",

    # Tree of Life
    "tree-of-life.jpg": "Tree of Life, Medieval.jpg",
}


def get_wikimedia_thumb_url(file_title, width=500):
    """Use Wikimedia API to get a thumbnail URL."""
    encoded = urllib.parse.quote(f"File:{file_title}")
    api_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={encoded}&prop=imageinfo&iiprop=url&iiurlwidth={width}&format=json"
    req = urllib.request.Request(api_url, headers={"User-Agent": "DreambaseBot/1.0 (personal project)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                info = page.get("imageinfo", [{}])[0]
                return info.get("thumburl") or info.get("url")
    except Exception as e:
        print(f"  API error for {file_title}: {e}")
    return None


def download_image(url, filepath):
    """Download an image from URL."""
    req = urllib.request.Request(url, headers={"User-Agent": "DreambaseBot/1.0 (personal project)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            with open(filepath, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"  Download error: {e}")
        return False


def main():
    os.makedirs(ART_DIR, exist_ok=True)

    downloaded = 0
    for filename, wiki_title in ARTWORKS.items():
        filepath = os.path.join(ART_DIR, filename)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            print(f"  EXISTS: {filename}")
            downloaded += 1
            continue

        print(f"  Fetching URL for: {wiki_title}")
        thumb_url = get_wikimedia_thumb_url(wiki_title)
        if not thumb_url:
            print(f"  FAILED to get URL for {wiki_title}")
            continue

        print(f"  Downloading: {filename}")
        if download_image(thumb_url, filepath):
            size = os.path.getsize(filepath)
            if size > 1000:
                print(f"  OK: {filename} ({size:,} bytes)")
                downloaded += 1
            else:
                print(f"  TOO SMALL: {filename} ({size} bytes) — probably an error page")
                os.remove(filepath)
        time.sleep(0.5)  # Be polite to Wikimedia

    print(f"\nDownloaded {downloaded}/{len(ARTWORKS)} images to {ART_DIR}")

    # Now update app.py to use local paths
    if "--update-paths" in sys.argv:
        update_app_paths()


def update_app_paths():
    """Replace Wikimedia URLs in app.py with local /static/art/ paths."""
    with open(APP_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    # Build mapping of old URL patterns to new local paths
    replacements = {
        "Atalanta_Fugiens_Emblem_21": "/static/art/maier-emblem21.jpg",
        "Michael_Maier_Atalanta_Fugiens_Emblem_01": "/static/art/maier-emblem01.jpg",
        "Atalanta_Fugiens_Emblem_42": "/static/art/maier-emblem21.jpg",  # fallback
        "Amphitheatrum_sapientiae_aeternae": "/static/art/khunrath-lab.jpg",
        "Giordano_Bruno_Campo_dei_Fiori": "/static/art/bruno-statue.jpg",
        "Giordano_Bruno.jpg": "/static/art/bruno-portrait.jpg",
        "5/5d/Giordano_Bruno": "/static/art/bruno-portrait.jpg",
        "Pico1.jpg": "/static/art/pico-portrait.jpg",
        "John_Dee_Ashmolean": "/static/art/dee-portrait.jpg",
        "Monas_Hieroglyphica": "/static/art/dee-portrait.jpg",  # fallback to portrait
        "Paracelsus.jpg": "/static/art/paracelsus-portrait.jpg",
        "Paracelsus_Astronomica": "/static/art/paracelsus-portrait.jpg",
        "Agrippa.png": "/static/art/agrippa-portrait.png",
        "De_Occulta_Philosophia": "/static/art/agrippa-portrait.png",
        "Proclus_Lycaeus": "/static/art/pico-portrait.jpg",  # fallback
        "GodfreyKneller-IsaacNewton": "/static/art/newton-portrait.jpg",
        "St-thomas-aquinas": "/static/art/aquinas-portrait.jpg",
        "Aleister_Crowley": "/static/art/khunrath-lab.jpg",  # fallback to alchemy
        "Philip_K_Dick": "/static/art/pkd-portrait.jpg",
        "Splendor_Solis": "/static/art/alchemy-lab.jpg",  # fallback
        "Fotothek_df_tg_0006097": "/static/art/alchemy-lab.jpg",
        "Tree_of_Life": "/static/art/tree-of-life.jpg",
        "Ficino_Platonic_Academy": "/static/art/pico-portrait.jpg",  # fallback
    }

    count = 0
    for pattern, local_path in replacements.items():
        # Match any URL containing this pattern
        regex = re.compile(r'https://upload\.wikimedia\.org/[^"]*' + re.escape(pattern) + r'[^"]*')
        new_text = regex.sub(local_path, text)
        if new_text != text:
            count += 1
            text = new_text

    with open(APP_PATH, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Updated {count} image URLs to local paths")


if __name__ == "__main__":
    main()
