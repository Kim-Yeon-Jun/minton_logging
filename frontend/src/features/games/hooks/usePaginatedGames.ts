import { useCallback, useEffect, useState } from 'react';
import { Game, GameListFilters, GameListResponse } from '../types/game.types';

const PAGE_SIZE = 10;

type Fetcher = (groupKey: string, limit: number, offset: number, filters?: GameListFilters) => Promise<GameListResponse>;

export function usePaginatedGames(
  fetcher: Fetcher,
  groupKey: string,
  errorFallback: string,
  filters: GameListFilters = {}
) {
  const { yearMonth, sort, myGamesOnly } = filters;

  const [games, setGames] = useState<Game[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isLoadingMore, setIsLoadingMore] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>('');

  const fetchFirstPage = useCallback(() => {
    setIsLoading(true);
    setErrorMsg('');

    fetcher(groupKey, PAGE_SIZE, 0, { yearMonth, sort, myGamesOnly })
      .then((data) => {
        setGames(data.items);
        setTotal(data.total);
      })
      .catch((err: unknown) => {
        setErrorMsg(err instanceof Error ? err.message : errorFallback);
      })
      .finally(() => setIsLoading(false));
  }, [fetcher, groupKey, errorFallback, yearMonth, sort, myGamesOnly]);

  useEffect(() => {
    fetchFirstPage();
  }, [fetchFirstPage]);

  const loadMore = async () => {
    setIsLoadingMore(true);
    try {
      const data = await fetcher(groupKey, PAGE_SIZE, games.length, { yearMonth, sort, myGamesOnly });
      setGames((prev) => [...prev, ...data.items]);
      setTotal(data.total);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : errorFallback);
    } finally {
      setIsLoadingMore(false);
    }
  };

  const updateGame = useCallback((gameId: string, patch: Partial<Game>) => {
    setGames((prev) => prev.map((g) => (g.game_id === gameId ? { ...g, ...patch } : g)));
  }, []);

  return {
    games,
    total,
    hasMore: games.length < total,
    isLoading,
    isLoadingMore,
    errorMsg,
    refetch: fetchFirstPage,
    loadMore,
    updateGame,
  };
}
