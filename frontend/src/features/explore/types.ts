import type { PublicProduct } from '../product-search/types'

export interface ExploreCategory {
  id: number
  name: string
  product_count: number
}

export interface ExploreStore {
  id: number
  number: number
  name: string
  description: string | null
  logo_url: string | null
}

export interface ExploreResponse {
  featured: PublicProduct[]
  offers: PublicProduct[]
  categories: ExploreCategory[]
  stores: ExploreStore[]
}
