import type { ReactElement } from 'react'
import { Link } from 'react-router-dom'
import { ExploreContent } from '../features/explore/ExploreContent'

export function HomePage(): ReactElement {
  return (
    <main className="mx-auto flex w-full max-w-6xl flex-col gap-12 px-6 py-12">
      <section className="space-y-4">
        <p className="text-xs font-semibold tracking-wide text-indigo-600 uppercase">
          Galería Comercial
        </p>
        <h1 className="max-w-2xl text-3xl font-bold text-slate-900 sm:text-4xl">
          Descubre los productos y locales de la galería
        </h1>
        <p className="max-w-2xl text-base text-slate-600">
          Encuentra productos destacados, ofertas, categorías y todos los locales de la
          galería en un mismo lugar.
        </p>
        <div>
          <Link
            to="/mapa"
            className="inline-flex rounded-md bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            Ver mapa de la galería
          </Link>
        </div>
      </section>

      <ExploreContent />
    </main>
  )
}
