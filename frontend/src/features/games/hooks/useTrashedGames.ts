import { getTrashedGamesApi } from '../services/gamesApi';
import { usePaginatedGames } from './usePaginatedGames';

export function useTrashedGames(groupKey: string) {
  return usePaginatedGames(getTrashedGamesApi, groupKey, '삭제 예정 목록을 불러오지 못했습니다.');
}
