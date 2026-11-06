import { apiFetch } from '../../lib/http'
import type { PaginatedPublicProducts } from '../product-search/types'
import type { StoreDetail } from './types'

export const STORE_PRODUCTS_PAGE_SIZE = 12

export function getStoreDetail(storeId: string): Promise<StoreDetail> {
  return apiFetch<StoreDetail>(`/public/stores/${storeId}`)
}

export function listStoreProducts(
  storeId: string,
  page: number,
): Promise<PaginatedPublicProducts> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(STORE_PRODUCTS_PAGE_SIZE),
  })

  return apiFetch<PaginatedPublicProducts>(
    `/public/stores/${storeId}/products?${params.toString()}`,
  )
}
