import { useState } from 'react';
import { joinGroupApi } from '../services/groupsApi';

export function useJoinGroup(onJoined?: () => void) {
  const [groupKey, setGroupKey] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [successMsg, setSuccessMsg] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const joinGroup = async () => {
    setErrorMsg('');
    setSuccessMsg('');

    if (!groupKey.trim()) {
      setErrorMsg('그룹 코드를 입력해 주세요.');
      return;
    }

    setIsLoading(true);

    try {
      const data = await joinGroupApi(groupKey.trim());
      setSuccessMsg(data.message);
      setGroupKey('');
      onJoined?.();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg('그룹 참여 중 오류가 발생했습니다.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return {
    groupKey,
    setGroupKey,
    errorMsg,
    successMsg,
    isLoading,
    joinGroup,
  };
}
