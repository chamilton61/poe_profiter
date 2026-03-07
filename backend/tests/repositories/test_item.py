from datetime import datetime, timezone

from app.repositories.item import ItemRepository, PriceRepository


def item_data(**kwargs):
    defaults = {
        "poe_id": "default_id",
        "base_type": "Base",
        "category": "Currency",
        "seller_account": "seller",
        "indexed_at": datetime.now(timezone.utc),
        "item_snapshot": {},
    }
    defaults.update(kwargs)
    return defaults


def test_get_by_poe_id_found(db):
    repo = ItemRepository(db)
    repo.create(item_data(poe_id="abc123"))
    found = repo.get_by_poe_id("abc123")
    assert found is not None
    assert found.poe_id == "abc123"


def test_get_by_poe_id_not_found(db):
    repo = ItemRepository(db)
    assert repo.get_by_poe_id("nonexistent") is None


def test_price_get_by_item_id(db, sample_item, sample_price):
    repo = PriceRepository(db)
    prices = repo.get_by_item_id(sample_item.id)
    assert len(prices) >= 1
    assert all(p.item_id == sample_item.id for p in prices)


def test_price_get_by_item_id_pagination(db, sample_item):
    repo = PriceRepository(db)
    for i in range(4):
        repo.create({"item_id": sample_item.id, "price_type": "~price", "price": float(i), "currency": "chaos"})
    page = repo.get_by_item_id(sample_item.id, skip=1, limit=2)
    assert len(page) == 2
