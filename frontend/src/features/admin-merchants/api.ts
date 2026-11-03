import { apiFetch } from '../../lib/http'
import type { CreateMerchantInput, Merchant, StoreAdmin } from './types'

export function listMerchants(): Promise<Merchant[]> {
  return apiFetch<Merchant[]>('/admin/merchants')
}

export function createMerchant(input: CreateMerchantInput): Promise<Merchant> {
  return apiFetch<Merchant>('/admin/merchants', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function deactivateMerchant(merchantId: number): Promise<void> {
  return apiFetch<void>(`/admin/merchants/${merchantId}`, {
    method: 'DELETE',
  })
}

export function listAdminStores(): Promise<StoreAdmin[]> {
  return apiFetch<StoreAdmin[]>('/admin/stores')
}
