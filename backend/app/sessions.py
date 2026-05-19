"""Lightweight in-memory session store with cart + allergen profile."""
from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class CartLine:
    item_id: str
    name: str
    price: float
    qty: int
    allergens: list[str] = field(default_factory=list)


@dataclass
class Session:
    session_id: str
    last_intent: str = ""
    last_restaurant_id: str | None = None
    # Cart can only have items from ONE restaurant at a time (industry standard)
    cart_restaurant_id: str | None = None
    cart: list[CartLine] = field(default_factory=list)
    # Allergens declared by the user, accumulated across the session
    allergen_profile: list[str] = field(default_factory=list)
    diet_profile: list[str] = field(default_factory=list)
    applied_offer: str | None = None
    history: list[dict] = field(default_factory=list)


class SessionStore:
    def __init__(self):
        self._sessions: dict[str, Session] = {}
        self._lock = Lock()

    def get_or_create(self, session_id: str | None) -> Session:
        with self._lock:
            if session_id and session_id in self._sessions:
                return self._sessions[session_id]
            new_id = session_id or secrets.token_urlsafe(12)
            s = Session(session_id=new_id)
            self._sessions[new_id] = s
            return s


store = SessionStore()
