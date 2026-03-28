from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.item import Item, Price
from app.repositories.base import BaseRepository


class ItemRepository(BaseRepository[Item]):
    """Repository for Item model with custom methods."""

    def __init__(self, db: Session):
        super().__init__(Item, db)

    def get_by_poe_id(self, poe_id: str) -> Optional[Item]:
        """Get an item by its trade API poe_id."""
        return self.db.query(self.model).filter(self.model.poe_id == poe_id).first()


class PriceRepository(BaseRepository[Price]):
    """Repository for Price model with custom methods."""

    def __init__(self, db: Session):
        super().__init__(Price, db)

    def get_by_item_id(
        self, item_id: int, skip: int = 0, limit: int = 100
    ) -> List[Price]:
        """Get prices for a specific item."""
        return (
            self.db.query(self.model)
            .filter(self.model.item_id == item_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
