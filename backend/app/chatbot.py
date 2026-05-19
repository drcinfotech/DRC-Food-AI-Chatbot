"""
Food, Restaurant Ordering & Delivery chatbot engine.

Flow:
  1. Safety check first
     • social_engineering / payment_privacy / allergen_promise → SHORT-CIRCUIT (refuse)
     • allergen detection (without "promise" patterns) → ENRICH session, continue
  2. Classify intent
  3. Dispatch to handler
  4. Decorate cart-affecting responses with allergen warnings if profile is set
"""
from __future__ import annotations

from .catalog import catalog
from .intents import Classification, classify
from .safety import (
    check_safety,
    build_allergen_promise_block,
    build_age_gate_block,
    build_payment_privacy_block,
    build_social_engineering_block,
    ALCOHOL_KEYWORDS,
)
from .sessions import Session, CartLine


# ─── Block helpers ─────────────────────────────────────────
def _text(content: str) -> dict:
    return {"type": "text", "content": content}


def _disclaimer(content: str) -> dict:
    return {"type": "disclaimer", "content": content}


def _allergen_callout(profile: list[str]) -> dict:
    """Inline allergen-context block — shown when an allergy is declared."""
    return {
        "type": "allergen_alert",
        "headline": f"Allergy noted: {', '.join(profile)}",
        "message": (
            "I'll flag any item that LISTS these in its ingredients. "
            "But for severe allergies, please call the restaurant before ordering — "
            "shared kitchens have cross-contamination risk I can't verify."
        ),
        "indicators": [
            "Menu allergen tags reflect listed ingredients only",
            "Items will show ⚠ on cards when they contain your allergen",
            "I won't 'promise' anything is allergen-free"
        ],
        "offer": "Continue browsing — I'll keep allergen awareness on for the rest of this session.",
    }


def _check_cart_for_allergens(cart: list[CartLine], profile: list[str]) -> list[str]:
    warnings = []
    for line in cart:
        hits = [a for a in profile if a in line.allergens]
        if hits:
            warnings.append(f"{line.name} contains {', '.join(hits)}")
    return warnings


def _filter_by_diet(items: list[dict], diet: str) -> list[dict]:
    if diet == "vegan":
        # Demo: vegan ≈ veg and no dairy/egg
        return [i for i in items if i.get("veg") and "dairy" not in i.get("allergens", []) and "egg" not in i.get("allergens", [])]
    if diet == "vegetarian":
        return [i for i in items if i.get("veg")]
    if diet == "non_vegetarian":
        return [i for i in items if not i.get("veg")]
    if diet == "halal":
        # Demo: assume non-veg items in the catalog are halal-prepared (in real app, restaurant-level flag)
        return [i for i in items if i.get("veg") or not i.get("veg")]   # show all but note in handler
    if diet == "jain":
        # Demo: very narrow — veg + no onion/garlic. Our catalog doesn't tag those, so we return mostly desserts/bakery
        return [i for i in items if i.get("veg") and i["category"] in ("Cakes", "Pastries", "Bakes", "Drinks", "Smoothies", "Toasts")]
    if diet == "keto":
        # Demo: veg/non-veg with no gluten and not rice/breads/desserts
        return [i for i in items if "gluten" not in i.get("allergens", []) and i["category"] not in ("Rice", "Breads", "Desserts", "Cakes", "Pastries")]
    return items


# ─── Intent handlers ───────────────────────────────────────
def _handle_greeting(s: Session):
    return [
        _text(
            "Hi 👋 — I'm your Order Assistant. I can help you find restaurants, browse menus, "
            "add items to your cart, track an order, and apply offers. What are you hungry for?"
        )
    ], ["Show restaurants nearby", "Pizza places", "Track my order", "Any offers?"]


def _handle_goodbye(_s: Session):
    return [_text("Enjoy your meal. Come back hungry.")], []


def _handle_thanks(_s: Session):
    return [_text("You're welcome! Want me to suggest something else?")], \
           ["Recommend something", "Show menu", "View offers"]


def _handle_browse_restaurants(c: Classification, _s: Session):
    items = catalog.restaurants()
    cuisine = c.entities.get("cuisine")
    if cuisine:
        items = [r for r in items if cuisine in r["cuisine"]]
    open_now = [r for r in items if r["open_now"]]
    if open_now:
        items = open_now
    return [
        _text(f"I found **{len(items)} restaurants** that are open and deliver to you:"),
        {"type": "restaurant_list", "title": "Open now", "items": items, "total": len(items)},
    ], ["Show me Italian", "Show me Indian", "Quick delivery", "Top rated"]


