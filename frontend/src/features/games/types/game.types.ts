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
  played_at: string;
  created_at: string;
  deleted_at?: string | null;
  participants: GameParticipant[];
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
  participants: GameParticipantInput[];
}

export interface UpdateGameRequest {
  game_type: string;
  court_number?: number | null;
  participants: GameParticipantInput[];
}
