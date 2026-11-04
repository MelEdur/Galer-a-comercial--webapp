import type { PublicCategory, PublicProduct } from '../product-search/types'

export interface ProductImageDetail {
  id: number
  url: string
  alt_text: string | null
  position: number
  is_primary: boolean
}

export interface StoreDetail {
  id: number
  number: number
  name: string
  logo_url: string | null
  email: string | null
  phone: string | null
  whatsapp: string | null
}

export interface ProductDetail {
  id: number
  name: string
  description: string | null
  price: string
  offer_price: string | null
  effective_price: string
  categories: PublicCategory[]
  images: ProductImageDetail[]
  store: StoreDetail
}

export interface SimilarProductsResponse {
  items: PublicProduct[]
}
