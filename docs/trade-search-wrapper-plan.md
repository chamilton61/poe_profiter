# Plan: Trade Search Wrapper Endpoint with History

## Context

We want a new endpoint that wraps the PoE2 trade API search+fetch flow and persists the results as trade history. The existing `Item` model is rewritten to represent a specific trade listing (one row per listed item), with all item properties stored directly on it. The existing `Price` model is kept as a one-to-many child — each time we observe a listing's price, we add a row. This lets us track price changes for the same listing over time.

---

## Requirements Summary

- **Input**: Simplified params (league, name, type, price range, status) + optional `raw_query` override
- **Pagination**: `page_size` (1–10, capped by fetch limit) and `page_offset` to select which IDs from the search result to fetch
- **Item**: Rewritten — one row per trade listing, keyed by `poe_id` (trade API item `id`)
- **Price**: Kept — a new Price row is added every time we observe the listing's price
- **Saved per listing**: `poe_id`, `listing.indexed`, `listing.account.name`, all item fields except `extended`; price (`listing.price.*`) saved to Price table
- **Tokens**: Not saved
- **Auth**: `POESESSID` stored in env/config, sent as cookie on all trade API requests

---

## Model Changes

### `app/models/item.py` — Rewrite `Item`, update `Price`

**Rewritten `Item`:**
```
Item
  id             Integer   PK autoincrement
  poe_id         String    unique, indexed  ← trade API item id
  name           String    nullable         ← item.name (only present on uniques)
  base_type      String                     ← item.typeLine
  category       String                     ← derived from item.frameType (see mapping below)
  seller_account String                     ← listing.account.name
  indexed_at     DateTime                   ← listing.indexed
  item_snapshot  JSON                       ← full item object minus "extended" key
  created_at     DateTime  server_default=now()
  updated_at     DateTime  onupdate=now()
  prices         → Price[] (one-to-many, cascade delete)
```

**Updated `Price`** (add `price_type`):
```
Price
  id           Integer   PK autoincrement
  item_id      Integer   FK → items.id
  price_type   String    ← listing.price.type  (NEW)
  price        Float     ← listing.price.amount
  currency     String    ← listing.price.currency
  recorded_at  DateTime  server_default=now()
```

**`frameType` → `category` mapping:**
```
0 → "Normal", 1 → "Magic", 2 → "Rare", 3 → "Unique",
4 → "Gem", 5 → "Currency", 6 → "Divination Card", 9 → "Relic"
```

---

## Schema Changes

### `app/schemas/item.py`

**Update `PriceBase`**: add `price_type: str` field.

**Rewrite `ItemBase`**: replace existing fields with:
```
poe_id:         str
name:           Optional[str]
base_type:      str
category:       str
seller_account: str
indexed_at:     datetime
item_snapshot:  dict
```

**Add `TradeSearchRequest`** (new input schema):
```
league:      str
name:        Optional[str]
type:        Optional[str]
min_price:   Optional[float]
max_price:   Optional[float]
currency:    Optional[str]
status:      str = "online"   # "online" | "any"
page_size:   int = 10         # 1–10
page_offset: int = 0
raw_query:   Optional[dict]   # if provided, overrides all query fields above
```

**Add `TradeSearchResponse`**:
```
total:       int    ← from PoE2 search response
page_size:   int
page_offset: int
returned:    int    ← actual count fetched
items:       List[Item]
```

---

## Repository Changes

### `app/repositories/item.py`

**`ItemRepository`**: replace `get_by_name` with `get_by_poe_id(poe_id: str)`.

**`PriceRepository`**: no changes needed (inherits `create`, `get_by_item_id` from base).

---

## New Service

### `app/services/poe_trade.py` (new file)

Async HTTP client (`httpx`) for the PoE2 trade API. Reads `POESESSID` from `settings`. Sends cookie + `User-Agent` header on every request.

```python
async def search(league: str, query_body: dict) -> dict:
    # POST /api/trade2/search/poe2/{league}
    # returns { "id": str, "result": List[str], "total": int }

async def fetch(item_ids: List[str], query_id: str) -> List[dict]:
    # GET /api/trade2/fetch/{ids}?query={query_id}
    # returns list of full listing objects
```

---

## Config Change

### `app/core/config.py`

Add `poesessid: str = ""` to `Settings`.

### `.env.example`

Add `POESESSID=` entry.

---

## New Route

### `app/main.py`

```
POST /trade/search
  body:     TradeSearchRequest
  response: TradeSearchResponse
```

**Route logic:**
1. Build trade API query body from `TradeSearchRequest` fields — or use `raw_query` directly if provided
2. `await poe_trade.search(req.league, query_body)` → `{id, result[], total}`
3. `ids = result[page_offset : page_offset + page_size]`
4. `await poe_trade.fetch(ids, query_id)` → list of full listing objects
5. For each listing result:
   a. Extract `poe_id = result["id"]`, item fields from `result["item"]`, listing fields from `result["listing"]`
   b. `item = ItemRepository.get_by_poe_id(poe_id)` — if None, create Item row
   c. Strip `"extended"` key from item snapshot before storing
   d. Add a new Price row: `{ price_type, price=amount, currency, item_id }`
6. Return `TradeSearchResponse`

---

## Files Touched

| File | Action |
|---|---|
| `app/models/item.py` | Rewrite `Item`, add `price_type` to `Price` |
| `app/schemas/item.py` | Rewrite `ItemBase`, update `PriceBase`, add `TradeSearchRequest` + `TradeSearchResponse` |
| `app/repositories/item.py` | Replace `get_by_name` → `get_by_poe_id` on `ItemRepository` |
| `app/core/config.py` | Add `poesessid` setting |
| `app/main.py` | Add `POST /trade/search` route |
| `app/services/poe_trade.py` | New file — async PoE2 API HTTP client |
| `.env.example` | Add `POESESSID=` |

---

## Verification

1. Add `POESESSID=<your_session>` to `.env`
2. `docker-compose up --build`
3. `POST /trade/search` with `{"league": "Standard", "name": "Tabula Rasa", "page_size": 5, "page_offset": 0}`
4. Confirm response has 5 items with price, seller, and item snapshot
5. Re-run — confirm same `Item` rows exist (no duplicates by `poe_id`) but new `Price` rows added
6. Repeat with `page_offset: 5` — confirm different items returned
7. `POST /trade/search` with `{"league": "Standard", "raw_query": {...}, "page_size": 3, "page_offset": 0}` — confirm raw query path works
8. `uv run pytest tests/ -v` — note: existing tests will need updating due to Item model rewrite
