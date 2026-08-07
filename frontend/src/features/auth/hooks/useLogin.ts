import { useState } from 'react';
import { loginApi } from '../services/authApi';
import { LoginResponse } from '../types/auth.types';

export function useLogin(onSuccess: (result: LoginResponse) => void) {
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const login = async () => {
    setErrorMsg('');

    if (!username.trim() || !password.trim()) {
      setErrorMsg('아이디와 비밀번호를 모두 입력해주세요.');
      return;
    }

    setIsLoading(true);

    try {
      const data = await loginApi(username.trim(), password);
      onSuccess(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg('로그인 중 오류가 발생했습니다.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return {
    username,
    setUsername,
    password,
    setPassword,
    errorMsg,
    setErrorMsg,
    isLoading,
    login,
  };
}
