export interface User {
  id: string
  username: string
  first_name: string
  last_name: string
  email: string
  pending_email: string | null
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
  likes_count: number
  is_liked: boolean
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
  liked_by_me?: boolean
}

export type XAxisField = 'month' | 'day' | 'year' | 'image_format' | 'megapixels'
export type MetricField =
  | 'count'
  | 'total_size_mb'
  | 'avg_size_mb'
  | 'total_megapixels'
  | 'likes_count'

export interface StatsParams {
  search?: string
  author?: string
  date_from?: string
  date_to?: string
  image_format?: string
  min_size_mb?: string | number
  max_size_mb?: string | number
  min_width?: string | number
  max_width?: string | number
  min_height?: string | number
  max_height?: string | number
  x_axis?: XAxisField
  metric?: MetricField
}

export interface StatsResponse {
  labels: string[]
  data: number[]
  x_label: string
  metric_label: string
}
