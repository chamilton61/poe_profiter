# PoE2 Trade API Reference

Base URL: `https://www.pathofexile.com/api/trade2`

GGG does not formally document this API. This doc was assembled from community tools and browser network inspection (Dec 2024 / early 2025).

---

## Authentication

The API uses a session cookie for authentication:

```
Cookie: POESESSID=<your_session_id>
```

### How to get your POESESSID

1. Go to https://www.pathofexile.com and log in
2. Open DevTools (`F12`) → **Application** tab → **Cookies** → `https://www.pathofexile.com`
3. Copy the value of the `POESESSID` cookie

**Security notes:**
- Treat it like a password — anyone with it can act as you on the site
- It is invalidated when you log out
- For the app, store it as an env var (e.g. `POESESSID=...` in `.env`)

---

## Required Headers

```
Cookie: POESESSID=<session_id>
Content-Type: application/json
User-Agent: <your_app_name contact@email.com>   ← GGG requests this for all API consumers
```

---

## Rate Limiting

- Dynamic, policy-based — limits can change at any time
- Rate limit state is returned in **response headers** — parse and respect them
- Implements a token bucket model
- If search `total > 10,000` results, tighten your filters and retry rather than paginating through all results

---

## Data Endpoints (GET, no auth required)

These return static reference data used to build queries. **None of these endpoints accept query parameters.**

---

### `GET /api/trade2/data/leagues`

Returns the list of available PoE2 leagues.

**Response:**
```json
{
  "result": [
    { "id": "Standard", "realm": "poe2", "text": "Standard" },
    { "id": "Hardcore", "realm": "poe2", "text": "Hardcore" }
  ]
}
```

| Field | Description |
|---|---|
| `id` | League identifier — used as `{league}` in the search endpoint URL |
| `realm` | Always `"poe2"` for PoE2 leagues |
| `text` | Human-readable display name |

---

### `GET /api/trade2/data/items`

Returns all searchable item names and base types, grouped by category. Used to populate `name` and `type` fields in the search query.

**Response:**
```json
{
  "result": [
    {
      "label": "Accessories",
      "entries": [
        {
          "name": "Ahkeli's Meadow",
          "type": "Ruby Ring",
          "text": "Ahkeli's Meadow Ruby Ring",
          "flags": { "unique": true }
        },
        {
          "type": "Ruby Ring",
          "text": "Ruby Ring"
        }
      ]
    },
    {
      "label": "Armour",
      "entries": [...]
    }
  ]
}
```

| Field | Description |
|---|---|
| `label` | Category name (e.g. `"Accessories"`, `"Armour"`, `"Weapons"`, `"Flasks"`) |
| `entries[].name` | Unique item name — only present for named uniques |
| `entries[].type` | Base type (e.g. `"Ruby Ring"`) |
| `entries[].text` | Combined display string |
| `entries[].flags.unique` | `true` if the item is a unique |

Use `name` alone to search for a specific unique, `type` alone to search all items of a base type, or both together.

---

### `GET /api/trade2/data/stats`

Returns all stat filter IDs used to filter by item modifiers. The `id` values from this endpoint are what you put in `query.stats[].filters[].id` in the search body.

**Response:**
```json
{
  "result": [
    {
      "label": "Pseudo",
      "entries": [
        {
          "id": "pseudo.pseudo_total_cold_resistance",
          "text": "+#% total to Cold Resistance",
          "type": "pseudo"
        }
      ]
    },
    {
      "label": "Explicit",
      "entries": [
        {
          "id": "explicit.stat_3299347043",
          "text": "+# to maximum Life",
          "type": "explicit"
        }
      ]
    },
    {
      "label": "Implicit",
      "entries": [...]
    },
    {
      "label": "Fractured",
      "entries": [...]
    },
    {
      "label": "Enchant",
      "entries": [...]
    }
  ]
}
```

| Field | Description |
|---|---|
| `label` | Stat category (e.g. `"Pseudo"`, `"Explicit"`, `"Implicit"`, `"Enchant"`, `"Fractured"`) |
| `entries[].id` | Stat identifier — used directly in search filter `id` field |
| `entries[].text` | Human-readable description; `#` is a placeholder for numeric values |
| `entries[].type` | Matches the category in lowercase (e.g. `"explicit"`, `"pseudo"`) |

