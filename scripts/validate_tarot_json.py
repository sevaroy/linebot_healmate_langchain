"""Validate tarot_cards.json for completeness and correctness."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "tarot_cards.json"


def main() -> None:  # noqa: D401
    """Run checks and exit non-zero on failure."""
    cards = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    # 1. count
    if len(cards) != 156:
        sys.exit(f"Expected 156 cards (78 upright + 78 reversed). Got {len(cards)}")

    # 2. required fields
    required = {"id", "name", "arcana", "orientation", "meaning"}
    for c in cards:
        missing = required - c.keys()
        if missing:
            sys.exit(f"Card id {c.get('id')} missing fields: {missing}")

    # 3. uniqueness
    id_counts = Counter(c["id"] for c in cards)
    dup_ids = [id_ for id_, cnt in id_counts.items() if cnt > 1]
    if dup_ids:
        sys.exit(f"Duplicate ids found: {dup_ids}")

    name_orient_counts = Counter((c["name"], c["orientation"]) for c in cards)
    duplicates = [k for k, cnt in name_orient_counts.items() if cnt > 1]
    if duplicates:
        sys.exit(f"Duplicate name+orientation combinations: {duplicates}")

    print("All checks passed! ✨")


if __name__ == "__main__":
    main()
