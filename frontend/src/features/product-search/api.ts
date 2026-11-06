import { apiFetch } from '../../lib/http'
import type {
  PaginatedPublicProducts,
  PublicCategory,
  PublicProductFilters,
} from './types'

function buildProductQuery(filters: PublicProductFilters): string {
  const params = new URLSearchParams()

  const search = filters.search.trim()
  if (search.length > 0) {
    params.set('search', search)
  }

  if (filters.categoryId !== null) {
    params.set('category_id', String(filters.categoryId))
  }

  const minPrice = filters.minPrice.trim()
  if (minPrice.length > 0) {
    params.set('min_price', minPrice)
  }

  const maxPrice = filters.maxPrice.trim()
  if (maxPrice.length > 0) {
    params.set('max_price', maxPrice)
  }

  if (filters.hasOffer) {
    params.set('has_offer', 'true')
  }

  params.set('sort', filters.sort)
  params.set('page', String(filters.page))

  return params.toString()
}

export function searchProducts(
  filters: PublicProductFilters,
): Promise<PaginatedPublicProducts> {
  return apiFetch<PaginatedPublicProducts>(`/public/products?${buildProductQuery(filters)}`)
}

export function listPublicCategories(): Promise<PublicCategory[]> {
  return apiFetch<PublicCategory[]>('/public/categories')
}
