from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


# TODO create a parent base class that has id, created_at, and updated_at so we have that functionality for all our models.
class Item(Base):
    """Model representing a specific trade listing."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    poe_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    base_type = Column(String, nullable=False)
    category = Column(String, nullable=False)
    seller_account = Column(String, nullable=False)
    indexed_at = Column(DateTime(timezone=True), nullable=False)
    item_snapshot = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    prices = relationship("Price", back_populates="item", cascade="all, delete-orphan")


class Price(Base):
    """Model representing a price observation for a trade listing."""

    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    price_type = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    item = relationship("Item", back_populates="prices")
