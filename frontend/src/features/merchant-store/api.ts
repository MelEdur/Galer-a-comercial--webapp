import { apiFetch } from '../../lib/http'
import type { MerchantStore, StoreUpdateInput } from './types'

export function getMyStore(): Promise<MerchantStore> {
  return apiFetch<MerchantStore>('/merchant/store')
}

export function updateMyStore(input: StoreUpdateInput): Promise<MerchantStore> {
  return apiFetch<MerchantStore>('/merchant/store', {
    method: 'PUT',
    body: JSON.stringify(input),
  })
}
