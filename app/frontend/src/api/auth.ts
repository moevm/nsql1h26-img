import { api } from '@/api/axios'
import type { AuthResponse, PublicUser, User } from '@/api/types'

export interface RegisterPayload {
  username: string
  email: string
  password: string
  password2: string
}

export interface LoginPayload {
  login: string
  password: string
}

export interface PasswordResetRequestPayload {
  email: string
}

export interface PasswordResetConfirmPayload {
  uid: string
  token: string
  new_password: string
  new_password2: string
}

export interface ChangePasswordPayload {
  old_password: string
  new_password: string
  new_password2: string
}

export interface UpdateProfilePayload {
  username?: string
  first_name?: string
  last_name?: string
  email?: string
}

export const authApi = {
  register: (data: RegisterPayload) => api.post<AuthResponse>('/auth/register/', data),
  login: (data: LoginPayload) => api.post<AuthResponse>('/auth/login/', data),
  logout: () => api.post('/auth/logout/'),
  me: () => api.get<User>('/auth/me/'),
  getPublicProfile: (username: string) => api.get<PublicUser>(`/auth/users/${username}/`),
  requestPasswordReset: (data: PasswordResetRequestPayload) =>
    api.post<{ detail: string }>('/auth/password/reset/', data),
  confirmPasswordReset: (data: PasswordResetConfirmPayload) =>
    api.post<{ detail: string }>('/auth/password/reset/confirm/', data),
  changePassword: (data: ChangePasswordPayload) =>
    api.post<{ token: string }>('/auth/password/change/', data),
  updateProfile: (data: UpdateProfilePayload) => api.patch<User>('/auth/me/', data),
  confirmEmailChange: (data: { code: string }) => api.post<User>('/auth/email/confirm/', data),
}
