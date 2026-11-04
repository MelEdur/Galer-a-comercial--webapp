import { apiFetch } from '../../lib/http'
import type { StoreDetail } from './types'

export function getStoreDetail(storeId: string): Promise<StoreDetail> {
  return apiFetch<StoreDetail>(`/public/stores/${storeId}`)
}
