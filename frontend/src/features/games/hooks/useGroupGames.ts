import { getGroupGamesApi } from '../services/gamesApi';
import { GameListFilters } from '../types/game.types';
import { usePaginatedGames } from './usePaginatedGames';

export function useGroupGames(groupKey: string, filters?: GameListFilters) {
  return usePaginatedGames(getGroupGamesApi, groupKey, '경기 이력을 불러오지 못했습니다.', filters);
}
