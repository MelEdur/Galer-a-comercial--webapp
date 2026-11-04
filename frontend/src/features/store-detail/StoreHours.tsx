import type { ReactElement } from 'react'
import type { StoreHour } from './types'

const DAY_LABELS = [
  'Lunes',
  'Martes',
  'Miércoles',
  'Jueves',
  'Viernes',
  'Sábado',
  'Domingo',
] as const

interface StoreHoursProps {
  hours: StoreHour[]
}

function formatTime(value: string): string {
  return value.slice(0, 5)
}

function sortHours(hours: StoreHour[]): StoreHour[] {
  return [...hours].sort((a, b) => a.opens_at.localeCompare(b.opens_at))
}

export function StoreHours({ hours }: StoreHoursProps): ReactElement | null {
  if (hours.length === 0) {
    return null
  }

  return (
    <section
      aria-labelledby="store-hours-title"
      className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
    >
      <h2
        id="store-hours-title"
        className="text-lg font-semibold text-slate-900"
      >
        Horarios
      </h2>

      <dl className="mt-4 grid gap-2 sm:grid-cols-2">
        {DAY_LABELS.map((dayLabel, dayOfWeek) => {
          const ranges = sortHours(
            hours.filter((hour) => hour.day_of_week === dayOfWeek),
          ).map((hour) => `${formatTime(hour.opens_at)} - ${formatTime(hour.closes_at)}`)

          return (
            <div
              key={dayLabel}
              className="flex items-baseline justify-between gap-3 rounded-md border border-slate-200 bg-slate-50/60 px-3 py-2"
            >
              <dt className="text-sm font-medium text-slate-700">{dayLabel}</dt>
              <dd className="text-sm text-slate-600">
                {ranges.length > 0 ? ranges.join(' · ') : 'Cerrado'}
              </dd>
            </div>
          )
        })}
      </dl>
    </section>
  )
}
