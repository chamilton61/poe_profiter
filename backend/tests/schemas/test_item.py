import pytest
from pydantic import ValidationError

from app.schemas.item import ItemCreate, PriceCreate
from app.schemas.item import Item as ItemSchema


def test_item_create_valid():
    item = ItemCreate(name="Chaos Orb", category="Currency")
    assert item.name == "Chaos Orb"
    assert item.category == "Currency"
    assert item.base_type is None


def test_item_create_with_base_type():
    item = ItemCreate(name="Headhunter", category="Belt", base_type="Leather Belt")
    assert item.base_type == "Leather Belt"


def test_item_create_missing_name():
    with pytest.raises(ValidationError):
        ItemCreate(category="Currency")


def test_item_create_missing_category():
    with pytest.raises(ValidationError):
        ItemCreate(name="Chaos Orb")


def test_price_create_valid():
    price = PriceCreate(price=50.0, currency="chaos")
    assert price.price == 50.0
    assert price.currency == "chaos"


def test_price_create_missing_price():
    with pytest.raises(ValidationError):
        PriceCreate(currency="chaos")


def test_price_create_missing_currency():
    with pytest.raises(ValidationError):
        PriceCreate(price=50.0)


def test_item_schema_from_orm(sample_item, sample_price):
    schema = ItemSchema.model_validate(sample_item)
    assert schema.id == sample_item.id
    assert schema.name == sample_item.name
    assert schema.category == sample_item.category
    assert len(schema.prices) >= 1
