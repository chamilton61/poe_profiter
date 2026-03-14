import { useState, useEffect } from 'react';
import type { Item, Profile } from '../types';
import { searchTrade, fetchItems, mapToItem } from '../services/tradeApi';

export interface ProfileItemsState {
  items: Item[];
  loading: boolean;
  error: string | null;
}

export function useProfileItems(
  profile: Profile,
  league: string,
  poesessid: string | null,
): ProfileItemsState {
  const [state, setState] = useState<ProfileItemsState>({
    items: profile.items,
    loading: false,
    error: null,
  });

  useEffect(() => {
    if (!poesessid || !profile.searchQuery) return;

    setState((s) => ({ ...s, loading: true, error: null }));
    let cancelled = false;

    async function run() {
      try {
        const searchResult = await searchTrade(league, profile.searchQuery!, poesessid!);
        if (cancelled) return;
        if (searchResult.result.length === 0) {
          setState({ items: [], loading: false, error: null });
          return;
        }
        const entries = await fetchItems(
          searchResult.id,
          searchResult.result.slice(0, 10),
          poesessid!,
        );
        if (cancelled) return;
        setState({ items: entries.map(mapToItem), loading: false, error: null });
      } catch (err) {
        if (cancelled) return;
        setState((s) => ({
          ...s,
          loading: false,
          error: err instanceof Error ? err.message : 'Failed to fetch items',
        }));
      }
    }

    run();
    return () => {
      cancelled = true;
    };
  }, [profile.id, league, poesessid]);

  return state;
}
