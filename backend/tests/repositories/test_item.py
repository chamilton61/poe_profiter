from app.repositories.item import ItemRepository, PriceRepository


def test_get_by_name_found(db):
    repo = ItemRepository(db)
    repo.create({"name": "Mirror of Kalandra", "category": "Currency"})
    found = repo.get_by_name("Mirror of Kalandra")
    assert found is not None
    assert found.name == "Mirror of Kalandra"


def test_get_by_name_not_found(db):
    repo = ItemRepository(db)
    assert repo.get_by_name("Nonexistent Item") is None


def test_get_by_category_filters(db):
    repo = ItemRepository(db)
    repo.create({"name": "Chaos Orb", "category": "Currency"})
    repo.create({"name": "Divine Orb", "category": "Currency"})
    repo.create({"name": "Oni-Goroshi", "category": "Weapon"})
    results = repo.get_by_category("Currency")
    assert len(results) == 2
    assert all(item.category == "Currency" for item in results)


def test_get_by_category_pagination(db):
    repo = ItemRepository(db)
    for i in range(5):
        repo.create({"name": f"Currency {i}", "category": "Currency"})
    page = repo.get_by_category("Currency", skip=1, limit=2)
    assert len(page) == 2


def test_price_get_by_item_id(db, sample_item, sample_price):
    repo = PriceRepository(db)
    prices = repo.get_by_item_id(sample_item.id)
    assert len(prices) >= 1
    assert all(p.item_id == sample_item.id for p in prices)


def test_price_get_by_item_id_pagination(db, sample_item):
    repo = PriceRepository(db)
    for i in range(4):
        repo.create({"item_id": sample_item.id, "price": float(i), "currency": "chaos"})
    page = repo.get_by_item_id(sample_item.id, skip=1, limit=2)
    assert len(page) == 2
