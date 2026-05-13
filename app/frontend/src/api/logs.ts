import { api } from './axios'
import type { ActionTypeOption, Log, LogListParams, Paginated } from './types'

export const logsApi = {
  list(params?: LogListParams) {
    return api.get<Paginated<Log>>('/logs/', { params })
  },
  actionTypes() {
    return api.get<ActionTypeOption[]>('/logs/action-types/')
  },
}
