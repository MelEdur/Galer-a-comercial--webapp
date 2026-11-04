import type { ProductFilters } from './types'

export const merchantCatalogKeys = {
  products: ['merchant', 'products'] as const,
  productsList: (filters: ProductFilters) =>
    ['merchant', 'products', filters] as const,
  product: (productId: number) => ['merchant', 'product', productId] as const,
  categories: ['merchant', 'categories'] as const,
}
