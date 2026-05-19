"""
Pydantic models for the Food, Restaurant Ordering & Delivery chatbot.
"""
from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field


# ─── Request ───────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    session_id: Optional[str] = None


# ─── Rich message blocks ───────────────────────────────────
class TextBlock(BaseModel):
    type: Literal["text"] = "text"
    content: str


class DisclaimerBlock(BaseModel):
    type: Literal["disclaimer"] = "disclaimer"
    content: str


class AllergenAlertBlock(BaseModel):
    """Shown when an allergy is declared or a safety guard fires."""
    type: Literal["allergen_alert"] = "allergen_alert"
    headline: str
    message: str
    indicators: list[str]
    offer: str


class RestaurantListBlock(BaseModel):
    type: Literal["restaurant_list"] = "restaurant_list"
    title: Optional[str] = None
    items: list[dict]
    total: int


class RestaurantDetailBlock(BaseModel):
    type: Literal["restaurant_detail"] = "restaurant_detail"
    restaurant: dict


class MenuBlock(BaseModel):
    type: Literal["menu"] = "menu"
    restaurant: dict
    items: list[dict]
    grouped: bool = True


class DishCardBlock(BaseModel):
    type: Literal["dish_card"] = "dish_card"
    item: dict
    restaurant_name: str


class CartBlock(BaseModel):
    type: Literal["cart"] = "cart"
    restaurant_name: Optional[str] = None
    items: list[dict]
    subtotal: float
    delivery_fee: float
    tax: float
    discount: float
    total: float
    applied_offer: Optional[str] = None
    allergen_warnings: list[str] = []


class OrderTrackingBlock(BaseModel):
    type: Literal["order_tracking"] = "order_tracking"
    order_id: str
    restaurant_name: str
    status: str
    steps: list[dict]
    eta_minutes: int
    rider: Optional[dict] = None


class OrderHistoryBlock(BaseModel):
    type: Literal["order_history"] = "order_history"
    items: list[dict]


class OffersBlock(BaseModel):
    type: Literal["offers"] = "offers"
    items: list[dict]


class AddressBlock(BaseModel):
    type: Literal["addresses"] = "addresses"
    items: list[dict]


class DietaryFilterBlock(BaseModel):
    """Shown when filtering by dietary preference."""
    type: Literal["dietary_filter"] = "dietary_filter"
    diet: str
    matching_items: list[dict]
    note: str


class RecommendationBlock(BaseModel):
    """Reorder suggestion / popular picks / based-on-history."""
    type: Literal["recommendation"] = "recommendation"
    rationale: str
    items: list[dict]


MessageBlock = (
    TextBlock | DisclaimerBlock | AllergenAlertBlock
    | RestaurantListBlock | RestaurantDetailBlock | MenuBlock | DishCardBlock
    | CartBlock | OrderTrackingBlock | OrderHistoryBlock | OffersBlock
    | AddressBlock | DietaryFilterBlock | RecommendationBlock
)


# ─── Response ──────────────────────────────────────────────
class ChatResponse(BaseModel):
    session_id: str
    intent: str
    confidence: float
    blocks: list[MessageBlock]
    suggestions: list[str] = []
    safety_flag: Optional[str] = None
