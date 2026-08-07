import { apiRequest } from '../../../lib/apiClient';
import { LoginResponse, RegisterResponse, User } from '../types/auth.types';

export async function loginApi(username: string, password: string): Promise<LoginResponse> {
  return apiRequest<LoginResponse>('/api/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}

export async function registerApi(username: string, password: string, name: string | null): Promise<RegisterResponse> {
  return apiRequest<RegisterResponse>('/api/register', {
    method: 'POST',
    body: JSON.stringify({ username, password, name }),
  });
}

export async function getMeApi(): Promise<User> {
  return apiRequest<User>('/api/me');
}
