from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class PriceBase(BaseModel):
    """Base schema for Price."""
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
    name: str
    category: str
    base_type: Optional[str] = None


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
