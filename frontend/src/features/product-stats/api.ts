import { apiFetch } from '../../lib/http'
import type { ProductStatsResponse, StatsPeriod } from './types'

function buildStatsQuery(period: StatsPeriod): string {
  const params = new URLSearchParams()

  if (period.mode === 'days') {
    params.set('days', String(period.days))
  } else {
    params.set('from_date', period.fromDate)
    params.set('to_date', period.toDate)
  }

  return params.toString()
}

export function getProductStats(period: StatsPeriod): Promise<ProductStatsResponse> {
  return apiFetch<ProductStatsResponse>(
    `/merchant/stats/products?${buildStatsQuery(period)}`,
  )
}
