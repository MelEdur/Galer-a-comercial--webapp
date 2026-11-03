import { useQuery } from '@tanstack/react-query'
import type { ReactElement } from 'react'
import { getHealth } from './api'
import type { DatabaseState } from './types'

const DATABASE_LABELS: Record<DatabaseState, string> = {
  ok: 'Base de datos disponible',
  unavailable: 'Base de datos no disponible',
}

export function HealthStatus(): ReactElement {
  const { data, isPending, isError } = useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
    retry: false,
  })

  if (isPending) {
    return (
      <section
        aria-live="polite"
        className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
      >
        <h2 className="text-lg font-semibold text-slate-900">Estado del backend</h2>
        <p className="mt-2 text-sm text-slate-600">Comprobando el estado del backend…</p>
      </section>
    )
  }

  if (isError) {
    return (
      <section
        role="alert"
        className="rounded-lg border border-red-200 bg-red-50 p-6 shadow-sm"
      >
        <h2 className="text-lg font-semibold text-red-800">Backend no disponible</h2>
        <p className="mt-2 text-sm text-red-700">
          No se ha podido contactar con el backend. Inténtalo de nuevo más tarde.
        </p>
      </section>
    )
  }

  return (
    <section className="rounded-lg border border-emerald-200 bg-emerald-50 p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-emerald-900">Backend operativo</h2>
      <p className="mt-2 text-sm text-emerald-800">
        La página se comunica correctamente con la API.
      </p>
      <p className="mt-1 text-sm text-emerald-800">{DATABASE_LABELS[data.database]}</p>
    </section>
  )
}
