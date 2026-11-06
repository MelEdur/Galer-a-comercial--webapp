import type { ReactElement } from 'react'
import type { StatsDays, StatsPeriod } from './types'

const PRESET_DAYS: StatsDays[] = [7, 30, 90]

interface StatsPeriodSelectorProps {
  period: StatsPeriod
  fromDate: string
  toDate: string
  error: string | null
  onSelectPreset: (days: StatsDays) => void
  onChangeFromDate: (value: string) => void
  onChangeToDate: (value: string) => void
  onApplyRange: () => void
}

export function StatsPeriodSelector({
  period,
  fromDate,
  toDate,
  error,
  onSelectPreset,
  onChangeFromDate,
  onChangeToDate,
  onApplyRange,
}: StatsPeriodSelectorProps): ReactElement {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-sm font-semibold tracking-wide text-slate-500 uppercase">
        Período
      </h2>

      <div className="mt-4 flex flex-wrap gap-2">
        {PRESET_DAYS.map((days) => {
          const isActive = period.mode === 'days' && period.days === days

          return (
            <button
              key={days}
              type="button"
              aria-pressed={isActive}
              onClick={() => onSelectPreset(days)}
              className={
                isActive
                  ? 'rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600'
                  : 'rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400'
              }
            >
              {days} días
            </button>
          )
        })}
      </div>

      <form
        className="mt-6 border-t border-slate-200 pt-4"
        onSubmit={(event) => {
          event.preventDefault()
          onApplyRange()
        }}
      >
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-[1fr_1fr_auto] sm:items-end">
          <div className="space-y-1">
            <label
              htmlFor="stats-from-date"
              className="block text-sm font-medium text-slate-700"
            >
              Desde
            </label>
            <input
              id="stats-from-date"
              type="date"
              value={fromDate}
              onChange={(event) => onChangeFromDate(event.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            />
          </div>

          <div className="space-y-1">
            <label
              htmlFor="stats-to-date"
              className="block text-sm font-medium text-slate-700"
            >
              Hasta
            </label>
            <input
              id="stats-to-date"
              type="date"
              value={toDate}
              onChange={(event) => onChangeToDate(event.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            />
          </div>

          <button
            type="submit"
            className="rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400"
          >
            Aplicar
          </button>
        </div>

        {error ? (
          <p
            role="alert"
            className="mt-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
          >
            {error}
          </p>
        ) : null}
      </form>
    </section>
  )
}
