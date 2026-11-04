export interface StoreHour {
  day_of_week: number
  opens_at: string
  closes_at: string
}

export interface StoreLink {
  label: string
  url: string
  position: number
}

export interface MerchantStore {
  id: number
  number: number
  side: string
  position: number
  name: string
  description: string | null
  logo_url: string | null
  email: string | null
  phone: string | null
  whatsapp: string | null
  hours: StoreHour[]
  links: StoreLink[]
}

export interface StoreHourInput {
  day_of_week: number
  opens_at: string
  closes_at: string
}

export interface StoreLinkInput {
  label: string
  url: string
}

export interface StoreUpdateInput {
  name: string
  description: string | null
  logo_url: string | null
  email: string | null
  phone: string | null
  whatsapp: string | null
  hours: StoreHourInput[]
  links: StoreLinkInput[]
}
