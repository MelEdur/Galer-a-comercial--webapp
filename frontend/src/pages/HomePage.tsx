import type { ReactElement } from 'react'
import { HealthStatus } from '../features/health/HealthStatus'

export function HomePage(): ReactElement {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col gap-10 px-6 py-16">
      <header className="space-y-3">
        <p className="text-xs font-semibold tracking-wide text-indigo-600 uppercase">
          Galería Comercial
        </p>
        <h1 className="text-3xl font-bold text-slate-900 sm:text-4xl">Galería Comercial</h1>
        <p className="max-w-2xl text-base text-slate-600">
          Punto de partida de la aplicación: descubre próximamente los locales y productos de la
          galería, así como su ubicación en el mapa interactivo.
        </p>
      </header>

      <HealthStatus />
    </main>
  )
}
