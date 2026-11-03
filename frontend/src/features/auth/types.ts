export type Role = 'admin' | 'merchant'

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface StoreSummary {
  id: number
  number: number
  name: string
}

export interface CurrentUser {
  id: number
  email: string
  full_name: string
  role: Role
  is_active: boolean
  store_id: number | null
  store: StoreSummary | null
}
