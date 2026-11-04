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

export interface StoreDetail {
  id: number
  number: number
  name: string
  description: string | null
  logo_url: string | null
  email: string | null
  phone: string | null
  whatsapp: string | null
  hours: StoreHour[]
  links: StoreLink[]
}