def _handle_search_cuisine(c: Classification, _s: Session):
    cuisine = c.entities.get("cuisine") or ""
    restaurants = catalog.restaurants()
    if cuisine:
        restaurants = [r for r in restaurants if cuisine in r["cuisine"]]
    if not restaurants:
        return [_text(f"No {cuisine} restaurants in this demo's catalog. Try Italian, Chinese, Indian, Healthy, or Desserts.")], \
               ["Italian", "Chinese", "Indian", "Healthy"]
    return [
        _text(f"Here are {len(restaurants)} {cuisine or 'matching'} restaurants:"),
        {"type": "restaurant_list", "title": f"{cuisine} restaurants", "items": restaurants, "total": len(restaurants)},
    ], ["See menu of top option", "Any offers?", "Quick delivery", "Top rated"]


def _handle_restaurant_detail(c: Classification, s: Session):
    rid = c.entities.get("restaurant_id") or s.last_restaurant_id
    if not rid:
        return [_text("Which restaurant would you like to see? You can mention the name or paste a restaurant ID.")], \
               ["Show restaurants nearby", "Italian places", "Indian places"]
    r = catalog.restaurant(rid)
    if not r:
        return [_text(f"I couldn't find restaurant **{rid}**.")], []
    s.last_restaurant_id = rid
    return [
        _text(f"Here are the details on **{r['name']}**:"),
        {"type": "restaurant_detail", "restaurant": r},
    ], ["Show the menu", "Add a popular item", "View offers", "Add to cart"]


def _handle_view_menu(c: Classification, s: Session):
    rid = c.entities.get("restaurant_id") or s.last_restaurant_id
    if not rid:
        return [_text("Which restaurant's menu would you like? Try saying *'show me the menu of Saffron Kitchen'*.")], \
               ["Saffron Kitchen", "Green Bowl Co.", "Slice Society", "Wok Express"]
    r = catalog.restaurant(rid)
    items = catalog.menu(rid)
    if not items:
        return [_text(f"No menu found for {rid}.")], []
    s.last_restaurant_id = rid
    # Add allergen-warning flags based on session profile
    if s.allergen_profile:
        for it in items:
            it["allergen_warning"] = bool(set(it["allergens"]) & set(s.allergen_profile))
    return [
        _text(f"Here's the menu at **{r['name']}**:"),
        {"type": "menu", "restaurant": r, "items": items, "grouped": True},
    ], ["Add a popular item", "Vegan options", "Apply offer", "View cart"]


def _handle_dietary_filter(c: Classification, s: Session):
    from .safety import detect_diets
    diets = detect_diets(c.entities.get("cuisine") or "")  # cuisine field is wrong; use text
    # Re-detect on raw text via safety helper — but we don't have raw text here.
    # Instead: rely on the first diet keyword in the original classification.
    # For simplicity, default to whatever's stored in session
    if s.diet_profile:
        diet = s.diet_profile[-1]
    else:
        diet = "vegetarian"
    items = catalog.all_items()
    filtered = _filter_by_diet(items, diet)
    # Limit to 8 most relevant
    filtered = filtered[:8]
    label_map = {
        "vegan": "vegan", "vegetarian": "vegetarian", "non_vegetarian": "non-vegetarian",
        "halal": "halal-friendly", "jain": "jain-friendly", "keto": "keto-friendly",
    }
    note = ""
    if diet == "halal":
        note = "In a real platform, the restaurant flags halal preparation explicitly. Confirm with the restaurant if certification matters."
    elif diet == "jain":
        note = "Jain dietary restrictions (no onion/garlic, no root vegetables) require explicit restaurant confirmation. This filter is approximate."
    elif diet == "vegan":
        note = "Vegan filtering here is approximate — confirm milk/butter content with the restaurant for items like breads, sweets, or curries."
    return [
        _text(f"Here are **{len(filtered)} {label_map.get(diet, diet)} options** across restaurants:"),
        {"type": "dietary_filter", "diet": label_map.get(diet, diet), "matching_items": filtered, "note": note},
    ], ["Show menu of one", "Add to cart", "View offers"]


