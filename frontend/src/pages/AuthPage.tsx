import { useState } from 'react';
import { LoginForm, RegisterForm, User } from '../features/auth';
import { WelcomeScreen } from '../features/dashboard';

type AuthMode = 'login' | 'register';

export default function AuthPage() {
  const [user, setUser] = useState<User | null>(null);
  const [authMode, setAuthMode] = useState<AuthMode>('login');
  const [successMsg, setSuccessMsg] = useState<string>('');

  const handleLoginSuccess = (userData: User) => {
    setUser(userData);
    setSuccessMsg('');
  };

  const handleRegisterSuccess = () => {
    setAuthMode('login');
    setSuccessMsg('회원가입이 성공적으로 완료되었습니다! 로그인해 주세요.');
  };

  const handleLogout = () => {
    setUser(null);
    setSuccessMsg('');
  };

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
        <WelcomeScreen user={user} onLogout={handleLogout} />
      )}
    </div>
  );
}
