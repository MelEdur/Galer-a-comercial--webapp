import { apiFetch } from '../../lib/http'
import type { ProductDetail, SimilarProductsResponse } from './types'

export function getProductDetail(productId: string): Promise<ProductDetail> {
  return apiFetch<ProductDetail>(`/public/products/${productId}`)
}

export function getSimilarProducts(
  productId: string,
): Promise<SimilarProductsResponse> {
  return apiFetch<SimilarProductsResponse>(`/public/products/${productId}/similar`)
}
