import React, { useEffect, useState } from 'react';
import { createCommentApi, deleteCommentApi, getCommentsApi, updateCommentApi } from '../services/gamesApi';
import { GameComment } from '../types/game.types';

export interface GameCommentsProps {
  gameId: string;
  currentUserId: string;
  onCountChange: (delta: number) => void;
}

export default function GameComments({ gameId, currentUserId, onCountChange }: GameCommentsProps) {
  const [comments, setComments] = useState<GameComment[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [content, setContent] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingContent, setEditingContent] = useState<string>('');

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setErrorMsg('');

    getCommentsApi(gameId)
      .then((data) => {
        if (!cancelled) setComments(data);
      })
      .catch((err: unknown) => {
        if (!cancelled) setErrorMsg(err instanceof Error ? err.message : '댓글을 불러오지 못했습니다.');
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [gameId]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!content.trim() || isSubmitting) return;

    setIsSubmitting(true);
    setErrorMsg('');

    try {
      const comment = await createCommentApi(gameId, content.trim());
      setComments((prev) => [...prev, comment]);
      setContent('');
      onCountChange(1);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : '댓글 등록에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const startEdit = (comment: GameComment) => {
    setEditingId(comment.comment_id);
    setEditingContent(comment.content);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditingContent('');
  };

  const handleUpdate = async (commentId: string) => {
    if (!editingContent.trim()) return;

    try {
      const updated = await updateCommentApi(gameId, commentId, editingContent.trim());
      setComments((prev) => prev.map((c) => (c.comment_id === commentId ? updated : c)));
      cancelEdit();
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : '댓글 수정에 실패했습니다.');
    }
  };

  const handleDelete = async (commentId: string) => {
    try {
      await deleteCommentApi(gameId, commentId);
      setComments((prev) => prev.filter((c) => c.comment_id !== commentId));
      onCountChange(-1);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : '댓글 삭제에 실패했습니다.');
    }
  };

  return (
    <div className="game-comments">
      {errorMsg && <div className="error-message">{errorMsg}</div>}

      {isLoading ? (
        <p className="subtitle">댓글을 불러오는 중...</p>
      ) : (
        <ul className="comment-list">
          {comments.length === 0 && <li className="comment-empty">첫 댓글을 남겨보세요.</li>}
          {comments.map((comment) => (
            <li key={comment.comment_id} className="comment-item">
              {editingId === comment.comment_id ? (
                <div className="comment-edit-form">
                  <input
                    value={editingContent}
                    onChange={(e) => setEditingContent(e.target.value)}
                    autoFocus
                  />
                  <div className="comment-edit-actions">
                    <button type="button" className="btn-link" onClick={() => handleUpdate(comment.comment_id)}>
                      저장
                    </button>
                    <button type="button" className="btn-link" onClick={cancelEdit}>
                      취소
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="comment-item-header">
                    <span className="comment-author">{comment.name || comment.username}</span>
                    <span className="comment-date">{new Date(comment.created_at).toLocaleString('ko-KR')}</span>
                  </div>
                  <p className="comment-content">{comment.content}</p>
                  {comment.user_id === currentUserId && (
                    <div className="comment-actions">
                      <button type="button" className="btn-link" onClick={() => startEdit(comment)}>
                        수정
                      </button>
                      <button
                        type="button"
                        className="btn-link btn-link-danger"
                        onClick={() => handleDelete(comment.comment_id)}
                      >
                        삭제
                      </button>
                    </div>
                  )}
                </>
              )}
            </li>
          ))}
        </ul>
      )}

      <form className="comment-form" onSubmit={handleSubmit}>
        <input
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="댓글을 입력하세요"
          disabled={isSubmitting}
        />
        <button type="submit" className="btn-link" disabled={isSubmitting || !content.trim()}>
          등록
        </button>
      </form>
    </div>
  );
}
