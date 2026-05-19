"""
Safety layer for the Food, Restaurant Ordering & Delivery chatbot.

Headline concern: ALLERGEN SAFETY. Anaphylaxis is the worst outcome in this
domain — a peanut allergy that the bot dismisses or mishandles can kill.

This module handles:
  • Allergen declarations — when a user states an allergy, we ENRICH the
    session with it so every downstream recommendation can be allergen-aware.
    We also REFUSE to "promise" allergen-free preparation, because
    cross-contamination is a kitchen-level concern that no chatbot can verify.
  • Age-gating — alcohol items require an age acknowledgment
  • Payment privacy — refuses to echo full card numbers or bypass payment flows
  • Prompt injection / social engineering

Detected allergies are NOT a "block" — they're a context flag. The bot keeps
helping, but with allergen awareness and a clear disclaimer.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional, Literal


# Standard allergen taxonomy
ALLERGENS = ["nuts", "peanut", "gluten", "dairy", "lactose", "egg", "shellfish",
             "fish", "soy", "sesame", "mustard", "celery", "sulphites"]

# Maps user phrasing → canonical allergen tag in the menu
ALLERGEN_ALIASES = {
    "nut":         "nuts",
    "nuts":        "nuts",
    "tree nut":    "nuts",
    "tree nuts":   "nuts",
    "almond":      "nuts",
    "walnut":      "nuts",
    "cashew":      "nuts",
    "pistachio":   "nuts",
    "peanut":      "nuts",   # treat peanut allergy as nuts for this demo
    "peanuts":     "nuts",
    "gluten":      "gluten",
    "wheat":       "gluten",
    "celiac":      "gluten",
    "coeliac":     "gluten",
    "dairy":       "dairy",
    "milk":        "dairy",
    "lactose":     "dairy",
    "cheese":      "dairy",
    "egg":         "egg",
    "eggs":        "egg",
    "shellfish":   "shellfish",
    "prawn":       "shellfish",
    "prawns":      "shellfish",
    "shrimp":      "shellfish",
    "fish":        "fish",
    "soy":         "soy",
    "soya":        "soy",
    "sesame":      "sesame",
    "til":         "sesame",
}

# Dietary preferences (not allergies — preferences)
DIETS = {
    "vegan":         ["vegan", "plant-based", "plant based"],
    "vegetarian":    ["vegetarian", "veg only", "veggie", "veg-only"],
    "non_vegetarian":["non veg", "non-veg", "non vegetarian", "meat"],
    "halal":         ["halal"],
    "jain":          ["jain food", "jain"],
    "keto":          ["keto", "ketogenic", "low carb", "low-carb"],
}


@dataclass
class SafetyResult:
    flag: Optional[Literal["allergen_promise", "age_gate", "payment_privacy", "social_engineering"]] = None
    detected_allergens: list[str] = field(default_factory=list)
    detected_diets:     list[str] = field(default_factory=list)
    reason: str = ""


# ─── Allergen DETECTION (not refusal — context enrichment) ─
def detect_allergens(text: str) -> list[str]:
    t = text.lower()
    found: set[str] = set()
    # Pattern: "I'm allergic to X" / "I have an X allergy" / "X allergy"
    if re.search(r"\b(allergic|allergy|allergies|intolerant|intolerance|cant eat|can'?t eat|avoid|no)\b", t):
        for alias, canon in ALLERGEN_ALIASES.items():
            # Word-boundary match against alias
            if re.search(rf"\b{re.escape(alias)}\b", t):
                found.add(canon)
    # Even without trigger words, celiac/coeliac always implies gluten
    if "celiac" in t or "coeliac" in t:
        found.add("gluten")
    return sorted(found)


def detect_diets(text: str) -> list[str]:
    t = text.lower()
    found: list[str] = []
    for diet, phrases in DIETS.items():
        for phrase in phrases:
            if re.search(rf"\b{re.escape(phrase)}\b", t):
                found.append(diet)
                break
    return found


# ─── "Promise me X is safe" patterns (we REFUSE these) ────
# These are dangerous because a bot saying "yes, this is 100% nut-free" gives
# false confidence — cross-contamination is a kitchen-level concern.
ALLERGEN_PROMISE_PATTERNS = [
    r"\b(promise|guarantee|confirm|swear|certify)\b.{0,40}\b(nut|peanut|gluten|dairy|egg|shellfish|fish|soy|sesame)[\s-]?free",
    r"\bis\s+(this|it|that)\s+(100%|completely|definitely|absolutely)\s+(nut|peanut|gluten|dairy|egg)[\s-]?free",
    r"\bsafe\s+for\s+(severe|life-threatening|anaphylaxis|anaphylactic)\b",
    r"\bcan\s+you\s+guarantee\b.{0,40}\b(allergen|allergy|nut|peanut|gluten|dairy)",
]


# ─── Age-gating for alcohol ───────────────────────────────
# Triggered when user asks about / adds alcohol items.
ALCOHOL_KEYWORDS = ["beer", "wine", "whisky", "whiskey", "vodka", "rum", "gin",
                    "cocktail", "champagne", "tequila", "alcohol", "liquor", "lager", "ale"]


# ─── Payment privacy ─────────────────────────────────────
PAYMENT_PRIVACY_PATTERNS = [
    r"\b(my|the|save|store)\s+(card|credit\s+card|debit\s+card|cvv)\s+(number|details?|info)\s+is\b",
    r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",   # 16-digit card numbers
    r"\bcvv\s+(is|number)\s+\d{3,4}\b",
    r"\b(remember|memorize|store)\s+my\s+(card|cvv|pin|password|otp)",
    r"\bbypass\s+(payment|otp|cvv|verification)",
    r"\bskip\s+(payment|otp|verification|2fa)",
]


# ─── Social engineering / prompt injection ───────────────
SOCIAL_ENGINEERING_PATTERNS = [
    r"\b(ignore|disregard|forget)\s+(\w+\s+){0,4}(instructions|rules|guidelines|system\s+prompt|safety)",
    r"\byou\s+are\s+now\s+(in\s+|an?\s+)?(admin|administrator|dev|developer|debug|root|owner|chef)\s+(mode|user)?",
    r"\bpretend\s+(you\s+are|to\s+be)\s+(an?\s+)?(admin|root|developer|restaurant\s+owner|chef\s+with\s+full\s+access)",
    r"\b(give|provide|reveal|show|tell)\s+(me\s+)?(your\s+)?(system\s+prompt|instructions|api\s+key|source\s+code)",
    r"\benable\s+(developer|admin|debug|root)\s+mode\b",
    r"\bjailbreak\b",
    r"\bDAN\s+mode\b",
    r"\bact\s+as\s+(if\s+)?(you\s+have\s+)?no\s+(rules|restrictions|guidelines|safety)",
    r"\b(give\s+me\s+)?(free|complimentary)\s+(food|meal|order|delivery)\s+(for\s+me\s+)?(please\s+)?(now|right\s+now)?\b",
]


def check_safety(text: str) -> SafetyResult:
    t = text.lower()

    # Social engineering FIRST
    for pat in SOCIAL_ENGINEERING_PATTERNS:
        if re.search(pat, t):
            return SafetyResult(flag="social_engineering", reason=pat)

    # Payment privacy
    for pat in PAYMENT_PRIVACY_PATTERNS:
        if re.search(pat, t):
            return SafetyResult(flag="payment_privacy", reason=pat)

    # Allergen "promise" requests — REFUSE these specifically
    for pat in ALLERGEN_PROMISE_PATTERNS:
        if re.search(pat, t):
            return SafetyResult(
                flag="allergen_promise",
                detected_allergens=detect_allergens(text),
                reason=pat,
            )

    # Otherwise, just enrich with detected allergens/diets — DON'T block
    return SafetyResult(
        flag=None,
        detected_allergens=detect_allergens(text),
        detected_diets=detect_diets(text),
    )


# ─── Block builders ───────────────────────────────────────
def build_allergen_promise_block(detected: list[str]) -> dict:
    return {
        "type": "allergen_alert",
        "headline": "I can't guarantee that.",
        "message": (
            "Cross-contamination happens in shared kitchens — a wok used for "
            "peanuts, a knife that cut bread, traces in the oil. No chatbot can verify "
            "what's actually happening in a restaurant's kitchen, and giving you a "
            "false 'yes, it's safe' is the kind of mistake that can put you in the ER. "
            "I won't do that, especially for severe or anaphylactic allergies."
        ),
        "indicators": [
            "Menu allergen tags are based on listed ingredients only",
            "Shared cooking equipment, oil, and surfaces create cross-contamination risk",
            "Severe / anaphylactic allergies need direct confirmation with the restaurant"
        ],
        "offer": (
            "What I CAN do: show you items that don't LIST your allergen in their "
            "ingredients, flag every cart item that does, and surface a callout for the "
            "restaurant to confirm preparation. For severe allergies, please call the "
            "restaurant directly before ordering."
        ),
    }


def build_age_gate_block() -> dict:
    return {
        "type": "allergen_alert",
        "headline": "Alcohol delivery has an age check.",
        "message": (
            "Alcohol orders require confirmation that you're of legal drinking age "
            "(21+ in Gujarat, where dry-state rules also apply; 25+ in some other Indian states). "
            "In real platforms, this is verified at delivery via ID. In this demo, I won't add "
            "alcoholic items without explicit acknowledgment."
        ),
        "indicators": [
            "India's legal drinking age varies by state (18–25)",
            "Gujarat is a dry state — alcohol sale/delivery requires special permits",
            "Real delivery platforms verify ID at handover, not at order"
        ],
        "offer": "Tell me your state and confirm you're of legal age, and I can show non-alcoholic alternatives in the meantime.",
    }


def build_payment_privacy_block() -> dict:
    return {
        "type": "allergen_alert",
        "headline": "Don't share card details in chat.",
        "message": (
            "I can't accept or store full card numbers, CVV, OTP, or PIN through chat — "
            "that's a security risk regardless of whether I'm 'asking' for it. Real payments "
            "go through encrypted gateways with PCI-DSS compliance, not free-text chat fields."
        ),
        "indicators": [
            "Card details typed in chat may be logged in plaintext",
            "Legitimate payment flows always use a dedicated, encrypted UI",
            "OTPs and PINs should NEVER be shared with anyone — including chatbots"
        ],
        "offer": "When you're ready to pay, the checkout flow handles cards / UPI / wallets through a proper gateway. I'll take you to checkout — just ask.",
    }


def build_social_engineering_block() -> dict:
    return {
        "type": "allergen_alert",
        "headline": "I can't do that.",
        "message": (
            "I'm not able to bypass my safety rules, switch into an 'admin' mode with "
            "elevated permissions, give out free orders, or reveal internal instructions. "
            "If you have a real ordering or delivery question, I'm happy to help."
        ),
        "indicators": [
            "I work the same way for everyone — there's no privileged mode to unlock",
            "Real customer support can do things I can't (refunds, comps, escalations)",
            "Use 'Contact support' for anything beyond ordering and tracking"
        ],
        "offer": "Try asking about restaurants, menus, your order status, or offers available right now.",
    }
