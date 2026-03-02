from app.models.item import Item, Price


def test_item_create(db):
    item = Item(name="Test Item", category="Currency")
    db.add(item)
    db.commit()
    db.refresh(item)
    assert item.id is not None
    assert item.name == "Test Item"
    assert item.created_at is not None


def test_price_create(db, sample_item):
    price = Price(item_id=sample_item.id, price=42.5, currency="chaos")
    db.add(price)
    db.commit()
    db.refresh(price)
    assert price.id is not None
    assert price.price == 42.5
    assert price.recorded_at is not None


def test_item_prices_relationship(db, sample_item, sample_price):
    db.refresh(sample_item)
    assert len(sample_item.prices) >= 1
    assert any(p.id == sample_price.id for p in sample_item.prices)


def test_cascade_delete(db, sample_item, sample_price):
    price_id = sample_price.id
    db.delete(sample_item)
    db.commit()
    deleted_price = db.query(Price).filter(Price.id == price_id).first()
    assert deleted_price is None
