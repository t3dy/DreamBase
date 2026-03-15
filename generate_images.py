"""
Generate public domain art image entries for showcase/scholar pages.

Uses Wikimedia Commons URLs for historically relevant art.
All images are public domain (pre-1900 or explicitly PD).

Usage:
    python generate_images.py --apply   # Apply images to app.py
"""

import json
import os
import re
import sys

APP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")

# Public domain art mapped to showcase/scholar slugs.
# All URLs are Wikimedia Commons direct file links (stable, PD).
IMAGES = {
    "michael-maier": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Atalanta_Fugiens_Emblem_21.jpeg/400px-Atalanta_Fugiens_Emblem_21.jpeg", "caption": "Atalanta Fugiens, Emblem 21 — Make of man and woman a circle (Matthäus Merian, 1618)"},
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Michael_Maier_Atalanta_Fugiens_Emblem_01.jpeg/400px-Michael_Maier_Atalanta_Fugiens_Emblem_01.jpeg", "caption": "Atalanta Fugiens, Emblem 1 — The Wind carries him in its belly"},
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Atalanta_Fugiens_Emblem_42.jpeg/400px-Atalanta_Fugiens_Emblem_42.jpeg", "caption": "Atalanta Fugiens, Emblem 42 — A Hermaphrodite, dead, is roasted by fire"},
    ],
    "heinrich-khunrath": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Amphitheatrum_sapientiae_aeternae_-_Alchemist%27s_Laboratory.jpg/500px-Amphitheatrum_sapientiae_aeternae_-_Alchemist%27s_Laboratory.jpg", "caption": "The Alchemist's Laboratory — Amphitheatrum Sapientiae Aeternae (Khunrath, 1595)"},
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Heinrich_Khunrath%2C_Amphitheatrum_sapientiae_aeternae%2C_1595._Wellcome_L0045758.jpg/500px-Heinrich_Khunrath%2C_Amphitheatrum_sapientiae_aeternae%2C_1595._Wellcome_L0045758.jpg", "caption": "The Rose of the Philosophers — Khunrath's theosophical vision"},
    ],
    "giordano-bruno": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Giordano_Bruno_Campo_dei_Fiori.jpg/400px-Giordano_Bruno_Campo_dei_Fiori.jpg", "caption": "Statue of Giordano Bruno at Campo de' Fiori, Rome — where he was burned in 1600"},
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Giordano_Bruno.jpg/350px-Giordano_Bruno.jpg", "caption": "Portrait of Giordano Bruno (19th century engraving)"},
    ],
    "pico-della-mirandola": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Pico1.jpg/350px-Pico1.jpg", "caption": "Giovanni Pico della Mirandola — portrait by Cristofano dell'Altissimo (Uffizi Gallery)"},
    ],
    "john-dee": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/John_Dee_Ashmolean.jpg/350px-John_Dee_Ashmolean.jpg", "caption": "Portrait of John Dee (16th century, Ashmolean Museum)"},
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Monas_Hieroglyphica.svg/300px-Monas_Hieroglyphica.svg.png", "caption": "The Monas Hieroglyphica — Dee's unified symbol of cosmic truth (1564)"},
    ],
    "marsilio-ficino": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Ficino_Platonic_Academy.jpg/450px-Ficino_Platonic_Academy.jpg", "caption": "Marsilio Ficino with members of the Platonic Academy (Ghirlandaio fresco, Santa Maria Novella)"},
    ],
    "paracelsus": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Paracelsus.jpg/350px-Paracelsus.jpg", "caption": "Paracelsus — portrait attributed to Quentin Matsys (16th century)"},
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Paracelsus_Astronomica_et_astrologica.jpg/400px-Paracelsus_Astronomica_et_astrologica.jpg", "caption": "Title page of Paracelsus's Astronomica et Astrologica (1567)"},
    ],
    "agrippa": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Agrippa.png/350px-Agrippa.png", "caption": "Heinrich Cornelius Agrippa — woodcut portrait (16th century)"},
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/De_Occulta_Philosophia.jpg/350px-De_Occulta_Philosophia.jpg", "caption": "Title page of De Occulta Philosophia (1533)"},
    ],
    "proclus": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Proclus_Lycaeus.jpg/350px-Proclus_Lycaeus.jpg", "caption": "Proclus Lycaeus — late antique philosopher and theurgist"},
    ],
    "isaac-newton": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/GodfreyKneller-IsaacNewton-1689.jpg/350px-GodfreyKneller-IsaacNewton-1689.jpg", "caption": "Isaac Newton — portrait by Godfrey Kneller (1689)"},
    ],
    "thomas-aquinas": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/St-thomas-aquinas.jpg/350px-St-thomas-aquinas.jpg", "caption": "Thomas Aquinas — detail from the Demidoff Altarpiece by Carlo Crivelli (1476)"},
    ],
    "aleister-crowley": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Aleister_Crowley%2C_wickedest_man_in_the_world.jpg/350px-Aleister_Crowley%2C_wickedest_man_in_the_world.jpg", "caption": "Aleister Crowley — photograph (early 20th century)"},
    ],
    "philip-k-dick": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Philip_K_Dick_photo_portrait.jpg/350px-Philip_K_Dick_photo_portrait.jpg", "caption": "Philip K. Dick — photo portrait (1982)"},
    ],
    "alchemy-board-game": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Splendor_Solis_-_The_Alchemist.jpg/400px-Splendor_Solis_-_The_Alchemist.jpg", "caption": "Splendor Solis — The Alchemist at Work (1582 illuminated manuscript)"},
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Fotothek_df_tg_0006097_Alchemie.jpg/400px-Fotothek_df_tg_0006097_Alchemie.jpg", "caption": "Alchemical laboratory — woodcut from the 16th century"},
    ],
    "hereward-tilton": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Amphitheatrum_sapientiae_aeternae_-_Alchemist%27s_Laboratory.jpg/500px-Amphitheatrum_sapientiae_aeternae_-_Alchemist%27s_Laboratory.jpg", "caption": "Khunrath's Amphitheatre — the alchemist's oratory and laboratory united"},
    ],
    "gershom-scholem": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Tree_of_Life%2C_Medieval.jpg/350px-Tree_of_Life%2C_Medieval.jpg", "caption": "The Kabbalistic Tree of Life — medieval manuscript illustration"},
    ],
    "carl-jung": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Splendor_Solis_-_The_Alchemist.jpg/400px-Splendor_Solis_-_The_Alchemist.jpg", "caption": "Splendor Solis — the alchemical imagery Jung interpreted as symbols of individuation"},
    ],
    "allen-debus": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Fotothek_df_tg_0006097_Alchemie.jpg/400px-Fotothek_df_tg_0006097_Alchemie.jpg", "caption": "An alchemist's laboratory — the kind of workspace Debus studied historically"},
    ],
    "lawrence-principe": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Fotothek_df_tg_0006097_Alchemie.jpg/400px-Fotothek_df_tg_0006097_Alchemie.jpg", "caption": "Alchemical distillation apparatus — the equipment Principe reproduces in modern labs"},
    ],
    "peter-forshaw": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Atalanta_Fugiens_Emblem_21.jpeg/400px-Atalanta_Fugiens_Emblem_21.jpeg", "caption": "Atalanta Fugiens, Emblem 21 — the visual alchemy Forshaw studies"},
    ],
    "dion-fortune": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Tree_of_Life%2C_Medieval.jpg/350px-Tree_of_Life%2C_Medieval.jpg", "caption": "The Tree of Life — central to Fortune's Kabbalistic magical system"},
    ],
    "frances-yates": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Giordano_Bruno.jpg/350px-Giordano_Bruno.jpg", "caption": "Giordano Bruno — the figure at the center of Yates's Hermetic Tradition thesis"},
    ],
    "antoine-faivre": [
        {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Monas_Hieroglyphica.svg/300px-Monas_Hieroglyphica.svg.png", "caption": "The Monas Hieroglyphica — an example of the 'correspondences' Faivre defined as central to esotericism"},
    ],
}


def apply_images():
    """Inject image arrays into app.py."""
    with open(APP_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    applied = 0
    for slug, images in IMAGES.items():
        images_json = json.dumps(images, ensure_ascii=False)
        pattern = re.compile(
            r'("slug":\s*"' + re.escape(slug) + r'".*?"images":\s*)\[\]',
            re.DOTALL
        )
        match = pattern.search(text)
        if match:
            text = text[:match.start()] + match.group(1) + images_json + text[match.end():]
            applied += 1
            print(f"  Applied {len(images)} images: {slug}")
        else:
            print(f"  SKIP: {slug}")

    with open(APP_PATH, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"\nApplied images to {applied}/{len(IMAGES)} pages")


def main():
    if len(sys.argv) < 2 or sys.argv[1] != "--apply":
        print("Usage: python generate_images.py --apply")
        return
    apply_images()


if __name__ == "__main__":
    main()
