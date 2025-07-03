"""Fetch tarot card meanings from open sources.

This is a scaffold script. For each card name it will attempt to download
Labyrinthos Academy HTML page and extract the Upright and Reversed meanings.
You can later extend with additional sources or translation logic.

Usage (dev):
    python scripts/fetch_tarot_sources.py --out data/tarot_raw.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://labyrinthos.co"
CARD_SLUGS = {
    "The Fool": "blogs/tarot-card-meanings/fool",
    "The Magician": "blogs/tarot-card-meanings/magician",
    # ... add remaining slugs
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TarotBot/0.1)"
}


def fetch_card(name: str, slug: str) -> Dict:
    url = f"{BASE_URL}/{slug}"
    r = httpx.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    content_el = soup.select_one("article")
    text = content_el.get_text("\n", strip=True) if content_el else ""

    # naive extraction of Upright / Reversed sections
    upright_match = re.search(r"Upright\s*(.+?)Reversed", text, re.DOTALL | re.IGNORECASE)
    reversed_match = re.search(r"Reversed\s*(.+)$", text, re.DOTALL | re.IGNORECASE)

    upright_meaning = upright_match.group(1).strip() if upright_match else ""
    reversed_meaning = reversed_match.group(1).strip() if reversed_match else ""

    return {
        "name_en": name,
        "upright": upright_meaning,
        "reversed": reversed_meaning,
        "source": url,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/tarot_raw.json")
    args = parser.parse_args()
    out_path = Path(args.out)

    results: List[Dict] = []
    for name, slug in CARD_SLUGS.items():
        try:
            print(f"Fetching {name}...")
            card_data = fetch_card(name, slug)
            results.append(card_data)
        except Exception as e:  # noqa: BLE001
            print(f"Failed to fetch {name}: {e}")

    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(results)} cards to {out_path}")


if __name__ == "__main__":
    main()