def _handle_add_to_cart(c: Classification, s: Session):
    item_id = c.entities.get("item_id")
    qty = c.entities.get("quantity") or 1
    if not item_id:
        return [_text(
            "Tell me which item — you can paste the item ID (like mi-001) or open a restaurant menu first."
        )], ["Show menu", "Browse restaurants"]
    item = catalog.item(item_id)
    if not item:
        return [_text(f"I couldn't find item **{item_id}**.")], []

    # Check alcohol gating
    if any(kw in item["name"].lower() for kw in ALCOHOL_KEYWORDS):
        return [build_age_gate_block()], ["Show non-alcoholic options", "Browse menu"]

    # Enforce single-restaurant cart
    item_rid = item["restaurant_id"]
    if s.cart_restaurant_id and s.cart_restaurant_id != item_rid:
        existing_r = catalog.restaurant(s.cart_restaurant_id)
        new_r = catalog.restaurant(item_rid)
        return [_text(
            f"Your cart has items from **{existing_r['name']}**. To add from **{new_r['name']}**, "
            "clear the cart first. (Most delivery apps restrict to one restaurant per order to keep delivery times reasonable.)"
        )], ["Clear cart", "View cart", "Continue with current cart"]

    # Add the item
    s.cart_restaurant_id = item_rid
    s.cart.append(CartLine(
        item_id=item["id"], name=item["name"], price=item["price"],
        qty=qty, allergens=item.get("allergens", []),
    ))

    # Build cart summary
    return _render_cart_response(s, just_added=item["name"])


def _render_cart_response(s: Session, just_added: str | None = None):
    if not s.cart:
        return [_text("Your cart is empty. Add some items to get started.")], ["Browse restaurants", "Show offers"]

    r = catalog.restaurant(s.cart_restaurant_id) if s.cart_restaurant_id else None
    lines = [{"name": l.name, "qty": l.qty, "price": l.price, "allergens": l.allergens,
              "has_warning": bool(set(l.allergens) & set(s.allergen_profile))} for l in s.cart]
    subtotal = sum(l.price * l.qty for l in s.cart)
    delivery_fee = 30
    tax = round(subtotal * 0.05, 2)
    discount = 0.0
    applied_offer = s.applied_offer
    if applied_offer == "FIRSTBITE" and subtotal >= 300:
        discount = min(subtotal * 0.5, 150)
    elif applied_offer == "BOWLSAVE" and s.cart_restaurant_id == "REST-202" and subtotal >= 250:
        discount = subtotal * 0.20
    elif applied_offer == "DESSERT100" and subtotal >= 400:
        discount = 100
    total = max(subtotal + delivery_fee + tax - discount, 0)

    allergen_warnings = _check_cart_for_allergens(s.cart, s.allergen_profile)

    blocks = []
    if just_added:
        blocks.append(_text(f"Added **{just_added}** to your cart."))
    else:
        if r:
            blocks.append(_text(f"Here's your cart from **{r['name']}**:"))
        else:
            blocks.append(_text("Here's your cart:"))
    blocks.append({
        "type": "cart",
        "restaurant_name": r["name"] if r else None,
        "items": lines,
        "subtotal": subtotal, "delivery_fee": delivery_fee, "tax": tax,
        "discount": discount, "total": total,
        "applied_offer": applied_offer,
        "allergen_warnings": allergen_warnings,
    })
    if allergen_warnings:
        blocks.append(_disclaimer(
            "Cart items contain ingredients you've flagged. Cross-contamination is a kitchen-level "
            "concern — call the restaurant before ordering if your allergy is severe."
        ))
    return blocks, ["Add more items", "Apply offer", "Checkout"]


def _handle_view_cart(_c: Classification, s: Session):
    return _render_cart_response(s)


def _handle_track_order(c: Classification, _s: Session):
    oid = c.entities.get("order_id") or "ORD-DEMO-001"
    return [
        _text(f"Tracking order **{oid}**:"),
        {
            "type": "order_tracking",
            "order_id": oid,
            "restaurant_name": "Saffron Kitchen",
            "status": "Out for delivery",
            "steps": [
                {"label": "Order placed",      "done": True,  "time": "7:42 PM"},
                {"label": "Restaurant accepted","done": True, "time": "7:43 PM"},
                {"label": "Preparing food",     "done": True, "time": "7:45 PM"},
                {"label": "Picked up",          "done": True, "time": "8:08 PM"},
                {"label": "Out for delivery",   "done": True, "time": "8:09 PM"},
                {"label": "Delivered",          "done": False, "time": ""},
            ],
            "eta_minutes": 8,
            "rider": {"name": "Mr. Karan Mehta", "vehicle": "Two-wheeler · GJ05XX1234", "phone": "+91 98XX XX4287"},
        },
    ], ["Contact rider", "Order status", "Talk to support"]


