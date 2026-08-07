import { apiRequest } from '../../../lib/apiClient';
import { CreateGameRequest, Game, GameListResponse, UpdateGameRequest } from '../types/game.types';

export async function getGroupGamesApi(groupKey: string, limit: number, offset: number): Promise<GameListResponse> {
  return apiRequest<GameListResponse>(`/api/games/group/${groupKey}?limit=${limit}&offset=${offset}`);
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
