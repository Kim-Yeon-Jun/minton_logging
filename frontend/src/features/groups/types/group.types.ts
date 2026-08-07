export interface Group {
  group_key: string;
  group_name: string;
  description?: string | null;
  owner_id?: string | null;
  member_count: number;
  created_at: string;
}

export interface GroupMember {
  user_id: string;
  username: string;
  name?: string | null;
  role: string;
  joined_at: string;
}

export interface GroupDetail extends Group {
  members: GroupMember[];
}

export interface JoinGroupResponse {
  message: string;
  group_key: string;
}
