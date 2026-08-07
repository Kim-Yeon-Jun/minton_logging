import { useEffect, useState } from 'react';
import { getGroupStatsApi } from '../services/statsApi';
import { GroupStats } from '../types/stats.types';

export function useGroupStats(groupKey: string) {
  const [stats, setStats] = useState<GroupStats | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string>('');

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setErrorMsg('');

    getGroupStatsApi(groupKey)
      .then((data) => {
        if (!cancelled) setStats(data);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setErrorMsg(err instanceof Error ? err.message : '통계를 불러오지 못했습니다.');
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [groupKey]);

  return { stats, isLoading, errorMsg };
}
