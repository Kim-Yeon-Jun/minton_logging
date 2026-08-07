import { useState } from 'react';
import { deleteGameApi } from '../services/gamesApi';
import { Game, GameParticipant } from '../types/game.types';

export interface GameHistoryListProps {
  games: Game[];
  total: number;
  hasMore: boolean;
  isLoading: boolean;
  isLoadingMore: boolean;
  errorMsg: string;
  onLoadMore: () => void;
  onDeleted: () => void;
  onEdit: (game: Game) => void;
}

function teamMembers(participants: GameParticipant[], team: string): GameParticipant[] {
  return participants.filter((p) => p.team_color === team);
}

export default function GameHistoryList({
  games,
  total,
  hasMore,
  isLoading,
  isLoadingMore,
  errorMsg,
  onLoadMore,
  onDeleted,
  onEdit,
}: GameHistoryListProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string>('');

  const handleDelete = async (gameId: string) => {
    setDeleteError('');
    setDeletingId(gameId);

    try {
      await deleteGameApi(gameId);
      onDeleted();
    } catch (err: unknown) {
      setDeleteError(err instanceof Error ? err.message : '경기 삭제에 실패했습니다.');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="mypage-section">
      <h2 className="section-title">경기 이력{total > 0 ? ` (${total})` : ''}</h2>

      {deleteError && <div className="error-message">{deleteError}</div>}
      {isLoading && <p className="subtitle">경기 이력을 불러오는 중...</p>}
      {!isLoading && errorMsg && <div className="error-message">{errorMsg}</div>}
      {!isLoading && !errorMsg && games.length === 0 && (
        <p className="subtitle">등록된 경기가 없습니다.</p>
      )}

      {!isLoading && !errorMsg && games.length > 0 && (
        <>
          <ul className="game-list">
            {games.map((game) => {
              const teamA = teamMembers(game.participants, 'A');
              const teamB = teamMembers(game.participants, 'B');
              const teamAScore = teamA[0]?.score ?? 0;
              const teamBScore = teamB[0]?.score ?? 0;

              return (
                <li key={game.game_id} className="game-item">
                  <div className="game-item-header">
                    <span className="game-item-date">
                      {new Date(game.played_at).toLocaleString('ko-KR')}
                    </span>
                    <div className="game-item-actions">
                      <button type="button" className="btn-link" onClick={() => onEdit(game)}>
                        수정
                      </button>
                      <button
                        type="button"
                        className="btn-link"
                        onClick={() => handleDelete(game.game_id)}
                        disabled={deletingId === game.game_id}
                      >
                        삭제
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
