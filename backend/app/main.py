from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager
from datetime import datetime

import httpx

from app.core.config import settings
from app.core.database import get_db, engine, Base
from app.schemas import item as schemas
from app.repositories.item import ItemRepository, PriceRepository
from app.services import poe_trade

FRAME_TYPE_CATEGORY = {
    0: "Normal",
    1: "Magic",
    2: "Rare",
    3: "Unique",
    4: "Gem",
    5: "Currency",
    6: "Divination Card",
    9: "Relic",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: cleanup if needed


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/")
def read_root():
    """Hello World endpoint."""
    return {"message": "Hello World from POE Profiter!"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Item endpoints
@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """Create a new item."""
    repo = ItemRepository(db)
    return repo.create(item.model_dump())


@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all items."""
    repo = ItemRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    """Get a single item by ID."""
    repo = ItemRepository(db)
    item = repo.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item



# Price endpoints
@app.post("/items/{item_id}/prices/", response_model=schemas.Price)
def create_price(item_id: int, price: schemas.PriceCreate, db: Session = Depends(get_db)):
    """Create a new price for an item."""
    item_repo = ItemRepository(db)
    if not item_repo.get(item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    
    price_repo = PriceRepository(db)
    price_data = price.model_dump()
    price_data["item_id"] = item_id
    return price_repo.create(price_data)


@app.get("/items/{item_id}/prices/", response_model=List[schemas.Price])
def read_prices_for_item(item_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all prices for a specific item."""
    item_repo = ItemRepository(db)
    if not item_repo.get(item_id):
        raise HTTPException(status_code=404, detail="Item not found")

    price_repo = PriceRepository(db)
    return price_repo.get_by_item_id(item_id, skip=skip, limit=limit)


# Trade search endpoint
@app.post("/trade/search", response_model=schemas.TradeSearchResponse)
async def trade_search(req: schemas.TradeSearchRequest, db: Session = Depends(get_db)):
    """Search the PoE2 trade API and persist results as trade history."""
    if req.raw_query is not None:
        query_body = req.raw_query
    else:
        query_body = {
            "query": {
                "status": {"option": req.status},
                "stats": [{"type": "and", "filters": []}],
                "filters": {},
            },
            "sort": {"price": "asc"},
        }
        if req.name:
            query_body["query"]["name"] = req.name
        if req.type:
            query_body["query"]["type"] = req.type

        price_filter: dict = {}
        if req.min_price is not None:
            price_filter["min"] = req.min_price
        if req.max_price is not None:
            price_filter["max"] = req.max_price
        if req.currency:
            price_filter["option"] = req.currency
        if price_filter:
            query_body["query"]["filters"]["trade_filters"] = {
                "filters": {"price": price_filter}
            }

    try:
        search_result = await poe_trade.search(req.league, query_body, req.poesessid)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"PoE trade search failed: {e.response.status_code}")

    all_ids: List[str] = search_result.get("result", [])
    total: int = search_result.get("total", 0)
    query_id: str = search_result["id"]

    page_size = max(1, min(req.page_size, 10))
    ids_to_fetch = all_ids[req.page_offset: req.page_offset + page_size]

    if not ids_to_fetch:
        return schemas.TradeSearchResponse(
            total=total,
            page_size=page_size,
            page_offset=req.page_offset,
            returned=0,
            items=[],
        )

    try:
        listings = await poe_trade.fetch(ids_to_fetch, query_id, req.poesessid)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"PoE trade fetch failed: {e.response.status_code}")

    item_repo = ItemRepository(db)
    price_repo = PriceRepository(db)
    result_items = []

    for listing_result in listings:
        poe_id: str = listing_result["id"]
        listing = listing_result["listing"]
        raw_item = listing_result["item"]

        snapshot = {k: v for k, v in raw_item.items() if k != "extended"}
        category = FRAME_TYPE_CATEGORY.get(raw_item.get("frameType", 0), "Normal")

        item = item_repo.get_by_poe_id(poe_id)
        if item is None:
            item = item_repo.create({
                "poe_id": poe_id,
                "name": raw_item.get("name") or None,
                "base_type": raw_item.get("typeLine", ""),
                "category": category,
                "seller_account": listing["account"]["name"],
                "indexed_at": datetime.fromisoformat(listing["indexed"].replace("Z", "+00:00")),
                "item_snapshot": snapshot,
            })

        price_data = listing["price"]
        price_repo.create({
            "item_id": item.id,
            "price_type": price_data.get("type", "~price"),
            "price": price_data["amount"],
            "currency": price_data["currency"],
        })

        db.refresh(item)
        result_items.append(item)

    return schemas.TradeSearchResponse(
        total=total,
        page_size=page_size,
        page_offset=req.page_offset,
        returned=len(result_items),
        items=[schemas.Item.model_validate(i) for i in result_items],
    )
