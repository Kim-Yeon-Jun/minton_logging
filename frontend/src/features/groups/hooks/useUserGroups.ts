import { useEffect, useState } from 'react';
import { getUserGroupsApi } from '../services/groupsApi';
import { Group } from '../types/group.types';

export function useUserGroups(userId: string) {
  const [groups, setGroups] = useState<Group[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string>('');

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setErrorMsg('');

    getUserGroupsApi(userId)
      .then((data) => {
        if (!cancelled) {
          setGroups(data);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setErrorMsg(err instanceof Error ? err.message : '그룹 목록을 불러오지 못했습니다.');
        }
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [userId]);

  return { groups, isLoading, errorMsg };
}
