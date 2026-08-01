import { useState } from 'react'

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const handleLogin = (e) => {
    e.preventDefault()
    if (username.trim()) {
      setIsLoggedIn(true)
    }
  }

  const handleLogout = () => {
    setIsLoggedIn(false)
    setPassword('')
  }

  return (
    <div className="app-container">
      {!isLoggedIn ? (
        /* Login Screen */
        <div className="login-screen">
          <div className="brand-badge">
            <span>🏸</span> Minton Logging
          </div>
          <h1 className="title">환영합니다! 👋</h1>
          <p className="subtitle">서비스 이용을 위해 로그인해 주세요.</p>

          <form onSubmit={handleLogin}>
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
                />
              </div>
            </div>

            <button type="submit" className="btn-primary">
              로그인하기
            </button>
          </form>
        </div>
      ) : (
        /* Welcome / Home Screen */
        <div className="welcome-screen">
          <div className="user-avatar">👤</div>
          <h1 className="title">{username}님, 환영합니다! 🎉</h1>
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

          <button onClick={handleLogout} className="btn-secondary">
            로그아웃
          </button>
        </div>
      )}
    </div>
  )
}

export default App
