import { apiFetch } from '../../lib/http'
import type { ExploreResponse, ExploreStore } from './types'

export function getExplore(): Promise<ExploreResponse> {
  return apiFetch<ExploreResponse>('/public/explore')
}

export function listPublicStores(): Promise<ExploreStore[]> {
  return apiFetch<ExploreStore[]>('/public/stores')
}
