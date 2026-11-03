import { apiFetch } from '../../lib/http'
import type { HealthResponse } from './types'

export function getHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>('/health')
}