def _handle_order_history(_c: Classification, _s: Session):
    items = catalog.recent_orders()
    return [
        _text(f"Here are your **{len(items)} most recent orders**:"),
        {"type": "order_history", "items": items},
    ], ["Reorder the last one", "Reorder Green Bowl", "Browse restaurants"]


def _handle_reorder(_c: Classification, s: Session):
    items = catalog.recent_orders()
    if not items:
        return [_text("You don't have any recent orders to reorder yet.")], ["Browse restaurants"]
    last = items[0]
    # Build cart from last order
    s.cart_restaurant_id = last["restaurant_id"]
    s.cart = []
    for it in last["items"]:
        # Find the item by name in the catalog
        rid_items = catalog.menu(last["restaurant_id"])
        match = next((x for x in rid_items if x["name"] == it["name"]), None)
        if match:
            s.cart.append(CartLine(
                item_id=match["id"], name=match["name"], price=match["price"],
                qty=it["qty"], allergens=match.get("allergens", []),
            ))
    blocks, suggestions = _render_cart_response(s, just_added=None)
    blocks.insert(0, _text(f"I've rebuilt your last order from **{last['restaurant_name']}** in your cart:"))
    return blocks, suggestions


def _handle_view_offers(_c: Classification, _s: Session):
    items = catalog.offers()
    return [
        _text(f"You have **{len(items)} offers** available right now:"),
        {"type": "offers", "items": items},
    ], ["Apply FIRSTBITE", "Apply BOWLSAVE", "Apply DESSERT100"]


def _handle_apply_offer(c: Classification, s: Session):
    code = c.entities.get("offer_code")
    if not code:
        return [_text("Which offer code would you like to apply? Say *'apply FIRSTBITE'* or check the offers list.")], \
               ["View offers"]
    # Validate against catalog
    valid_codes = {o["code"] for o in catalog.offers()}
    if code not in valid_codes:
        return [_text(f"**{code}** isn't a valid offer code in this demo. Check 'View offers' for available codes.")], \
               ["View offers"]
    s.applied_offer = code
    blocks, suggestions = _render_cart_response(s)
    blocks.insert(0, _text(f"Applied offer **{code}**. Your cart total has been updated:"))
    return blocks, suggestions


def _handle_manage_addresses(_c: Classification, _s: Session):
    items = catalog.addresses()
    return [
        _text(f"Here are your **{len(items)} saved delivery addresses**:"),
        {"type": "addresses", "items": items},
    ], ["Deliver to Home", "Deliver to Work", "Add new address"]


def _handle_recommend(_c: Classification, s: Session):
    # Pick a popular set across restaurants
    pool = catalog.all_items()
    # Filter by allergen profile if set
    if s.allergen_profile:
        pool = [i for i in pool if not (set(i["allergens"]) & set(s.allergen_profile))]
    # Filter by diet profile if set
    if "vegetarian" in s.diet_profile:
        pool = [i for i in pool if i.get("veg")]
    if "vegan" in s.diet_profile:
        pool = [i for i in pool if i.get("veg") and "dairy" not in i["allergens"] and "egg" not in i["allergens"]]
    # Curated picks
    picks = []
    seen_rids = set()
    for it in pool:
        if it["restaurant_id"] not in seen_rids and len(picks) < 4:
            picks.append(it)
            seen_rids.add(it["restaurant_id"])
    rationale = "Based on what's popular tonight"
    if s.allergen_profile or s.diet_profile:
        parts = []
        if s.allergen_profile:
            parts.append(f"avoiding {', '.join(s.allergen_profile)}")
        if s.diet_profile:
            parts.append(f"matching {', '.join(s.diet_profile)} preference")
        rationale += f" — {' and '.join(parts)}"
    return [
        _text("Here are a few hand-picked recommendations from different restaurants:"),
        {"type": "recommendation", "rationale": rationale, "items": picks},
    ], ["Add a recommendation", "Show me more", "View cart"]


