import React from 'react';
import { useRegister } from '../hooks/useRegister';

export interface RegisterFormProps {
  onRegisterSuccess: () => void;
  onSwitchToLogin: () => void;
}

export default function RegisterForm({ onRegisterSuccess, onSwitchToLogin }: RegisterFormProps) {
  const {
    username,
    setUsername,
    password,
    setPassword,
    confirmPassword,
    setConfirmPassword,
    name,
    setName,
    errorMsg,
    isLoading,
    register,
  } = useRegister(onRegisterSuccess);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    register();
  };

  return (
    <div className="register-screen">
      <div className="brand-badge">
        <span>🏸</span> Minton Logging
      </div>
      <h1 className="title">회원가입 📝</h1>
      <p className="subtitle">Minton Logging과 함께 새로운 민턴 라이프를 시작해보세요!</p>

      {errorMsg && <div className="error-message">{errorMsg}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="reg-username">아이디 *</label>
          <div className="input-wrapper">
            <input
              id="reg-username"
              type="text"
              placeholder="사용할 아이디를 입력하세요"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="reg-name">이름 (선택)</label>
          <div className="input-wrapper">
            <input
              id="reg-name"
              type="text"
              placeholder="이름 또는 닉네임"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={isLoading}
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="reg-password">비밀번호 *</label>
          <div className="input-wrapper">
            <input
              id="reg-password"
              type="password"
              placeholder="비밀번호를 입력하세요"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="reg-confirm-password">비밀번호 확인 *</label>
          <div className="input-wrapper">
            <input
              id="reg-confirm-password"
              type="password"
              placeholder="비밀번호를 다시 입력하세요"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
        </div>

        <button type="submit" className="btn-primary" disabled={isLoading}>
          {isLoading ? '가입 진행 중...' : '회원가입하기'}
        </button>
      </form>

      <div className="auth-switch">
        <span>이미 계정이 있으신가요?</span>
        <button type="button" onClick={onSwitchToLogin} className="btn-link">
          로그인
        </button>
      </div>
    </div>
  );
}
