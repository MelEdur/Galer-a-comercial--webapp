import type { StatsPeriod } from './types'

export const productStatsKeys = {
  all: ['merchant', 'stats', 'products'] as const,
  byPeriod: (period: StatsPeriod) =>
    ['merchant', 'stats', 'products', period] as const,
}
