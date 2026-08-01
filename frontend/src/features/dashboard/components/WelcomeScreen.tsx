import { User } from '../features/auth';

export interface WelcomeScreenProps {
  user: User;
  onLogout: () => void;
}

export default function WelcomeScreen({ user, onLogout }: WelcomeScreenProps) {
  return (
    <div className="welcome-screen">
      <div className="user-avatar">👤</div>
      <h1 className="title">
        {user.name ? `${user.name}(${user.username})` : user.username}님, 환영합니다! 🎉
      </h1>
      <p className="subtitle">
        Minton Logging 앱에 성공적으로 로그인하셨습니다.<br />
        오늘도 즐거운 민턴 라이프 되세요!
      </p>

      <div className="quick-stats">
        <div className="stat-card">
          <div className="stat-value">12회</div>
          <div className="stat-label">이번 달 경기 수</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">85%</div>
          <div className="stat-label">승률</div>
        </div>
      </div>

      <button onClick={onLogout} className="btn-secondary">
        로그아웃
      </button>
    </div>
  );
}
