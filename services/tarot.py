"""Tarot card utilities.

Load tarot card data from JSON and provide random draw functionality.
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import List, Dict

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "tarot_cards.json"


class TarotService:  # pragma: no cover
    """Singleton-style helper to manage tarot data in memory."""

    _cards: List[Dict] | None = None

    @classmethod
    def _load(cls) -> None:
        if cls._cards is None:
            with _DATA_PATH.open("r", encoding="utf-8") as fp:
                cls._cards = json.load(fp)

    @classmethod
    def draw(cls, n: int = 1) -> List[Dict]:
        cls._load()
        n = max(1, min(n, len(cls._cards)))
        return random.sample(cls._cards, n)
