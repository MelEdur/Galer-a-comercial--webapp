import { getStoredToken } from './token'

const DEFAULT_API_URL = 'http://localhost:8000/api'

function resolveApiUrl(): string {
  const configuredUrl = import.meta.env.VITE_API_URL?.trim()
  return configuredUrl && configuredUrl.length > 0 ? configuredUrl : DEFAULT_API_URL
}

export const API_URL = resolveApiUrl()

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getStoredToken()

  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  })

  if (!response.ok) {
    throw new ApiError(
      response.status,
      `La petición a ${path} ha fallado con el estado ${response.status}.`,
    )
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}
