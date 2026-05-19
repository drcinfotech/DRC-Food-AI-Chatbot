"""Data catalog — loads catalog from JSON."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


DATA_DIR = Path(__file__).parent.parent / "data"


class Catalog:
    def __init__(self):
        with open(DATA_DIR / "catalog.json", "r", encoding="utf-8") as f:
            self._data = json.load(f)
        # Build a flat item index for quick lookups
        self._all_items: dict[str, dict] = {}
        for rid, items in self._data["menu"].items():
            for it in items:
                self._all_items[it["id"]] = {**it, "restaurant_id": rid}

    # ── Restaurants ────────────────────────────────────
    def restaurants(self) -> list[dict]:
        return list(self._data["restaurants"])

    def restaurant(self, rid: str) -> Optional[dict]:
        for r in self._data["restaurants"]:
            if r["id"] == rid:
                return r
        return None

    # ── Menu ───────────────────────────────────────────
    def menu(self, rid: str) -> list[dict]:
        return list(self._data["menu"].get(rid, []))

    def item(self, item_id: str) -> Optional[dict]:
        return self._all_items.get(item_id)

    def all_items(self) -> list[dict]:
        return list(self._all_items.values())

    # ── Other ──────────────────────────────────────────
    def recent_orders(self) -> list[dict]:
        return list(self._data["recent_orders"])

    def addresses(self) -> list[dict]:
        return list(self._data["addresses"])

    def offers(self) -> list[dict]:
        return list(self._data["offers"])


catalog = Catalog()
