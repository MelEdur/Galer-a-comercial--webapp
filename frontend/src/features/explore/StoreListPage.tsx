import { useQuery } from '@tanstack/react-query'
import type { ReactElement } from 'react'
import { Link } from 'react-router-dom'
import { listPublicStores } from './api'
import { exploreKeys } from './queryKeys'
import { StoreCard } from './StoreCard'

export function StoreListPage(): ReactElement {
  const storesQuery = useQuery({
    queryKey: exploreKeys.stores,
    queryFn: listPublicStores,
  })

  const stores = storesQuery.data

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-6 py-16">
      <header className="space-y-2">
        <p className="text-xs font-semibold tracking-wide text-indigo-600 uppercase">
          Galería Comercial
        </p>
        <h1 className="text-3xl font-bold text-slate-900">Locales</h1>
        <p className="max-w-2xl text-sm text-slate-600">
          Conoce todos los locales de la galería y visita su ficha para ver su
          información de contacto y horarios.
        </p>
      </header>

      <Link
        to="/"
        className="w-fit text-sm font-semibold text-indigo-600 hover:text-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
      >
        ← Volver a explorar
      </Link>

      {storesQuery.isPending ? (
        <p aria-live="polite" className="text-sm text-slate-600">
          Cargando locales…
        </p>
      ) : null}

      {storesQuery.isError ? (
        <p
          role="alert"
          className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          No se han podido cargar los locales. Inténtalo de nuevo más tarde.
        </p>
      ) : null}

      {stores ? (
        stores.length === 0 ? (
          <p className="rounded-lg border border-slate-200 bg-white px-4 py-6 text-sm text-slate-600 shadow-sm">
            Todavía no hay locales disponibles en la galería.
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {stores.map((store) => (
              <StoreCard key={store.id} store={store} />
            ))}
          </div>
        )
      ) : null}
    </main>
  )
}
