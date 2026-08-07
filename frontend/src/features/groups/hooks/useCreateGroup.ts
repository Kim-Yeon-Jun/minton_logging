import { useState } from 'react';
import { createGroupApi } from '../services/groupsApi';

export function useCreateGroup(onCreated?: () => void) {
  const [groupName, setGroupName] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [successMsg, setSuccessMsg] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const createGroup = async () => {
    setErrorMsg('');
    setSuccessMsg('');

    if (!groupName.trim()) {
      setErrorMsg('그룹 이름을 입력해 주세요.');
      return;
    }

    setIsLoading(true);

    try {
      const data = await createGroupApi(groupName.trim(), description.trim() || null);
      setSuccessMsg(`'${data.group_name}' 그룹이 생성되었습니다.`);
      setGroupName('');
      setDescription('');
      onCreated?.();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg('그룹 생성 중 오류가 발생했습니다.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return {
    groupName,
    setGroupName,
    description,
    setDescription,
    errorMsg,
    successMsg,
    isLoading,
    createGroup,
  };
}
