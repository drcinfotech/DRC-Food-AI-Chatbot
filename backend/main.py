"""FastAPI entry point for the Food, Restaurant Ordering & Delivery AI Chatbot."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.catalog import catalog
from app.chatbot import engine
from app.models import ChatRequest, ChatResponse
from app.sessions import store

app = FastAPI(
    title="Food AI Chatbot — Order Assistant",
    description=(
        "A demo conversational AI for the food, restaurant ordering, and delivery industry. "
        "Includes intent classification, allergen-safety guardrails, age-gating for alcohol, "
        "payment-privacy protection, and rich response blocks for restaurants, menus, cart, "
        "tracking, offers, and dietary filtering. NOT a real delivery service."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status":      "ok",
        "restaurants": len(catalog.restaurants()),
        "menu_items":  len(catalog.all_items()),
        "offers":      len(catalog.offers()),
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session = store.get_or_create(req.session_id)
    return engine.respond(req.message, session)


@app.get("/restaurants")
def list_restaurants():
    return catalog.restaurants()


@app.get("/restaurants/{rid}")
def get_restaurant(rid: str):
    r = catalog.restaurant(rid)
    if not r:
        return {"error": "not_found", "id": rid}
    return r


@app.get("/restaurants/{rid}/menu")
def get_menu(rid: str):
    return catalog.menu(rid)


@app.get("/items/{item_id}")
def get_item(item_id: str):
    it = catalog.item(item_id)
    if not it:
        return {"error": "not_found", "id": item_id}
    return it


@app.get("/orders/recent")
def list_recent_orders():
    return catalog.recent_orders()


@app.get("/offers")
def list_offers():
    return catalog.offers()


@app.get("/addresses")
def list_addresses():
    return catalog.addresses()


@app.get("/")
def root():
    return {
        "name":       "Food AI Chatbot — Order Assistant",
        "version":    app.version,
        "docs":       "/docs",
        "disclaimer": "Demo only. Not a real food delivery service. Allergen guardrails are best-effort.",
    }
