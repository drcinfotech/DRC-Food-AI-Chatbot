"""
Intent classifier for the Food, Restaurant Ordering & Delivery chatbot.

Safety detection (see safety.py) runs BEFORE this classifier — but unlike
fair-housing or academic-integrity bots, allergen detection ENRICHES context
rather than blocking it. Most safety hits here are advisory, not refusal.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class IntentSpec:
    name: str
    patterns: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


INTENTS: list[IntentSpec] = [
    IntentSpec(
        "greeting",
        patterns=[r"^\s*(hi|hello|hey|hola|namaste|good (morning|afternoon|evening))\b"],
        keywords=["hi", "hello", "hey", "hola", "namaste"],
    ),
    IntentSpec(
        "goodbye",
        patterns=[r"\b(bye|goodbye|see ya|see you|cya|take care)\b"],
        keywords=["bye", "goodbye"],
    ),
    IntentSpec(
        "thanks",
        patterns=[r"^\s*(thanks|thank you|thx|ty|appreciate it)\b"],
        keywords=["thanks", "thank"],
    ),
    IntentSpec(
        "browse_restaurants",
        patterns=[
            r"\b(show|list|find|browse|explore)\s+(me\s+)?(restaurants?|places? to eat|food places?|eateries)",
            r"\bwhat'?s\s+(good|nearby|around|open)\s+(to eat|for (lunch|dinner|breakfast))?",
            r"\b(restaurants?|food)\s+near\s+(me|here)",
            r"\bopen\s+(now|right now|currently)\b",
        ],
        keywords=["restaurants", "places to eat", "what's nearby"],
    ),
    IntentSpec(
        "search_cuisine",
        patterns=[
            r"\b(i want|i'?m craving|craving|looking for|find)\s+(some\s+)?(pizza|pasta|biryani|noodles|momos|chinese|italian|indian|north indian|south indian|continental|burger|salad|dessert|cake|coffee)",
            r"\b(pizza|pasta|biryani|noodles|momos|chinese|italian|indian|burger|salad|dessert|cake|coffee)\s+(places?|restaurants?|delivery|near\s+me)",
            r"\bwhere\s+can\s+i\s+(get|find)\s+(\w+)\s+(pizza|pasta|biryani|noodles|momos|chinese|italian|burger|salad|dessert|cake|coffee)",
        ],
        keywords=["pizza", "pasta", "biryani", "noodles", "chinese", "italian", "burger", "salad", "dessert"],
    ),
    IntentSpec(
        "restaurant_detail",
        patterns=[
            r"\b(show|tell me about|info on|details? (of|on|for|about))\s+(\w+\s+)?(restaurant|place)",
            r"\bmore (info|details|about)\s+(this|that)\s+(restaurant|place)",
            r"\bopen this restaurant\b",
            r"\brest-?\d+\b",
        ],
        keywords=["restaurant details", "rest-"],
    ),
    IntentSpec(
        "view_menu",
        patterns=[
            r"\b(show|view|see|open)\s+(me\s+)?(the\s+)?menu\b",
            r"\bwhat'?s\s+on\s+(the\s+)?menu\b",
            r"\b(menu|dishes|items)\s+(at|of|for|from)\s+",
            r"\bmenu\s+of\b",
        ],
        keywords=["menu", "see menu", "what's on the menu"],
    ),
    IntentSpec(
        "dietary_filter",
        patterns=[
            r"\b(vegan|vegetarian|veg only|veg-only|jain|halal|keto|gluten[\s-]?free|nut[\s-]?free|dairy[\s-]?free)\s+(options?|items?|dishes?|menu|food|restaurants?)",
            r"\b(show|find|filter|only)\s+(me\s+)?(vegan|vegetarian|jain|halal|keto)\s+",
            r"\b(only|just)\s+(vegan|vegetarian|jain|halal|keto)\b",
            r"\bwhat\s+(vegan|vegetarian|jain|halal|keto|gluten[\s-]?free)\s+(items?|dishes?|options?)",
        ],
        keywords=["vegan", "jain food", "halal options", "keto", "gluten free", "dairy free"],
    ),
    IntentSpec(
        "add_to_cart",
        patterns=[
            r"\b(add|order|get|i'?ll have|i want|i'?ll take)\s+(\d+\s+)?(\w+\s+)?(to\s+(my\s+)?cart|to\s+order)?",
            r"\b(\d+\s+)?(plate|piece|portion)s?\s+of\b",
            r"\b(order|add)\s+(me\s+)?(a|an|the)?\s+\w+",
        ],
        keywords=["add to cart", "order this", "I want"],
    ),
    IntentSpec(
        "view_cart",
        patterns=[
            r"\b(show|view|see|open|check)\s+(my\s+)?cart\b",
            r"\bwhat'?s\s+in\s+my\s+cart\b",
            r"\bmy\s+cart\b",
            r"\bgo\s+to\s+checkout\b",
            r"\bcheckout\b",
        ],
        keywords=["cart", "my cart", "checkout"],
    ),
    IntentSpec(
        "track_order",
        patterns=[
            r"\b(track|status|where\s+is)\s+(my\s+)?(order|food|delivery)\b",
            r"\bwhen\s+will\s+(my\s+)?(food|order)\s+(arrive|come|be here)\b",
            r"\border\s+(status|tracking)\b",
            r"\bord-?\d+\b",
            r"\bhow\s+much\s+longer\b",
        ],
        keywords=["track order", "order status", "where is my food"],
    ),
    IntentSpec(
        "order_history",
        patterns=[
            r"\b(my\s+)?(past|previous|previous orders|order\s+history|recent orders?)\b",
            r"\bwhat\s+did\s+i\s+order\s+(last|before|recently)\b",
            r"\b(show|view|list)\s+(me\s+)?(my\s+)?(past|previous|recent)\s+orders?",
        ],
        keywords=["order history", "past orders", "recent orders"],
    ),
    IntentSpec(
        "reorder",
        patterns=[
            r"\b(re[\s-]?order|order\s+again|same\s+as\s+(last\s+time|before|yesterday))\b",
            r"\brepeat\s+(my\s+)?(last|previous)\s+order\b",
            r"\b(get|order)\s+the\s+same\s+thing\b",
        ],
        keywords=["reorder", "order again", "same as last time"],
    ),
    IntentSpec(
        "view_offers",
        patterns=[
            r"\b(any\s+)?(offers?|deals?|discounts?|coupons?|promo\s+codes?)\b",
            r"\b(what|show)\s+(offers?|deals?|discounts?)\b",
            r"\bsave\s+money\b",
            r"\bdiscount\s+(available|today|now)\b",
        ],
        keywords=["offers", "deals", "discount", "coupon", "promo"],
    ),
    IntentSpec(
        "apply_offer",
        patterns=[
            r"\bapply\s+(offer|code|coupon|promo)\b",
            r"\b(use|apply)\s+([A-Z]{4,12}\d*)\b",
        ],
        keywords=["apply offer", "use code"],
    ),
    IntentSpec(
        "manage_addresses",
        patterns=[
            r"\b(my\s+)?(addresses?|delivery\s+addresses?|saved\s+addresses?)\b",
            r"\b(change|update|set)\s+(my\s+)?(delivery\s+)?address\b",
            r"\bdeliver\s+to\s+(home|work|office)\b",
        ],
        keywords=["addresses", "delivery address", "change address"],
    ),
    IntentSpec(
        "recommend",
        patterns=[
            r"\b(recommend|suggest|what should i|what would you|surprise me|pick (for|something))\b",
            r"\b(don'?t know what to order|cant decide|can'?t decide)\b",
            r"\bwhat'?s good (here|tonight|today)\b",
            r"\bpopular\s+(items?|dishes?|orders?)\b",
        ],
        keywords=["recommend", "suggest", "what should I order", "surprise me"],
    ),
    IntentSpec(
        "contact_support",
        patterns=[
            r"\b(contact|talk to|speak to|reach)\s+(support|customer\s+(service|care)|help)",
            r"\b(human|real person|agent|representative)\b",
            r"\b(refund|complaint|issue|problem)\s+(with|about|on)\s+(my\s+)?order",
        ],
        keywords=["support", "customer service", "refund", "complaint"],
    ),
]


# ─── Entity extraction ─────────────────────────────────────
RESTAURANT_KEYWORDS = {
    "REST-101": ["saffron", "saffron kitchen"],
    "REST-202": ["green bowl", "greenbowl", "green bowl co"],
    "REST-303": ["slice society", "slice"],
    "REST-404": ["wok express", "wok"],
    "REST-505": ["bake theory", "bake"],
    "REST-606": ["tandoor", "tandoor & tales", "tandoor and tales"],
}

CUISINE_KEYWORDS = {
    "Italian":   ["pizza", "pasta", "italian"],
    "Chinese":   ["chinese", "indo-chinese", "noodles", "momos", "manchurian"],
    "Indian":    ["biryani", "kebab", "tikka", "naan", "indian", "north indian", "mughlai", "tandoori"],
    "Healthy":   ["salad", "bowl", "smoothie", "healthy"],
    "Desserts":  ["dessert", "cake", "pastry", "tiramisu", "ice cream"],
}


def extract_restaurant_id(text: str) -> Optional[str]:
    t = text.lower()
    # Explicit REST-### id
    m = re.search(r"\brest-?(\d{2,4})\b", t)
    if m:
        return f"REST-{m.group(1)}"
    # Keyword match (longest match wins to disambiguate "bake" vs "bake theory")
    best = None
    best_len = 0
    for rid, kws in RESTAURANT_KEYWORDS.items():
        for kw in kws:
            if kw in t and len(kw) > best_len:
                best = rid
                best_len = len(kw)
    return best


def extract_cuisine(text: str) -> Optional[str]:
    t = text.lower()
    for cuisine, kws in CUISINE_KEYWORDS.items():
        if any(kw in t for kw in kws):
            return cuisine
    return None


def extract_item_id(text: str) -> Optional[str]:
    """Item ids look like mi-001."""
    m = re.search(r"\bmi-?(\d{3})\b", text.lower())
    if m:
        return f"mi-{m.group(1)}"
    return None


def extract_order_id(text: str) -> Optional[str]:
    m = re.search(r"\bord-?(\d{4,6})\b", text.lower())
    if m:
        return f"ORD-{m.group(1)}"
    return None


def extract_quantity(text: str) -> int:
    """Extract leading qty in 'add 2 X' or '3 plates of X'."""
    m = re.search(r"\b(\d+)\s+(plate|piece|portion|of|x|servings?)\b", text.lower())
    if m:
        return int(m.group(1))
    # 'add 2 paneer'
    m2 = re.search(r"\b(?:add|order|get|i want)\s+(\d+)\s+", text.lower())
    if m2:
        return int(m2.group(1))
    return 1


def extract_offer_code(text: str) -> Optional[str]:
    """Offer codes are uppercase 4-12 chars + optional digits."""
    m = re.search(r"\b([A-Z]{4,12}\d{0,4})\b", text)
    if m:
        return m.group(1)
    return None


# ─── Classifier ────────────────────────────────────────────
@dataclass
class Classification:
    intent: str
    confidence: float
    entities: dict


def classify(text: str) -> Classification:
    raw = text
    text_lc = text.lower().strip()

    scores: dict[str, float] = {}
    for spec in INTENTS:
        score = 0.0
        for p in spec.patterns:
            if re.search(p, text_lc, re.IGNORECASE):
                score += 2.0
        for kw in spec.keywords:
            if re.search(rf"\b{re.escape(kw)}\b", text_lc):
                score += 0.6
        if score > 0:
            scores[spec.name] = score

    # Disambiguation boosts
    if extract_order_id(text):
        scores["track_order"] = scores.get("track_order", 0) + 2.0
    if extract_item_id(text):
        scores["add_to_cart"] = scores.get("add_to_cart", 0) + 1.5

    if not scores:
        intent, conf = "unknown", 0.0
    else:
        intent = max(scores, key=scores.get)
        top = scores[intent]
        rest = sorted(scores.values(), reverse=True)[1] if len(scores) > 1 else 0.1
        conf = min(1.0, top / (top + rest))

    entities = {
        "restaurant_id": extract_restaurant_id(raw),
        "cuisine":       extract_cuisine(raw),
        "item_id":       extract_item_id(raw),
        "order_id":      extract_order_id(raw),
        "quantity":      extract_quantity(raw),
        "offer_code":    extract_offer_code(raw),
    }
    return Classification(intent=intent, confidence=round(conf, 2), entities=entities)
