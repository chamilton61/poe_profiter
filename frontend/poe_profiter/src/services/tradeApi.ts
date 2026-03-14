import type { Item, TradeQuery, TradeSearchResult, TradeFetchedEntry } from '../types';

const BASE_URL = '/api/trade2';

function buildHeaders(sessid: string): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'X-Poesessid': sessid,
  };
}

export async function searchTrade(
  league: string,
  query: TradeQuery,
  sessid: string,
): Promise<TradeSearchResult> {
  const res = await fetch(
    `${BASE_URL}/search/poe2/${encodeURIComponent(league)}`,
    {
      method: 'POST',
      headers: buildHeaders(sessid),
      body: JSON.stringify(query),
    },
  );
  if (!res.ok) throw new Error(`Search failed: ${res.status} ${res.statusText}`);
  return res.json() as Promise<TradeSearchResult>;
}

export async function fetchItems(
  queryId: string,
  itemIds: string[],
  sessid: string,
): Promise<TradeFetchedEntry[]> {
  const ids = itemIds.slice(0, 10).join(',');
  const res = await fetch(`${BASE_URL}/fetch/${ids}?query=${queryId}`, {
    headers: buildHeaders(sessid),
  });
  if (!res.ok) throw new Error(`Fetch failed: ${res.status} ${res.statusText}`);
  const data = (await res.json()) as { result: TradeFetchedEntry[] };
  return data.result;
}

function mapRarity(r: string): Item['rarity'] {
  switch (r.toLowerCase()) {
    case 'unique':
      return 'unique';
    case 'rare':
      return 'rare';
    case 'magic':
      return 'magic';
    default:
      return 'normal';
  }
}

export function mapToItem(entry: TradeFetchedEntry): Item {
  const { listing, item } = entry;
  const name = item.name ? `${item.name} ${item.typeLine}`.trim() : item.typeLine;
  const stats: string[] = [];
  if (item.ilvl) stats.push(`ilvl: ${item.ilvl}`);
  if (item.explicitMods) stats.push(...item.explicitMods.slice(0, 3));

  return {
    icon: item.icon,
    name,
    rarity: mapRarity(item.rarity),
    cost: `${listing.price.amount} ${listing.price.currency}`,
    roi: '—',
    roiSign: 0,
    stats,
    whisper: listing.whisper,
    whisperToken: listing.whisper_token,
  };
}
