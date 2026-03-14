export interface Material {
  name: string;
  price: string;
}

export interface Item {
  icon: string;
  name: string;
  rarity: 'unique' | 'rare' | 'magic' | 'normal';
  cost: string;
  roi: string;
  roiSign: number;
  stats: string[];
  whisper?: string;
  whisperToken?: string;
}

export interface TradeQuery {
  query: {
    status?: { option: 'online' | 'any' };
    name?: string;
    type?: string;
    stats?: Array<{
      type: 'and' | 'if' | 'not' | 'count' | 'weight';
      filters: Array<{ id: string; value?: { min?: number; max?: number } }>;
    }>;
    filters?: Record<string, { filters: Record<string, unknown> }>;
  };
  sort?: Record<string, string>;
}

export interface TradeSearchResult {
  id: string;
  result: string[];
  total: number;
}

export interface TradeFetchedEntry {
  id: string;
  listing: {
    indexed: string;
    whisper: string;
    whisper_token: string;
    account: {
      name: string;
      lastCharacterName: string;
      online?: { league: string };
    };
    price: {
      type: string;
      amount: number;
      currency: string;
    };
    stash?: { name: string; x: number; y: number };
  };
  item: {
    name: string;
    typeLine: string;
    baseType: string;
    rarity: string;
    ilvl?: number;
    icon: string;
    properties?: Array<{ name: string; values: [string, number][] }>;
    explicitMods?: string[];
    implicitMods?: string[];
  };
}

export interface Profile {
  id: string;
  name: string;
  description: string;
  maxProfitPrice: string;
  gamblingMethod: string;
  materials: Material[];
  notes: string;
  items: Item[];
  searchQuery?: TradeQuery;
}

export type Page = 'login' | 'overview' | 'details';
