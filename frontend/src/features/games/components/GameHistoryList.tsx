import { useState } from 'react';
import { deleteGameApi, likeGameApi, unlikeGameApi } from '../services/gamesApi';
import { Game, GameFilterState, GameParticipant } from '../types/game.types';
import { getVideoEmbedUrl } from '../utils/videoEmbed';
import GameComments from './GameComments';
import GameFilterBar from './GameFilterBar';

export interface GameHistoryListProps {
  games: Game[];
  total: number;
  hasMore: boolean;
  isLoading: boolean;
  isLoadingMore: boolean;
  errorMsg: string;
  currentUserId: string;
  filters: GameFilterState;
  onFiltersChange: (patch: Partial<GameFilterState>) => void;
  onLoadMore: () => void;
  onDeleted: () => void;
  onEdit: (game: Game) => void;
  updateGame: (gameId: string, patch: Partial<Game>) => void;
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
  currentUserId,
  filters,
  onFiltersChange,
  onLoadMore,
  onDeleted,
  onEdit,
  updateGame,
}: GameHistoryListProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string>('');
  const [likingId, setLikingId] = useState<string | null>(null);
  const [openIds, setOpenIds] = useState<Set<string>>(new Set());
  const [openCommentsId, setOpenCommentsId] = useState<string | null>(null);

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

  const handleToggleLike = async (game: Game) => {
    if (likingId) return;
    setLikingId(game.game_id);

    try {
      if (game.liked_by_me) {
        const result = await unlikeGameApi(game.game_id);
        updateGame(game.game_id, { liked_by_me: false, like_count: result.like_count });
      } else {
        const result = await likeGameApi(game.game_id);
        updateGame(game.game_id, { liked_by_me: true, like_count: result.like_count });
      }
    } catch {
      // 좋아요 토글 실패는 화면 하단 에러 배너 없이 조용히 무시 (다음 클릭에서 재시도 가능)
    } finally {
      setLikingId(null);
    }
  };

  const toggleComments = (gameId: string) => {
    setOpenCommentsId((prev) => (prev === gameId ? null : gameId));
  };

  const toggleOpen = (gameId: string) => {
    setOpenIds((prev) => {
      const next = new Set(prev);
      if (next.has(gameId)) {
        next.delete(gameId);
      } else {
        next.add(gameId);
      }
      return next;
    });
  };

  return (
    <div className="mypage-section">
      <div className="section-title-row">
        <h2 className="section-title">경기 이력{total > 0 ? ` (${total})` : ''}</h2>
        <label className="game-filter-checkbox">
          <input
            type="checkbox"
            checked={filters.myGamesOnly}
            onChange={(e) => onFiltersChange({ myGamesOnly: e.target.checked })}
          />
          내가 참여한 경기만 보기
        </label>
      </div>

      <GameFilterBar filters={filters} onChange={onFiltersChange} />

      {deleteError && <div className="error-message">{deleteError}</div>}
      {errorMsg && <div className="error-message">{errorMsg}</div>}
      {isLoading && games.length === 0 && !errorMsg && (
        <p className="subtitle">경기 이력을 불러오는 중...</p>
      )}
      {!isLoading && !errorMsg && games.length === 0 && (
        <p className="subtitle">등록된 경기가 없습니다.</p>
      )}

      {games.length > 0 && (
        <>
          <ul className={`game-list${isLoading ? ' game-list-refreshing' : ''}`}>
            {games.map((game) => {
              const teamA = teamMembers(game.participants, 'A');
              const teamB = teamMembers(game.participants, 'B');
              const teamAScore = teamA[0]?.score ?? 0;
              const teamBScore = teamB[0]?.score ?? 0;
              const teamANames = teamA.map((p) => p.name || p.username).join(', ');
              const teamBNames = teamB.map((p) => p.name || p.username).join(', ');
              const isOpen = openIds.has(game.game_id);

              return (
                <li key={game.game_id} className="game-item">
                  <div
                    className="game-item-summary"
                    role="button"
                    tabIndex={0}
                    onClick={() => toggleOpen(game.game_id)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        toggleOpen(game.game_id);
                      }
                    }}
                  >
                    <div className="game-item-summary-header">
                      <span className="game-item-date">
                        {new Date(game.played_at).toLocaleString('ko-KR')}
                      </span>
                      <span className={`game-item-chevron${isOpen ? ' game-item-chevron-open' : ''}`}>
                        ▾
                      </span>
                    </div>
                    <div className="game-item-summary-score">
                      <span className="game-item-summary-team">{teamANames}</span>
                      <span
                        className={`game-item-summary-points${
                          teamAScore > teamBScore ? ' game-item-summary-points-win' : ''
                        }`}
                      >
                        {teamAScore}
                      </span>
                      <span className="game-item-summary-sep">:</span>
                      <span
                        className={`game-item-summary-points${
                          teamBScore > teamAScore ? ' game-item-summary-points-win' : ''
                        }`}
                      >
                        {teamBScore}
                      </span>
                      <span className="game-item-summary-team">{teamBNames}</span>
                    </div>
                  </div>

                  {isOpen && (
                    <div className="game-item-detail">
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

                      <div className="game-item-teams">
                        <div className={`game-item-team${teamAScore > teamBScore ? ' game-item-team-win' : ''}`}>
                          <span className="game-item-team-label">A팀</span>
                          <span className="game-item-team-score">{teamAScore}</span>
                          <span className="game-item-team-members">{teamANames}</span>
                        </div>
                        <div className="game-item-vs">vs</div>
                        <div className={`game-item-team${teamBScore > teamAScore ? ' game-item-team-win' : ''}`}>
                          <span className="game-item-team-label">B팀</span>
                          <span className="game-item-team-score">{teamBScore}</span>
                          <span className="game-item-team-members">{teamBNames}</span>
                        </div>
                      </div>

                      {game.video_url && (() => {
                        const embedUrl = getVideoEmbedUrl(game.video_url);
                        return embedUrl ? (
                          <div className="game-video">
                            <iframe
                              src={embedUrl}
                              title="경기 영상"
                              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                              allowFullScreen
                            />
                          </div>
                        ) : (
                          <a
                            className="game-video-link"
                            href={game.video_url}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            🎬 영상 보기
                          </a>
                        );
                      })()}

                      <div className="game-item-social">
                        <button
                          type="button"
                          className={`like-button${game.liked_by_me ? ' like-button-active' : ''}`}
                          onClick={() => handleToggleLike(game)}
                          disabled={likingId === game.game_id}
                        >
                          {game.liked_by_me ? '❤️' : '🤍'} {game.like_count}
                        </button>
                        <button
                          type="button"
                          className="comment-toggle-button"
                          onClick={() => toggleComments(game.game_id)}
                        >
                          💬 댓글 {game.comment_count}
                        </button>
                      </div>

                      {openCommentsId === game.game_id && (
                        <GameComments
                          gameId={game.game_id}
                          currentUserId={currentUserId}
                          onCountChange={(delta) =>
                            updateGame(game.game_id, { comment_count: game.comment_count + delta })
                          }
                        />
                      )}
                    </div>
                  )}
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
