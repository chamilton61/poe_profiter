from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class PriceBase(BaseModel):
    """Base schema for Price."""

    price_type: str
    price: float
    currency: str


class PriceCreate(PriceBase):
    """Schema for creating a Price."""

    pass


class Price(PriceBase):
    """Schema for Price response."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    item_id: int
    recorded_at: datetime


class ItemBase(BaseModel):
    """Base schema for Item."""

    poe_id: str
    name: Optional[str] = None
    base_type: str
    category: str
    seller_account: str
    indexed_at: datetime
    item_snapshot: dict


class ItemCreate(ItemBase):
    """Schema for creating an Item."""

    pass


class Item(ItemBase):
    """Schema for Item response."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    prices: List[Price] = []


class TradeSearchRequest(BaseModel):
    """Input schema for the trade search endpoint."""

    poesessid: Optional[str] = None
    league: str
    name: Optional[str] = None
    type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    currency: Optional[str] = None
    status: str = "online"
    page_size: int = 10
    page_offset: int = 0
    raw_query: Optional[dict] = None


class TradeSearchResponse(BaseModel):
    """Response schema for the trade search endpoint."""

    total: int
    page_size: int
    page_offset: int
    returned: int
    items: List[Item]
