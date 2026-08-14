export interface GameParticipant {
  user_id: string;
  username: string;
  name?: string | null;
  team_color: string;
  score: number;
  is_winner: boolean | null;
}

export interface Game {
  game_id: string;
  group_key: string;
  game_type: string;
  game_status: string;
  court_number?: number | null;
  video_url?: string | null;
  played_at: string;
  created_at: string;
  deleted_at?: string | null;
  participants: GameParticipant[];
  comment_count: number;
  like_count: number;
  liked_by_me: boolean;
}

export interface GameListResponse {
  items: Game[];
  total: number;
}

export interface GameParticipantInput {
  user_id: string;
  team_color: string;
  score: number;
}

export interface CreateGameRequest {
  group_key: string;
  game_type: string;
  court_number?: number | null;
  video_url?: string | null;
  played_at?: string | null;
  participants: GameParticipantInput[];
}

export interface UpdateGameRequest {
  game_type: string;
  court_number?: number | null;
  video_url?: string | null;
  played_at?: string | null;
  participants: GameParticipantInput[];
}

export interface GameComment {
  comment_id: string;
  game_id: string;
  user_id: string;
  username: string;
  name?: string | null;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface LikeActionResponse {
  message: string;
  like_count: number;
}

export type GameSortOrder = 'desc' | 'asc';
export type GameFilterMode = 'all' | 'month';

export interface GameListFilters {
  yearMonth?: string | null;
  sort?: GameSortOrder;
  myGamesOnly?: boolean;
}

export interface GameFilterState {
  mode: GameFilterMode;
  yearMonth: string;
  sort: GameSortOrder;
  myGamesOnly: boolean;
}
