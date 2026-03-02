from app.models.item import Item
from app.repositories.base import BaseRepository


def make_repo(db):
    return BaseRepository(Item, db)


def test_create(db):
    repo = make_repo(db)
    item = repo.create({"name": "Exalted Orb", "category": "Currency"})
    assert item.id is not None
    assert item.name == "Exalted Orb"


def test_get(db):
    repo = make_repo(db)
    created = repo.create({"name": "Exalted Orb", "category": "Currency"})
    fetched = repo.get(created.id)
    assert fetched is not None
    assert fetched.id == created.id


def test_get_missing(db):
    repo = make_repo(db)
    assert repo.get(9999) is None


def test_get_all(db):
    repo = make_repo(db)
    repo.create({"name": "Item A", "category": "Cat"})
    repo.create({"name": "Item B", "category": "Cat"})
    items = repo.get_all()
    assert len(items) >= 2


def test_get_all_pagination(db):
    repo = make_repo(db)
    for i in range(5):
        repo.create({"name": f"Item {i}", "category": "Cat"})
    page = repo.get_all(skip=2, limit=2)
    assert len(page) == 2


def test_update(db):
    repo = make_repo(db)
    item = repo.create({"name": "Old Name", "category": "Currency"})
    updated = repo.update(item.id, {"name": "New Name"})
    assert updated is not None
    assert updated.name == "New Name"


def test_delete(db):
    repo = make_repo(db)
    item = repo.create({"name": "To Delete", "category": "Currency"})
    result = repo.delete(item.id)
    assert result is True
    assert repo.get(item.id) is None


def test_delete_missing(db):
    repo = make_repo(db)
    result = repo.delete(9999)
    assert result is False
