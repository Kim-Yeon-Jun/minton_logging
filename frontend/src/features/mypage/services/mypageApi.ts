import { apiRequest } from '../../../lib/apiClient';
import { ChangePasswordResponse } from '../types/mypage.types';

export async function changePasswordApi(
  currentPassword: string,
  newPassword: string
): Promise<ChangePasswordResponse> {
  return apiRequest<ChangePasswordResponse>('/api/users/me/password', {
    method: 'PUT',
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
    }),
  });
}
