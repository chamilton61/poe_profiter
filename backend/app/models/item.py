from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

#TODO create a parent base class that has id, created_at, and updated_at so we have that functionality for all our models.
class Item(Base):
    """Model representing an item in the game."""
    
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    category = Column(String, nullable=False)
    base_type = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    prices = relationship("Price", back_populates="item", cascade="all, delete-orphan")


class Price(Base):
    """Model representing a price entry for an item."""
    
    __tablename__ = "prices"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    item = relationship("Item", back_populates="prices")
