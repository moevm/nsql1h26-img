export interface User {
  id: string
  username: string
  email: string
  role: 'user' | 'admin'
  date_joined: string
}

export interface PublicUser {
  id: string
  username: string
  first_name: string
  last_name: string
  date_joined: string
}

export interface AuthResponse {
  token: string
  user: User
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface Image {
  id: string
  title: string
  description: string
  file: string
  image_format: string
  width: number
  height: number
  file_size_mb: number
  created_at: string
  updated_at: string
  author: string
  author_username: string
}

export interface ImageListParams {
  search?: string
  author?: string
  date_from?: string
  date_to?: string
  image_format?: string
  min_size_mb?: number
  max_size_mb?: number
  min_width?: number
  max_width?: number
  min_height?: number
  max_height?: number
  page?: number
}
