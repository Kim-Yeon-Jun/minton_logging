export interface User {
  username: string;
  name?: string | null;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  message: string;
  username: string;
  name?: string | null;
}

export interface RegisterRequest {
  username: string;
  password: string;
  name?: string | null;
}

export interface RegisterResponse {
  message: string;
  username: string;
  name?: string | null;
}
