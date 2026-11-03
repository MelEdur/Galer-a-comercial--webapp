export interface MerchantStore {
  id: number
  number: number
  name: string
}

export interface Merchant {
  id: number
  email: string
  full_name: string
  is_active: boolean
  created_at: string
  store: MerchantStore | null
}

export interface StoreMerchant {
  id: number
  full_name: string
  email: string
}

export type StoreSide = 'left' | 'right' | 'back'

export interface StoreAdmin {
  id: number
  number: number
  name: string
  side: StoreSide
  position: number
  is_active: boolean
  merchant: StoreMerchant | null
}

export interface CreateMerchantInput {
  email: string
  full_name: string
  password: string
  store_id: number
}
