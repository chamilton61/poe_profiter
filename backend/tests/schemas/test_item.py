import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from app.schemas.item import ItemCreate, PriceCreate
from app.schemas.item import Item as ItemSchema


def valid_item_data(**kwargs):
    defaults = {
        "poe_id": "abc123",
        "base_type": "Mirror of Kalandra",
        "category": "Currency",
        "seller_account": "seller1",
        "indexed_at": datetime.now(timezone.utc),
        "item_snapshot": {"typeLine": "Mirror of Kalandra"},
    }
    defaults.update(kwargs)
    return defaults


def test_item_create_valid():
    item = ItemCreate(**valid_item_data())
    assert item.poe_id == "abc123"
    assert item.category == "Currency"
    assert item.name is None


def test_item_create_with_name():
    item = ItemCreate(**valid_item_data(name="Mirror of Kalandra"))
    assert item.name == "Mirror of Kalandra"


def test_item_create_missing_poe_id():
    with pytest.raises(ValidationError):
        data = valid_item_data()
        del data["poe_id"]
        ItemCreate(**data)


def test_item_create_missing_base_type():
    with pytest.raises(ValidationError):
        data = valid_item_data()
        del data["base_type"]
        ItemCreate(**data)


def test_price_create_valid():
    price = PriceCreate(price_type="~price", price=50.0, currency="chaos")
    assert price.price == 50.0
    assert price.currency == "chaos"
    assert price.price_type == "~price"


def test_price_create_missing_price():
    with pytest.raises(ValidationError):
        PriceCreate(price_type="~price", currency="chaos")


def test_price_create_missing_currency():
    with pytest.raises(ValidationError):
        PriceCreate(price_type="~price", price=50.0)


def test_price_create_missing_price_type():
    with pytest.raises(ValidationError):
        PriceCreate(price=50.0, currency="chaos")


def test_item_schema_from_orm(sample_item, sample_price):
    schema = ItemSchema.model_validate(sample_item)
    assert schema.id == sample_item.id
    assert schema.poe_id == sample_item.poe_id
    assert schema.category == sample_item.category
    assert len(schema.prices) >= 1
