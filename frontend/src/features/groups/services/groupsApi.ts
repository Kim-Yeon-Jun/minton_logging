import { apiRequest } from '../../../lib/apiClient';
import { Group, GroupDetail, JoinGroupResponse } from '../types/group.types';

export async function getUserGroupsApi(userId: string): Promise<Group[]> {
  return apiRequest<Group[]>(`/api/groups/user/${userId}`);
}

export async function getGroupDetailApi(groupKey: string): Promise<GroupDetail> {
  return apiRequest<GroupDetail>(`/api/groups/${groupKey}`);
}

export async function createGroupApi(groupName: string, description: string | null): Promise<Group> {
  return apiRequest<Group>('/api/groups', {
    method: 'POST',
    body: JSON.stringify({ group_name: groupName, description }),
  });
}

export async function joinGroupApi(groupKey: string): Promise<JoinGroupResponse> {
  return apiRequest<JoinGroupResponse>(`/api/groups/${groupKey}/join`, {
    method: 'POST',
    body: JSON.stringify({}),
  });
}
