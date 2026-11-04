import { apiFetch } from '../../lib/http'
import type {
  Category,
  PaginatedProducts,
  Product,
  ProductFilters,
  ProductInput,
  ProductUpdateInput,
} from './types'

function buildProductQuery(filters: ProductFilters): string {
  const params = new URLSearchParams()

  if (filters.search.trim().length > 0) {
    params.set('search', filters.search.trim())
  }

  params.set('status', filters.status)

  if (filters.categoryId !== null) {
    params.set('category_id', String(filters.categoryId))
  }

  params.set('page', String(filters.page))

  if (filters.pageSize !== undefined) {
    params.set('page_size', String(filters.pageSize))
  }

  return params.toString()
}

export function listProducts(filters: ProductFilters): Promise<PaginatedProducts> {
  return apiFetch<PaginatedProducts>(`/merchant/products?${buildProductQuery(filters)}`)
}

export function getProduct(productId: number): Promise<Product> {
  return apiFetch<Product>(`/merchant/products/${productId}`)
}

export function createProduct(input: ProductInput): Promise<Product> {
  return apiFetch<Product>('/merchant/products', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function updateProduct(
  productId: number,
  input: ProductUpdateInput,
): Promise<Product> {
  return apiFetch<Product>(`/merchant/products/${productId}`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  })
}

export function deleteProduct(productId: number): Promise<void> {
  return apiFetch<void>(`/merchant/products/${productId}`, {
    method: 'DELETE',
  })
}

export function restoreProduct(productId: number): Promise<Product> {
  return apiFetch<Product>(`/merchant/products/${productId}/restore`, {
    method: 'POST',
  })
}

export function listCategories(): Promise<Category[]> {
  return apiFetch<Category[]>('/merchant/categories')
}
