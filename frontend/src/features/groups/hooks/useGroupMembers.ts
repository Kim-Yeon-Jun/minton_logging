import { useEffect, useState } from 'react';
import { getGroupDetailApi } from '../services/groupsApi';
import { GroupMember } from '../types/group.types';

export function useGroupMembers(groupKey: string) {
  const [members, setMembers] = useState<GroupMember[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string>('');

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setErrorMsg('');

    getGroupDetailApi(groupKey)
      .then((data) => {
        if (!cancelled) {
          setMembers(data.members);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setErrorMsg(err instanceof Error ? err.message : '그룹 멤버를 불러오지 못했습니다.');
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
  }, [groupKey]);

  return { members, isLoading, errorMsg };
}
