import { useState } from 'react';
import { permanentDeleteGameApi, restoreGameApi } from '../services/gamesApi';
import { Game, GameParticipant } from '../types/game.types';

export interface DeletedGameListProps {
  games: Game[];
  total: number;
  hasMore: boolean;
  isLoading: boolean;
  isLoadingMore: boolean;
  errorMsg: string;
  onLoadMore: () => void;
  onChanged: () => void;
}

function teamMembers(participants: GameParticipant[], team: string): GameParticipant[] {
  return participants.filter((p) => p.team_color === team);
}

export default function DeletedGameList({
  games,
  total,
  hasMore,
  isLoading,
  isLoadingMore,
  errorMsg,
  onLoadMore,
  onChanged,
}: DeletedGameListProps) {
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string>('');

  const handleRestore = async (gameId: string) => {
    setActionError('');
    setPendingId(gameId);

    try {
      await restoreGameApi(gameId);
      onChanged();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : '경기 복구에 실패했습니다.');
    } finally {
      setPendingId(null);
    }
  };

  const handlePermanentDelete = async (gameId: string) => {
    if (!window.confirm('영구 삭제하면 다시 되돌릴 수 없습니다. 계속할까요?')) {
      return;
    }

    setActionError('');
    setPendingId(gameId);

    try {
      await permanentDeleteGameApi(gameId);
      onChanged();
    } catch (err: unknown) {
      setActionError(err instanceof Error ? err.message : '경기 영구 삭제에 실패했습니다.');
    } finally {
      setPendingId(null);
    }
  };

  return (
    <div className="mypage-section">
      <h2 className="section-title">삭제 예정 경기{total > 0 ? ` (${total})` : ''}</h2>

      {actionError && <div className="error-message">{actionError}</div>}
      {isLoading && <p className="subtitle">삭제 예정 목록을 불러오는 중...</p>}
      {!isLoading && errorMsg && <div className="error-message">{errorMsg}</div>}
      {!isLoading && !errorMsg && games.length === 0 && (
        <p className="subtitle">삭제 예정인 경기가 없습니다.</p>
      )}

      {!isLoading && !errorMsg && games.length > 0 && (
        <>
          <ul className="game-list">
            {games.map((game) => {
              const teamA = teamMembers(game.participants, 'A');
              const teamB = teamMembers(game.participants, 'B');
              const teamAScore = teamA[0]?.score ?? 0;
              const teamBScore = teamB[0]?.score ?? 0;
              const isPending = pendingId === game.game_id;

              return (
                <li key={game.game_id} className="game-item">
                  <div className="game-item-header">
                    <span className="game-item-date">
                      {game.deleted_at
                        ? `삭제됨: ${new Date(game.deleted_at).toLocaleString('ko-KR')}`
                        : new Date(game.played_at).toLocaleString('ko-KR')}
                    </span>
                    <div className="game-item-actions">
                      <button
                        type="button"
                        className="btn-link"
                        onClick={() => handleRestore(game.game_id)}
                        disabled={isPending}
                      >
                        복구
                      </button>
                      <button
                        type="button"
                        className="btn-link btn-link-danger"
                        onClick={() => handlePermanentDelete(game.game_id)}
                        disabled={isPending}
                      >
                        영구삭제
                      </button>
                    </div>
                  </div>

                  <div className="game-item-teams">
                    <div className={`game-item-team${teamAScore > teamBScore ? ' game-item-team-win' : ''}`}>
                      <span className="game-item-team-label">A팀</span>
                      <span className="game-item-team-score">{teamAScore}</span>
                      <span className="game-item-team-members">
                        {teamA.map((p) => p.name || p.username).join(', ')}
                      </span>
                    </div>
                    <div className="game-item-vs">vs</div>
                    <div className={`game-item-team${teamBScore > teamAScore ? ' game-item-team-win' : ''}`}>
                      <span className="game-item-team-label">B팀</span>
                      <span className="game-item-team-score">{teamBScore}</span>
                      <span className="game-item-team-members">
                        {teamB.map((p) => p.name || p.username).join(', ')}
                      </span>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>

          {hasMore && (
            <button type="button" className="btn-secondary" onClick={onLoadMore} disabled={isLoadingMore}>
              {isLoadingMore ? '불러오는 중...' : '더 보기'}
            </button>
          )}
        </>
      )}
    </div>
  );
}
