import { apiFetch } from '../../lib/http'
import type { MapResponse } from './types'

export function getStoreMap(): Promise<MapResponse> {
  return apiFetch<MapResponse>('/public/map')
}
