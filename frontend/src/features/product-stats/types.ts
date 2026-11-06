export type StatsDays = 7 | 30 | 90

export type StatsPeriod =
  | { mode: 'days'; days: StatsDays }
  | { mode: 'range'; fromDate: string; toDate: string }

export interface ProductStatItem {
  product_id: number
  name: string
  search_count: number
  is_deleted: boolean
  last_searched_at: string
}

export interface ProductStatsResponse {
  from_date: string
  to_date: string
  total_searches: number
  items: ProductStatItem[]
}
