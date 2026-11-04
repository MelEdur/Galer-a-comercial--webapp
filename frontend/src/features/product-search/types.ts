export interface PublicCategory {
  id: number
  name: string
}

export interface PublicStore {
  id: number
  number: number
  name: string
}

export interface PublicImage {
  url: string
  alt_text: string | null
}

export interface PublicProduct {
  id: number
  name: string
  description: string | null
  price: string
  offer_price: string | null
  effective_price: string
  categories: PublicCategory[]
  primary_image: PublicImage | null
  store: PublicStore
}

export type PublicProductSort = 'name' | 'price_asc' | 'price_desc'

export interface PublicProductFilters {
  search: string
  categoryId: number | null
  minPrice: string
  maxPrice: string
  sort: PublicProductSort
  page: number
}

export interface PaginatedPublicProducts {
  items: PublicProduct[]
  total: number
  page: number
  page_size: number
  pages: number
}
