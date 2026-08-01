import { LoginResponse, RegisterResponse } from '../types/auth.types';

const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

export async function loginApi(username: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/api/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || '로그인에 실패했습니다.');
  }

  return data as LoginResponse;
}

export async function registerApi(username: string, password: string, name: string | null): Promise<RegisterResponse> {
  const response = await fetch(`${API_BASE_URL}/api/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password, name }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || '회원가입에 실패했습니다.');
  }

  return data as RegisterResponse;
}
