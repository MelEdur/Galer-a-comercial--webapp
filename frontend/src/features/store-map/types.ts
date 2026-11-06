export type MapSide = 'left' | 'right' | 'back'

export interface MapStore {
  id: number
  number: number
  name: string
  logo_url: string | null
  side: MapSide
  position: number
}

export interface MapResponse {
  stores: MapStore[]
}
