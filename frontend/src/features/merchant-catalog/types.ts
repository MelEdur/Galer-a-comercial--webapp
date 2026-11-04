export interface Category {
  id: number
  name: string
}

export interface ProductImage {
  id: number
  url: string
  alt_text: string | null
  position: number
  is_primary: boolean
}

export interface Product {
  id: number
  name: string
  description: string | null
  price: string
  offer_price: string | null
  categories: Category[]
  images: ProductImage[]
  is_active: boolean
  deleted_at: string | null
  created_at: string
  updated_at: string
}

export interface ProductImageInput {
  url: string
  alt_text?: string
}

export interface ProductInput {
  name: string
  description?: string | null
  price: string
  offer_price?: string | null
  category_ids: number[]
  images?: ProductImageInput[]
}

export type ProductUpdateInput = Partial<ProductInput>

export type ProductStatus = 'active' | 'deleted' | 'all'

export interface ProductFilters {
  search: string
  status: ProductStatus
  categoryId: number | null
  page: number
  pageSize?: number
}

export interface PaginatedProducts {
  items: Product[]
  total: number
  page: number
  page_size: number
  pages: number
}
