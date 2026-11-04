import type { ReactElement } from 'react'

export interface HourEntry {
  dayOfWeek: number
  opensAt: string
  closesAt: string
}

export const DAY_LABELS = [
  'Lunes',
  'Martes',
  'Miércoles',
  'Jueves',
  'Viernes',
  'Sábado',
  'Domingo',
] as const

interface HoursEditorProps {
  hours: HourEntry[]
  error?: string
  onAdd: (dayOfWeek: number) => void
  onChange: (index: number, field: 'opensAt' | 'closesAt', value: string) => void
  onRemove: (index: number) => void
}

const timeInputClass =
  'rounded-md border border-slate-300 px-2 py-1 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200'

export function HoursEditor({
  hours,
  error,
  onAdd,
  onChange,
  onRemove,
}: HoursEditorProps): ReactElement {
  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Horarios</h2>
        <p className="mt-1 text-xs text-slate-500">
          Añade uno o varios tramos por día. El cierre debe ser posterior a la apertura.
        </p>
      </div>

      <div className="space-y-3">
        {DAY_LABELS.map((dayLabel, dayOfWeek) => {
          const dayEntries = hours
            .map((hour, index) => ({ hour, index }))
            .filter(({ hour }) => hour.dayOfWeek === dayOfWeek)

          return (
            <div
              key={dayLabel}
              className="rounded-md border border-slate-200 bg-slate-50/60 p-3"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h3 className="text-sm font-semibold text-slate-800">{dayLabel}</h3>
                <button
                  type="button"
                  onClick={() => onAdd(dayOfWeek)}
                  className="rounded-md border border-slate-300 bg-white px-3 py-1 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100"
                >
                  Agregar tramo {dayLabel}
                </button>
              </div>

              {dayEntries.length === 0 ? (
                <p className="mt-2 text-xs text-slate-500">Cerrado</p>
              ) : (
                <div className="mt-2 space-y-2">
                  {dayEntries.map(({ hour, index }, position) => (
                    <div
                      key={index}
                      className="flex flex-wrap items-center gap-2"
                    >
                      <label className="flex items-center gap-1 text-xs text-slate-600">
                        Apertura
                        <input
                          type="time"
                          aria-label={`Apertura ${dayLabel} ${position + 1}`}
                          value={hour.opensAt}
                          onChange={(event) =>
                            onChange(index, 'opensAt', event.target.value)
                          }
                          className={timeInputClass}
                        />
                      </label>
                      <label className="flex items-center gap-1 text-xs text-slate-600">
                        Cierre
                        <input
                          type="time"
                          aria-label={`Cierre ${dayLabel} ${position + 1}`}
                          value={hour.closesAt}
                          onChange={(event) =>
                            onChange(index, 'closesAt', event.target.value)
                          }
                          className={timeInputClass}
                        />
                      </label>
                      <button
                        type="button"
                        onClick={() => onRemove(index)}
                        aria-label={`Quitar tramo ${dayLabel} ${position + 1}`}
                        className="rounded-md border border-slate-300 px-2 py-1 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100"
                      >
                        Quitar
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {error ? (
        <p role="alert" className="text-xs text-red-600">
          {error}
        </p>
      ) : null}
    </section>
  )
}
