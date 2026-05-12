import { api } from '@/api/axios'
import type { StatsParams, StatsResponse } from '@/api/types'

export const statsApi = {
  get: (params?: StatsParams) => api.get<StatsResponse>('/stats/', { params }),
}
