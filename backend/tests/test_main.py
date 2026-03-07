from datetime import datetime, timezone


def valid_item_payload(**kwargs):
    defaults = {
        "poe_id": "abc123",
        "base_type": "Mirror of Kalandra",
        "category": "Currency",
        "seller_account": "seller1",
        "indexed_at": datetime.now(timezone.utc).isoformat(),
        "item_snapshot": {"typeLine": "Mirror of Kalandra"},
    }
    defaults.update(kwargs)
    return defaults


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World from POE Profiter!"}


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_item(client):
    response = client.post("/items/", json=valid_item_payload())
    assert response.status_code == 200
    data = response.json()
    assert data["poe_id"] == "abc123"
    assert data["category"] == "Currency"
    assert data["id"] is not None


def test_read_items(client, sample_item):
    response = client.get("/items/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(item["id"] == sample_item.id for item in data)


def test_read_item(client, sample_item):
    response = client.get(f"/items/{sample_item.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_item.id
    assert data["poe_id"] == sample_item.poe_id


def test_read_item_not_found(client):
    response = client.get("/items/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_create_price(client, sample_item):
    response = client.post(
        f"/items/{sample_item.id}/prices/",
        json={"price_type": "~price", "price": 50.0, "currency": "chaos"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 50.0
    assert data["currency"] == "chaos"
    assert data["price_type"] == "~price"
    assert data["item_id"] == sample_item.id


def test_create_price_unknown_item(client):
    response = client.post(
        "/items/9999/prices/",
        json={"price_type": "~price", "price": 50.0, "currency": "chaos"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_read_prices_for_item(client, sample_item, sample_price):
    response = client.get(f"/items/{sample_item.id}/prices/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(p["id"] == sample_price.id for p in data)
