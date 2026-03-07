from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import get_db, engine, Base
from app.models import item as models
from app.schemas import item as schemas
from app.repositories.item import ItemRepository, PriceRepository


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
