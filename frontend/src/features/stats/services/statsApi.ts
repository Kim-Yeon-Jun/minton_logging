import { apiRequest } from '../../../lib/apiClient';
import { GroupStats } from '../types/stats.types';

export async function getGroupStatsApi(groupKey: string): Promise<GroupStats> {
  return apiRequest<GroupStats>(`/api/groups/${groupKey}/stats`);
}
