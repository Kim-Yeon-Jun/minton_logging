export interface MyRecord {
  wins: number;
  losses: number;
  draws: number;
  win_rate: number;
}

export interface HeadToHead {
  opponent_id: string;
  opponent_name: string;
  wins: number;
  losses: number;
}

export interface MonthlyTrend {
  month: string;
  games: number;
  wins: number;
}

export interface MonthlyLeader {
  user_id: string;
  name: string;
  wins: number;
  losses: number;
  draws: number;
  win_rate: number;
  score_diff: number;
}

export interface GroupStats {
  my_record: MyRecord;
  head_to_head: HeadToHead[];
  monthly_trend: MonthlyTrend[];
  monthly_best?: MonthlyLeader | null;
  monthly_worst?: MonthlyLeader | null;
}