def _handle_contact_support(_c: Classification, _s: Session):
    return [_text(
        "Sure — for issues with a recent order (refunds, missing items, late delivery), our support team is the right place. "
        "In this demo, support isn't connected to a real ticket system. In a production app, this would open a chat with a human agent or create a support ticket."
    )], ["Track my order", "Order history", "View cart"]


def _handle_unknown(_c: Classification, _s: Session):
    return [_text(
        "I'm not sure I caught that. I can show restaurants, browse menus, add to cart, track orders, "
        "apply offers, or recommend something. Try one of the buttons below."
    )], ["Browse restaurants", "Track my order", "View offers", "Recommend something"]


# ─── Engine ────────────────────────────────────────────────
class ChatbotEngine:
    def respond(self, message: str, session: Session) -> dict:
        safety = check_safety(message)

        # Hard short-circuits — refuse and explain
        if safety.flag == "social_engineering":
            return self._safety_response(session, "social_engineering",
                                         build_social_engineering_block(),
                                         ["Browse restaurants", "Track order", "View offers"])
        if safety.flag == "payment_privacy":
            return self._safety_response(session, "payment_privacy",
                                         build_payment_privacy_block(),
                                         ["Go to checkout", "View cart", "Track order"])
        if safety.flag == "allergen_promise":
            return self._safety_response(session, "allergen_promise",
                                         build_allergen_promise_block(safety.detected_allergens),
                                         ["Show allergen-aware items", "Call the restaurant", "Browse safer options"])

        # ENRICH session with detected allergens/diets — additive
        added_allergens = [a for a in safety.detected_allergens if a not in session.allergen_profile]
        added_diets     = [d for d in safety.detected_diets if d not in session.diet_profile]
        session.allergen_profile.extend(added_allergens)
        session.diet_profile.extend(added_diets)

        # 2️⃣ Classify intent
        c = classify(message)
        session.last_intent = c.intent
        session.history.append({"role": "user", "text": message})

        # Cache restaurant_id from entity
        if c.entities.get("restaurant_id"):
            session.last_restaurant_id = c.entities["restaurant_id"]

        handler_map = {
            "greeting":            lambda: _handle_greeting(session),
            "goodbye":             lambda: _handle_goodbye(session),
            "thanks":              lambda: _handle_thanks(session),
            "browse_restaurants":  lambda: _handle_browse_restaurants(c, session),
            "search_cuisine":      lambda: _handle_search_cuisine(c, session),
            "restaurant_detail":   lambda: _handle_restaurant_detail(c, session),
            "view_menu":           lambda: _handle_view_menu(c, session),
            "dietary_filter":      lambda: _handle_dietary_filter(c, session),
            "add_to_cart":         lambda: _handle_add_to_cart(c, session),
            "view_cart":           lambda: _handle_view_cart(c, session),
            "track_order":         lambda: _handle_track_order(c, session),
            "order_history":       lambda: _handle_order_history(c, session),
            "reorder":             lambda: _handle_reorder(c, session),
            "view_offers":         lambda: _handle_view_offers(c, session),
            "apply_offer":         lambda: _handle_apply_offer(c, session),
            "manage_addresses":    lambda: _handle_manage_addresses(c, session),
            "recommend":           lambda: _handle_recommend(c, session),
            "contact_support":     lambda: _handle_contact_support(c, session),
        }
        handler = handler_map.get(c.intent, lambda: _handle_unknown(c, session))
        blocks, suggestions = handler()

        # Prepend an allergen callout if the user just declared allergies in this message
        if added_allergens:
            blocks.insert(0, _allergen_callout(added_allergens))

        return {
            "session_id":  session.session_id,
            "intent":      c.intent,
            "confidence":  c.confidence,
            "blocks":      blocks,
            "suggestions": suggestions,
            "safety_flag": "allergen_declared" if added_allergens else None,
        }

    def _safety_response(self, session: Session, flag: str, block: dict, suggestions: list[str]):
        return {
            "session_id":  session.session_id,
            "intent":      f"{flag}_block",
            "confidence":  1.0,
            "blocks":      [block],
            "suggestions": suggestions,
            "safety_flag": flag,
        }


engine = ChatbotEngine()
