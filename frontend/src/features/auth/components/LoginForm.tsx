import React from 'react';
import { useLogin } from '../hooks/useLogin';
import { LoginResponse } from '../types/auth.types';

export interface LoginFormProps {
  onLoginSuccess: (result: LoginResponse) => void;
  onSwitchToRegister: () => void;
}

export default function LoginForm({ onLoginSuccess, onSwitchToRegister }: LoginFormProps) {
  const {
    username,
    setUsername,
    password,
    setPassword,
    errorMsg,
    isLoading,
    login,
  } = useLogin(onLoginSuccess);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    login();
  };

  return (
    <div className="login-screen">
      <div className="brand-badge">
        <span>🏸</span> Minton Logging
      </div>
      <h1 className="title">환영합니다! 👋</h1>
      <p className="subtitle">서비스 이용을 위해 로그인해 주세요.</p>

      {errorMsg && <div className="error-message">{errorMsg}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">아이디 / 사용자 이름</label>
          <div className="input-wrapper">
            <input
              id="username"
              type="text"
              placeholder="아이디를 입력하세요"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="password">비밀번호</label>
          <div className="input-wrapper">
            <input
              id="password"
              type="password"
              placeholder="비밀번호를 입력하세요"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
        </div>

        <button type="submit" className="btn-primary" disabled={isLoading}>
          {isLoading ? '로그인 중...' : '로그인하기'}
        </button>
      </form>

      <div className="auth-switch">
        <span>계정이 없으신가요?</span>
        <button type="button" onClick={onSwitchToRegister} className="btn-link">
          회원가입
        </button>
      </div>
    </div>
  );
}
