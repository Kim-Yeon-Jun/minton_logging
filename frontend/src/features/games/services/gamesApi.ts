import { apiRequest } from '../../../lib/apiClient';
import {
  CreateGameRequest,
  Game,
  GameComment,
  GameListFilters,
  GameListResponse,
  LikeActionResponse,
  UpdateGameRequest,
} from '../types/game.types';

export async function getGroupGamesApi(
  groupKey: string,
  limit: number,
  offset: number,
  filters?: GameListFilters
): Promise<GameListResponse> {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (filters?.yearMonth) params.set('year_month', filters.yearMonth);
  if (filters?.sort) params.set('sort', filters.sort);
  if (filters?.myGamesOnly) params.set('my_games_only', 'true');

  return apiRequest<GameListResponse>(`/api/games/group/${groupKey}?${params.toString()}`);
}

export async function getTrashedGamesApi(groupKey: string, limit: number, offset: number): Promise<GameListResponse> {
  return apiRequest<GameListResponse>(`/api/games/group/${groupKey}/trash?limit=${limit}&offset=${offset}`);
}

export async function createGameApi(request: CreateGameRequest): Promise<Game> {
  return apiRequest<Game>('/api/games', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function updateGameApi(gameId: string, request: UpdateGameRequest): Promise<Game> {
  return apiRequest<Game>(`/api/games/${gameId}`, {
    method: 'PUT',
    body: JSON.stringify(request),
  });
}

export async function deleteGameApi(gameId: string): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/api/games/${gameId}`, { method: 'DELETE' });
}

export async function restoreGameApi(gameId: string): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/api/games/${gameId}/restore`, { method: 'POST' });
}

export async function permanentDeleteGameApi(gameId: string): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/api/games/${gameId}/permanent`, { method: 'DELETE' });
}

export async function getCommentsApi(gameId: string): Promise<GameComment[]> {
  return apiRequest<GameComment[]>(`/api/games/${gameId}/comments`);
}

export async function createCommentApi(gameId: string, content: string): Promise<GameComment> {
  return apiRequest<GameComment>(`/api/games/${gameId}/comments`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
}

export async function updateCommentApi(gameId: string, commentId: string, content: string): Promise<GameComment> {
  return apiRequest<GameComment>(`/api/games/${gameId}/comments/${commentId}`, {
    method: 'PUT',
    body: JSON.stringify({ content }),
  });
}

export async function deleteCommentApi(gameId: string, commentId: string): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/api/games/${gameId}/comments/${commentId}`, { method: 'DELETE' });
}

export async function likeGameApi(gameId: string): Promise<LikeActionResponse> {
  return apiRequest<LikeActionResponse>(`/api/games/${gameId}/like`, { method: 'POST' });
}

export async function unlikeGameApi(gameId: string): Promise<LikeActionResponse> {
  return apiRequest<LikeActionResponse>(`/api/games/${gameId}/like`, { method: 'DELETE' });
}
