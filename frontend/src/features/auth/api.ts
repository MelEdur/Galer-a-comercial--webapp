import { apiFetch } from '../../lib/http'
import type { CurrentUser, LoginRequest, LoginResponse } from './types'

export function login(credentials: LoginRequest): Promise<LoginResponse> {
  return apiFetch<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
}

export function getCurrentUser(): Promise<CurrentUser> {
  return apiFetch<CurrentUser>('/auth/me')
}
