import { apiRequest } from '../../../lib/apiClient';
import { GroupStats } from '../types/stats.types';

export async function getGroupStatsApi(groupKey: string, yearMonth?: string | null): Promise<GroupStats> {
  const params = new URLSearchParams();
  if (yearMonth) params.set('year_month', yearMonth);
  const query = params.toString();

  return apiRequest<GroupStats>(`/api/groups/${groupKey}/stats${query ? `?${query}` : ''}`);
}
