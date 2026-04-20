import { api } from '@/api/axios'
import type { Image, ImageListParams, Paginated } from '@/api/types'

export const imagesApi = {
  list: (params?: ImageListParams) => api.get<Paginated<Image>>('/images/', { params }),
  retrieve: (id: string) => api.get<Image>(`/images/${id}/`),
  create: (data: FormData) => api.post<Image>('/images/', data),
  patch: (id: string, data: Partial<Pick<Image, 'title' | 'description'>>) =>
    api.patch<Image>(`/images/${id}/`, data),
  remove: (id: string) => api.delete(`/images/${id}/`),
}
