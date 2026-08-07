import { useCallback, useEffect, useState } from 'react';
import { Game, GameListResponse } from '../types/game.types';

const PAGE_SIZE = 10;

type Fetcher = (groupKey: string, limit: number, offset: number) => Promise<GameListResponse>;

export function usePaginatedGames(fetcher: Fetcher, groupKey: string, errorFallback: string) {
  const [games, setGames] = useState<Game[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isLoadingMore, setIsLoadingMore] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string>('');

  const fetchFirstPage = useCallback(() => {
    setIsLoading(true);
    setErrorMsg('');

    fetcher(groupKey, PAGE_SIZE, 0)
      .then((data) => {
        setGames(data.items);
        setTotal(data.total);
      })
      .catch((err: unknown) => {
        setErrorMsg(err instanceof Error ? err.message : errorFallback);
      })
      .finally(() => setIsLoading(false));
  }, [fetcher, groupKey, errorFallback]);

  useEffect(() => {
    fetchFirstPage();
  }, [fetchFirstPage]);

  const loadMore = async () => {
    setIsLoadingMore(true);
    try {
      const data = await fetcher(groupKey, PAGE_SIZE, games.length);
      setGames((prev) => [...prev, ...data.items]);
      setTotal(data.total);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : errorFallback);
    } finally {
      setIsLoadingMore(false);
    }
  };

  return {
    games,
    total,
    hasMore: games.length < total,
    isLoading,
    isLoadingMore,
    errorMsg,
    refetch: fetchFirstPage,
    loadMore,
  };
}
