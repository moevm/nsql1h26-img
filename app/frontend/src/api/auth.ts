import { api } from '@/api/axios'
import type { AuthResponse, User } from '@/api/types'

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

export const authApi = {
  register: (data: RegisterPayload) => api.post<AuthResponse>('/auth/register/', data),
  login: (data: LoginPayload) => api.post<AuthResponse>('/auth/login/', data),
  logout: () => api.post('/auth/logout/'),
  me: () => api.get<User>('/auth/me/'),
}
