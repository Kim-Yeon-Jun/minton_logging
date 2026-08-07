import { useGroupStats } from '../hooks/useGroupStats';

export interface GroupStatsProps {
  groupKey: string;
}

export default function GroupStats({ groupKey }: GroupStatsProps) {
  const { stats, isLoading, errorMsg } = useGroupStats(groupKey);

  if (isLoading) {
    return (
      <div className="mypage-section">
        <p className="subtitle">통계를 불러오는 중...</p>
      </div>
    );
  }

  if (errorMsg) {
    return (
      <div className="mypage-section">
        <div className="error-message">{errorMsg}</div>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  const { my_record, head_to_head, monthly_trend } = stats;
  const maxGames = Math.max(1, ...monthly_trend.map((m) => m.games));

  return (
    <>
      <div className="mypage-section">
        <h2 className="section-title">내 전적</h2>
        <div className="quick-stats">
          <div className="stat-card">
            <div className="stat-value">{my_record.win_rate}%</div>
            <div className="stat-label">승률</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">
              {my_record.wins}승 {my_record.losses}패
              {my_record.draws > 0 ? ` ${my_record.draws}무` : ''}
            </div>
            <div className="stat-label">전적</div>
          </div>
        </div>
      </div>

      <div className="mypage-section">
        <h2 className="section-title">상대 전적</h2>
        {head_to_head.length === 0 ? (
          <p className="subtitle">아직 함께한 경기가 없습니다.</p>
        ) : (
          <ul className="h2h-list">
            {head_to_head.map((h) => (
              <li key={h.opponent_id} className="h2h-item">
                <span className="h2h-name">{h.opponent_name}</span>
                <span className="h2h-record">
                  {h.wins}승 {h.losses}패
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="mypage-section">
        <h2 className="section-title">월별 추이</h2>
        {monthly_trend.length === 0 ? (
          <p className="subtitle">아직 경기 기록이 없습니다.</p>
        ) : (
          <>
            <div className="trend-chart" role="img" aria-label="월별 경기 수 및 승리 수 추이">
              {monthly_trend.map((m) => {
                const totalHeightPct = (m.games / maxGames) * 100;
                const winHeightPct = m.games > 0 ? (m.wins / m.games) * 100 : 0;

                return (
                  <div key={m.month} className="trend-bar-col">
                    <div className="trend-bar-value">
                      {m.wins}/{m.games}
                    </div>
                    <div className="trend-bar-outer">
                      <div className="trend-bar-total" style={{ height: `${totalHeightPct}%` }}>
                        <div className="trend-bar-win" style={{ height: `${winHeightPct}%` }} />
                      </div>
                    </div>
                    <div className="trend-bar-label">{m.month.slice(5)}월</div>
                  </div>
                );
              })}
            </div>
            <div className="trend-legend">
              <span className="trend-legend-item">
                <span className="trend-legend-dot trend-legend-dot-win" /> 승리
              </span>
              <span className="trend-legend-item">
                <span className="trend-legend-dot trend-legend-dot-total" /> 전체 경기
              </span>
            </div>
          </>
        )}
      </div>
    </>
  );
}
