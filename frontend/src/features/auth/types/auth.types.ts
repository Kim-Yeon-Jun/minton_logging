export interface User {
  id: string;
  username: string;
  name?: string | null;
  group_key?: string | null;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  message: string;
  access_token: string;
  token_type: string;
  id: string;
  username: string;
  name?: string | null;
  group_key?: string | null;
}

export interface RegisterRequest {
  username: string;
  password: string;
  name?: string | null;
}

export interface RegisterResponse {
  message: string;
  id: string;
  username: string;
  name?: string | null;
  group_key?: string | null;
}
