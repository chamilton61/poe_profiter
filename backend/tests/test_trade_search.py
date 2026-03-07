from unittest.mock import AsyncMock, patch

import pytest

SEARCH_RESPONSE = {
    "id": "query123",
    "result": ["id1", "id2"],
    "total": 2,
}

LISTING_RESULT = [
    {
        "id": "id1",
        "listing": {
            "indexed": "2025-01-15T10:00:00Z",
            "account": {"name": "seller1"},
            "price": {"type": "~price", "amount": 10.0, "currency": "chaos"},
        },
        "item": {
            "name": "Mirror of Kalandra",
            "typeLine": "Mirror of Kalandra",
            "frameType": 5,
        },
    },
    {
        "id": "id2",
        "listing": {
            "indexed": "2025-01-15T11:00:00Z",
            "account": {"name": "seller2"},
            "price": {"type": "~price", "amount": 20.0, "currency": "chaos"},
        },
        "item": {
            "name": "",
            "typeLine": "Chaos Orb",
            "frameType": 5,
        },
    },
]


def mock_poe_trade(search_resp=None, fetch_resp=None):
    return patch.multiple(
        "app.main.poe_trade",
        search=AsyncMock(return_value=search_resp or SEARCH_RESPONSE),
        fetch=AsyncMock(return_value=fetch_resp or LISTING_RESULT),
    )


def test_trade_search_basic(client):
    with mock_poe_trade():
        response = client.post(
            "/trade/search",
            json={"league": "Standard", "name": "Mirror of Kalandra"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["returned"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["poe_id"] == "id1"
    assert data["items"][0]["seller_account"] == "seller1"
    assert data["items"][0]["category"] == "Currency"
    assert len(data["items"][0]["prices"]) == 1
    assert data["items"][0]["prices"][0]["price"] == 10.0


def test_trade_search_no_duplicates_on_second_call(client):
    with mock_poe_trade():
        client.post("/trade/search", json={"league": "Standard"})

    with mock_poe_trade():
        client.post("/trade/search", json={"league": "Standard"})

    with mock_poe_trade():
        response = client.get("/items/")
    data = response.json()
    poe_ids = [item["poe_id"] for item in data]
    assert len(poe_ids) == len(set(poe_ids)), "Duplicate poe_id rows found"


def test_trade_search_appends_price_on_repeat(client):
    with mock_poe_trade():
        client.post("/trade/search", json={"league": "Standard"})
    with mock_poe_trade():
        client.post("/trade/search", json={"league": "Standard"})

    response = client.get("/items/")
    items = response.json()
    item_id1 = next(i["id"] for i in items if i["poe_id"] == "id1")

    response = client.get(f"/items/{item_id1}/prices/")
    prices = response.json()
    assert len(prices) == 2


def test_trade_search_pagination(client):
    search_resp = {"id": "q1", "result": ["a", "b", "c", "d"], "total": 4}
    fetch_resp = [LISTING_RESULT[0]]

    with mock_poe_trade(search_resp=search_resp, fetch_resp=fetch_resp):
        response = client.post(
            "/trade/search",
            json={"league": "Standard", "page_size": 1, "page_offset": 2},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["page_size"] == 1
    assert data["page_offset"] == 2
    assert data["returned"] == 1


def test_trade_search_raw_query(client):
    raw = {"query": {"status": {"option": "any"}, "stats": []}, "sort": {"price": "asc"}}
    with mock_poe_trade():
        response = client.post(
            "/trade/search",
            json={"league": "Standard", "raw_query": raw},
        )
    assert response.status_code == 200


def test_trade_search_empty_result(client):
    with mock_poe_trade(
        search_resp={"id": "q1", "result": [], "total": 0},
        fetch_resp=[],
    ):
        response = client.post("/trade/search", json={"league": "Standard"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["returned"] == 0
    assert data["items"] == []


def test_trade_search_page_offset_beyond_results(client):
    with mock_poe_trade(
        search_resp={"id": "q1", "result": ["id1"], "total": 1},
        fetch_resp=[],
    ):
        response = client.post(
            "/trade/search",
            json={"league": "Standard", "page_offset": 10},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["returned"] == 0


def test_trade_search_name_is_empty_string_stored_as_none(client):
    with mock_poe_trade(fetch_resp=[LISTING_RESULT[1]]):
        response = client.post("/trade/search", json={"league": "Standard"})
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["name"] is None
