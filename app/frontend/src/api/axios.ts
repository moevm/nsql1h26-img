import axios, { type AxiosError } from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const raw = localStorage.getItem('auth')
  const token = raw ? (JSON.parse(raw) as { token?: string }).token : null
  if (token) config.headers['Authorization'] = `Token ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (err: AxiosError) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('auth')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  },
)

export function mapDrfErrors(
  err: unknown,
  setErrors: (fields: Record<string, string>) => void,
): string | null {
  const data = (err as AxiosError<Record<string, string | string[]>>)?.response?.data
  if (!data || typeof data !== 'object') return null

  const fields: Record<string, string> = {}
  let nonFieldError: string | null = null

  for (const [key, messages] of Object.entries(data)) {
    const msg = Array.isArray(messages) ? messages[0] : String(messages)
    if (key === 'non_field_errors' || key === 'detail') {
      nonFieldError = msg
    } else {
      fields[key] = msg
    }
  }

  if (Object.keys(fields).length > 0) setErrors(fields)
  return nonFieldError
}
