export type TopBarView = 'home' | 'mypage' | 'group';

export interface TopBarProps {
  activeView: TopBarView;
  onNavigate: (view: TopBarView) => void;
  onLogout: () => void;
}

export default function TopBar({ activeView, onNavigate, onLogout }: TopBarProps) {
  const isHome = activeView === 'home';

  return (
    <div className="top-bar">
      <div className="brand-badge">
        <span>🏸</span> Minton Logging
      </div>

      <div className="top-bar-actions">
        <button
          type="button"
          className="icon-button"
          onClick={() => onNavigate(isHome ? 'mypage' : 'home')}
          aria-label={isHome ? '마이페이지' : '홈으로'}
          title={isHome ? '마이페이지' : '홈으로'}
        >
          {isHome ? '👤' : '🏠'}
        </button>
        <button type="button" className="btn-logout" onClick={onLogout}>
          로그아웃
        </button>
      </div>
    </div>
  );
}
