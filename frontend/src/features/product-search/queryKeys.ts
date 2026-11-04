import type { PublicProductFilters } from './types'

export const productSearchKeys = {
  products: ['public', 'products'] as const,
  productsList: (filters: PublicProductFilters) =>
    ['public', 'products', filters] as const,
  categories: ['public', 'categories'] as const,
}
