from datetime import datetime, timezone

from app.models.item import Item
from app.repositories.base import BaseRepository


def make_repo(db):
    return BaseRepository(Item, db)


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


def test_create(db):
    repo = make_repo(db)
    item = repo.create(item_data(poe_id="create1", base_type="Orb"))
    assert item.id is not None
    assert item.poe_id == "create1"


def test_get(db):
    repo = make_repo(db)
    created = repo.create(item_data(poe_id="get1"))
    fetched = repo.get(created.id)
    assert fetched is not None
    assert fetched.id == created.id


def test_get_missing(db):
    repo = make_repo(db)
    assert repo.get(9999) is None


def test_get_all(db):
    repo = make_repo(db)
    repo.create(item_data(poe_id="all1"))
    repo.create(item_data(poe_id="all2"))
    items = repo.get_all()
    assert len(items) >= 2


def test_get_all_pagination(db):
    repo = make_repo(db)
    for i in range(5):
        repo.create(item_data(poe_id=f"page{i}"))
    page = repo.get_all(skip=2, limit=2)
    assert len(page) == 2


def test_update(db):
    repo = make_repo(db)
    item = repo.create(item_data(poe_id="upd1", seller_account="old_seller"))
    updated = repo.update(item.id, {"seller_account": "new_seller"})
    assert updated is not None
    assert updated.seller_account == "new_seller"


def test_delete(db):
    repo = make_repo(db)
    item = repo.create(item_data(poe_id="del1"))
    result = repo.delete(item.id)
    assert result is True
    assert repo.get(item.id) is None


def test_delete_missing(db):
    repo = make_repo(db)
    result = repo.delete(9999)
    assert result is False
