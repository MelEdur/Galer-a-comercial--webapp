export type HealthState = 'ok' | 'degraded'

export type DatabaseState = 'ok' | 'unavailable'

export interface HealthResponse {
  status: HealthState
  database: DatabaseState
}
