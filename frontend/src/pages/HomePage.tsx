import type { ReactElement } from 'react'
import { Link } from 'react-router-dom'
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
          Descubre los productos y locales de la galería, y encuentra lo que buscas por nombre,
          categoría o precio.
        </p>
      </header>

      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Explora el catálogo</h2>
        <p className="mt-2 text-sm text-slate-600">
          Busca productos disponibles en todos los locales de la galería.
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link
            to="/explorar"
            className="inline-flex rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            Explorar la galería
          </Link>
          <Link
            to="/buscar"
            className="inline-flex rounded-md border border-indigo-600 px-4 py-2 text-sm font-semibold text-indigo-600 transition-colors hover:bg-indigo-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            Buscar productos
          </Link>
          <Link
            to="/mapa"
            className="inline-flex rounded-md border border-indigo-600 px-4 py-2 text-sm font-semibold text-indigo-600 transition-colors hover:bg-indigo-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            Mapa de la galería
          </Link>
        </div>
      </section>

      <HealthStatus />
    </main>
  )
}