**Stat types for search queries:**
- `"and"` — item must have all listed stats
- `"if"` — conditional (used for pseudo stats)
- `"not"` — item must NOT have the stat
- `"count"` — item must have at least N of the listed stats
- `"weight"` — weighted sum across stats

---

### `GET /api/trade2/data/static`

Returns static reference data for currencies and other exchangeable items. Primarily used for the bulk exchange feature and for resolving price `option` values.

**Response:**
```json
{
  "result": [
    {
      "id": "Currency",
      "label": "Currency",
      "entries": [
        {
          "id": "chaos",
          "text": "Chaos Orb",
          "image": "/image/Art/2DItems/Currency/CurrencyRerollRare.png?v=..."
        },
        {
          "id": "alt",
          "text": "Orb of Alteration",
          "image": "/image/Art/2DItems/Currency/CurrencyRerollMagic.png?v=..."
        }
      ]
    },
    {
      "id": "Fragments",
      "label": "Fragments",
      "entries": [...]
    }
  ]
}
```

| Field | Description |
|---|---|
| `label` | Category name (e.g. `"Currency"`, `"Fragments"`, `"Essences"`) |
| `entries[].id` | Short identifier — used as the `option` value in price filters |
| `entries[].text` | Full display name |
| `entries[].image` | Relative path to the item's icon on pathofexile.com |

---

## Search Endpoint

```
POST /api/trade2/search/{realm}/{league}
```

**Example:** `POST /api/trade2/search/poe2/Standard`

### Request body

```json
{
  "query": {
    "status": { "option": "online" },
    "name": "Tabula Rasa",
    "type": "Simple Robe",
    "stats": [
      {
        "type": "and",
        "filters": [
          { "id": "explicit.stat_123456", "value": { "min": 5 } }
        ]
      }
    ],
    "filters": {
      "trade_filters": {
        "filters": {
          "price": { "min": 1, "max": 10, "option": "chaos" }
        }
      }
    }
  },
  "sort": { "price": "asc" }
}
```

**Notes:**
- Max **35 filters** per query (slots are reserved for type/rarity, mirrored exclusion, price limits, level requirements)
- `name` and `type` are optional — omit to search broadly
- `status.option`: `"online"` | `"any"`
- Stat filter IDs (e.g. `explicit.stat_123456`) come from `/api/trade2/data/stats`

### Response

```json
{
  "id": "AbCdEf123456",
  "result": ["itemId1", "itemId2", "itemId3", "..."],
  "total": 1234
}
```

- `id` — query ID, required for the fetch step
- `result` — list of item IDs (can be large)
- `total` — total matches

---

## Fetch Endpoint

```
GET /api/trade2/fetch/{ids}?query={queryId}
```

- `{ids}` — comma-separated item IDs from the search `result` array
- `?query=` — the `id` returned from the search response
- **Fetch at most 10 IDs per request**

**Example:**
```
GET /api/trade2/fetch/itemId1,itemId2,itemId3?query=AbCdEf123456
```

### Response

Returns full item data for each requested ID, including listing price, seller account, item properties, mods, etc.

---

## Typical Flow

```
1. GET  /api/trade2/data/stats        → get stat filter IDs
2. POST /api/trade2/search/poe2/{league}  → submit query, get { id, result[], total }
3. GET  /api/trade2/fetch/{ids[0..9]}?query={id}  → get full item data
   (repeat step 3 in batches of 10, respecting rate limits)
```

---

## Sources

- [DeepWiki - Path of Building PoE2 Trade System](https://deepwiki.com/PathOfBuildingCommunity/PathOfBuilding-PoE2/5.1-trade-system)
- [PoE Developer Docs](https://www.pathofexile.com/developer/docs)
- [gamepressure.com - How to Find PoE Session ID](https://www.gamepressure.com/newsroom/how-to-find-poe-session-id/z74e59)
- [Chuanhsing/poe-api OpenAPI spec](https://github.com/Chuanhsing/poe-api/blob/master/poe.yaml) (covers trade v1; trade2 mirrors same patterns)
