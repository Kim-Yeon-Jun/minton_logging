import { getGroupGamesApi } from '../services/gamesApi';
import { usePaginatedGames } from './usePaginatedGames';

export function useGroupGames(groupKey: string) {
  return usePaginatedGames(getGroupGamesApi, groupKey, '경기 이력을 불러오지 못했습니다.');
}
