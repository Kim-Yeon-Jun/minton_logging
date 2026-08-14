import { useState } from 'react';
import { MonthPicker } from '../../../components';
import { currentYearMonth } from '../../../utils/date';
import { useGroupStats } from '../hooks/useGroupStats';

export interface GroupStatsProps {
  groupKey: string;
}

function formatScoreDiff(diff: number): string {
  return diff > 0 ? `+${diff}` : String(diff);
}

export default function GroupStats({ groupKey }: GroupStatsProps) {
  const [yearMonth, setYearMonth] = useState<string>(currentYearMonth());
  const { stats, isLoading, errorMsg } = useGroupStats(groupKey, yearMonth);

  if (isLoading && !stats) {
    return (
      <div className="mypage-section">
        <p className="subtitle">통계를 불러오는 중...</p>
      </div>
    );
  }

  if (errorMsg && !stats) {
    return (
      <div className="mypage-section">
        <div className="error-message">{errorMsg}</div>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  const { my_record, head_to_head, monthly_trend, monthly_best, monthly_worst } = stats;
  const maxGames = Math.max(1, ...monthly_trend.map((m) => m.games));

  return (
    <>
      <div className="mypage-section">
        <div className="section-title-row">
          <h2 className="section-title">이달의 기록</h2>
          <MonthPicker value={yearMonth} onChange={setYearMonth} />
        </div>

        {errorMsg && <div className="error-message">{errorMsg}</div>}

        {!monthly_best ? (
          <p className="subtitle">이 달에는 아직 경기 기록이 없습니다.</p>
        ) : (
          <div className={`leader-cards${isLoading ? ' leader-cards-refreshing' : ''}`}>
            <div className="leader-card leader-card-best">
              <div className="leader-card-badge">🏆 이달의 베스트</div>
              <div className="leader-card-name">{monthly_best.name}</div>
              <div className="leader-card-stats">
                승률 {monthly_best.win_rate}% · {monthly_best.wins}승 {monthly_best.losses}패
                {monthly_best.draws > 0 ? ` ${monthly_best.draws}무` : ''}
              </div>
              <div className="leader-card-diff">득실차 {formatScoreDiff(monthly_best.score_diff)}</div>
            </div>

            {monthly_worst && (
              <div className="leader-card leader-card-worst">
                <div className="leader-card-badge">💪 분발이 필요해요</div>
                <div className="leader-card-name">{monthly_worst.name}</div>
                <div className="leader-card-stats">
                  승률 {monthly_worst.win_rate}% · {monthly_worst.wins}승 {monthly_worst.losses}패
                  {monthly_worst.draws > 0 ? ` ${monthly_worst.draws}무` : ''}
                </div>
                <div className="leader-card-diff">득실차 {formatScoreDiff(monthly_worst.score_diff)}</div>
              </div>
            )}
          </div>
        )}
      </div>

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
