from typing import List, Optional

import httpx

BASE_URL = "https://www.pathofexile.com/api/trade2"
USER_AGENT = "poe-profiter contact@example.com"


def _headers(poesessid: Optional[str]) -> dict:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }
    if poesessid:
        headers["Cookie"] = f"POESESSID={poesessid}"
    return headers


async def search(league: str, query_body: dict, poesessid: Optional[str] = None) -> dict:
    """POST /api/trade2/search/poe2/{league} — returns {id, result[], total}."""
    url = f"{BASE_URL}/search/poe2/{league}"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=query_body, headers=_headers(poesessid))
        response.raise_for_status()
        return response.json()


async def fetch(item_ids: List[str], query_id: str, poesessid: Optional[str] = None) -> List[dict]:
    """GET /api/trade2/fetch/{ids}?query={query_id} — returns list of full listing objects."""
    ids_param = ",".join(item_ids)
    url = f"{BASE_URL}/fetch/{ids_param}"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            params={"query": query_id},
            headers=_headers(poesessid),
        )
        response.raise_for_status()
        return response.json()["result"]
