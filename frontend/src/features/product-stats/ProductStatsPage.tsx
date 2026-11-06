import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import type { ReactElement } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { getProductStats } from './api'
import { ProductStatsTable } from './ProductStatsTable'
import { StatsPeriodSelector } from './StatsPeriodSelector'
import { productStatsKeys } from './queryKeys'
import type { StatsDays, StatsPeriod } from './types'

function parseDays(value: string | null): StatsDays | null {
  if (value === '7' || value === '30' || value === '90') {
    return Number(value) as StatsDays
  }

  return null
}

function resolvePeriod(
  days: StatsDays | null,
  fromDate: string | null,
  toDate: string | null,
): StatsPeriod {
  if (fromDate && toDate && fromDate <= toDate) {
    return { mode: 'range', fromDate, toDate }
  }

  return { mode: 'days', days: days ?? 30 }
}

function getPeriodKey(period: StatsPeriod): string {
  return period.mode === 'range'
    ? `range:${period.fromDate}:${period.toDate}`
    : `days:${period.days}`
}

export function ProductStatsPage(): ReactElement {
  const [searchParams, setSearchParams] = useSearchParams()

  const period = resolvePeriod(
    parseDays(searchParams.get('days')),
    searchParams.get('from'),
    searchParams.get('to'),
  )
  const periodKey = getPeriodKey(period)

  const [fromDate, setFromDate] = useState(
    period.mode === 'range' ? period.fromDate : '',
  )
  const [toDate, setToDate] = useState(period.mode === 'range' ? period.toDate : '')
  const [rangeError, setRangeError] = useState<string | null>(null)

  useEffect(() => {
    setFromDate(period.mode === 'range' ? period.fromDate : '')
    setToDate(period.mode === 'range' ? period.toDate : '')
    setRangeError(null)
  }, [periodKey])

  const statsQuery = useQuery({
    queryKey: productStatsKeys.byPeriod(period),
    queryFn: () => getProductStats(period),
  })

  function updateParams(next: Record<string, string | null>) {
    setSearchParams(
      (previous) => {
        const params = new URLSearchParams(previous)

        for (const [key, value] of Object.entries(next)) {
          if (value === null || value.length === 0) {
            params.delete(key)
          } else {
            params.set(key, value)
          }
        }

        return params
      },
      { replace: true },
    )
  }

  function handleSelectPreset(days: StatsDays) {
    setRangeError(null)
    updateParams({ days: String(days), from: null, to: null })
  }

  function handleApplyRange() {
    if (!fromDate || !toDate) {
      setRangeError('Selecciona la fecha desde y hasta.')
      return
    }

    if (fromDate > toDate) {
      setRangeError('La fecha desde no puede ser posterior a la fecha hasta.')
      return
    }

    setRangeError(null)
    updateParams({ days: null, from: fromDate, to: toDate })
  }

  const data = statsQuery.data

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-4xl flex-col gap-8 px-6 py-16">
      <header className="space-y-2">
        <p className="text-xs font-semibold tracking-wide text-indigo-600 uppercase">
          Mi local
        </p>
        <h1 className="text-3xl font-bold text-slate-900">Estadísticas</h1>
        <p className="text-sm text-slate-600">
          Consulta los productos más buscados de tu local en el período elegido.
        </p>
        <p>
          <Link
            to="/comerciante"
            className="text-sm font-medium text-indigo-600 hover:text-indigo-700"
          >
            ← Volver al panel
          </Link>
        </p>
      </header>

      <StatsPeriodSelector
        period={period}
        fromDate={fromDate}
        toDate={toDate}
        error={rangeError}
        onSelectPreset={handleSelectPreset}
        onChangeFromDate={setFromDate}
        onChangeToDate={setToDate}
        onApplyRange={handleApplyRange}
      />

      {statsQuery.isPending ? (
        <p aria-live="polite" className="text-sm text-slate-600">
          Cargando estadísticas…
        </p>
      ) : null}

      {statsQuery.isError ? (
        <p
          role="alert"
          className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          No se han podido cargar las estadísticas. Revisa tu sesión e inténtalo de
          nuevo.
        </p>
      ) : null}

      {data ? (
        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-1 border-b border-slate-200 pb-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                Top 10 productos más buscados
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                Del {data.from_date} al {data.to_date}
              </p>
            </div>
            <p className="text-sm text-slate-600">
              Total de búsquedas en el período:{' '}
              <span className="font-semibold text-slate-900">
                {data.total_searches}
              </span>
            </p>
          </div>

          {data.items.length === 0 ? (
            <p className="mt-6 text-sm text-slate-600">
              Sin búsquedas en el período
            </p>
          ) : (
            <div className="mt-4">
              <ProductStatsTable items={data.items} />
            </div>
          )}
        </section>
      ) : null}
    </main>
  )
}
