import React from 'react';
import { useChangePassword } from '../hooks/useChangePassword';

export default function ChangePasswordForm() {
  const {
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
  } = useChangePassword();

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    changePassword();
  };

  return (
    <div className="mypage-section">
      <h2 className="section-title">비밀번호 변경</h2>

      {errorMsg && <div className="error-message">{errorMsg}</div>}
      {successMsg && <div className="info-message">{successMsg}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="current-password">현재 비밀번호</label>
          <div className="input-wrapper">
            <input
              id="current-password"
              type="password"
              placeholder="현재 비밀번호를 입력하세요"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="new-password">새 비밀번호</label>
          <div className="input-wrapper">
            <input
              id="new-password"
              type="password"
              placeholder="새 비밀번호를 입력하세요"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="confirm-new-password">새 비밀번호 확인</label>
          <div className="input-wrapper">
            <input
              id="confirm-new-password"
              type="password"
              placeholder="새 비밀번호를 다시 입력하세요"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
        </div>

        <button type="submit" className="btn-primary" disabled={isLoading}>
          {isLoading ? '변경 중...' : '비밀번호 변경'}
        </button>
      </form>
    </div>
  );
}
