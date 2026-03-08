import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

import app.main as app_main
from app.core.database import Base, get_db
from app.main import app
from app.models.item import Item, Price


@pytest.fixture
def engine():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture
def db(engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(engine, db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    original_engine = app_main.engine
    app_main.engine = engine

    with TestClient(app) as c:
        yield c

    app_main.engine = original_engine
    app.dependency_overrides.clear()


@pytest.fixture
def sample_item(db):
    item = Item(
        poe_id="abc123",
        name="Mirror of Kalandra",
        base_type="Mirror of Kalandra",
        category="Currency",
        seller_account="seller1",
        indexed_at=datetime.now(timezone.utc),
        item_snapshot={"typeLine": "Mirror of Kalandra"},
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@pytest.fixture
def sample_price(db, sample_item):
    price = Price(
        item_id=sample_item.id,
        price_type="~price",
        price=100.0,
        currency="divine",
    )
    db.add(price)
    db.commit()
    db.refresh(price)
    return price
