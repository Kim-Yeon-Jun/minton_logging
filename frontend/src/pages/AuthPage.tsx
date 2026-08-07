import { useEffect, useState } from 'react';
import { getMeApi, LoginForm, LoginResponse, RegisterForm, User } from '../features/auth';
import { clearToken, getToken, setToken } from '../lib/apiClient';
import HomePage from './HomePage';

type AuthMode = 'login' | 'register';

export default function AuthPage() {
  const [user, setUser] = useState<User | null>(null);
  const [authMode, setAuthMode] = useState<AuthMode>('login');
  const [successMsg, setSuccessMsg] = useState<string>('');
  const [isRestoringSession, setIsRestoringSession] = useState<boolean>(true);

  useEffect(() => {
    if (!getToken()) {
      setIsRestoringSession(false);
      return;
    }

    getMeApi()
      .then((me) => setUser(me))
      .catch(() => clearToken())
      .finally(() => setIsRestoringSession(false));
  }, []);

  const handleLoginSuccess = (result: LoginResponse) => {
    setToken(result.access_token);
    setUser(result);
    setSuccessMsg('');
  };

  const handleRegisterSuccess = () => {
    setAuthMode('login');
    setSuccessMsg('회원가입이 성공적으로 완료되었습니다! 로그인해 주세요.');
  };

  const handleLogout = () => {
    clearToken();
    setUser(null);
    setSuccessMsg('');
  };

  if (isRestoringSession) {
    return (
      <div className="app-container">
        <p className="subtitle">불러오는 중...</p>
      </div>
    );
  }

  return (
    <div className="app-container">
      {successMsg && (
        <div className="info-message">
          {successMsg}
        </div>
      )}

      {!user ? (
        authMode === 'login' ? (
          <LoginForm
            onLoginSuccess={handleLoginSuccess}
            onSwitchToRegister={() => {
              setSuccessMsg('');
              setAuthMode('register');
            }}
          />
        ) : (
          <RegisterForm
            onRegisterSuccess={handleRegisterSuccess}
            onSwitchToLogin={() => {
              setSuccessMsg('');
              setAuthMode('login');
            }}
          />
        )
      ) : (
        <HomePage user={user} onLogout={handleLogout} />
      )}
    </div>
  );
}
