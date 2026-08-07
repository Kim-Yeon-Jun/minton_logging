import { useState } from 'react';
import { changePasswordApi } from '../services/mypageApi';

export function useChangePassword() {
  const [currentPassword, setCurrentPassword] = useState<string>('');
  const [newPassword, setNewPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [successMsg, setSuccessMsg] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const changePassword = async () => {
    setErrorMsg('');
    setSuccessMsg('');

    if (!currentPassword || !newPassword) {
      setErrorMsg('현재 비밀번호와 새 비밀번호를 모두 입력해 주세요.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setErrorMsg('새 비밀번호가 일치하지 않습니다.');
      return;
    }

    setIsLoading(true);

    try {
      const data = await changePasswordApi(currentPassword, newPassword);
      setSuccessMsg(data.message);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg('비밀번호 변경 중 오류가 발생했습니다.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return {
    currentPassword,
    setCurrentPassword,
    newPassword,
    setNewPassword,
    confirmPassword,
    setConfirmPassword,
    errorMsg,
    successMsg,
    isLoading,
    changePassword,
  };
}
