import { useQuery } from '@tanstack/react-query'
import type { ReactElement } from 'react'
import { Link } from 'react-router-dom'
import { getStoreMap } from './api'
import { MapLayout } from './MapLayout'
import { storeMapKeys } from './queryKeys'

export function StoreMapPage(): ReactElement {
  const mapQuery = useQuery({
    queryKey: storeMapKeys.map,
    queryFn: getStoreMap,
  })

  const stores = mapQuery.data?.stores

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-6 px-6 py-16">
      <header className="space-y-2">
        <p className="text-xs font-semibold tracking-wide text-indigo-600 uppercase">
          Galería Comercial
        </p>
        <h1 className="text-3xl font-bold text-slate-900">Mapa de la galería</h1>
        <p className="max-w-2xl text-sm text-slate-600">
          Consulta la ubicación esquemática de los locales y abre la ficha de
          cada local para ver su información.
        </p>
      </header>

      <Link
        to="/"
        className="w-fit text-sm font-semibold text-indigo-600 hover:text-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
      >
        ← Volver al inicio
      </Link>

      {mapQuery.isPending ? (
        <p aria-live="polite" className="text-sm text-slate-600">
          Cargando mapa…
        </p>
      ) : null}

      {mapQuery.isError ? (
        <p
          role="alert"
          className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          No se ha podido cargar el mapa de la galería. Inténtalo de nuevo más
          tarde.
        </p>
      ) : null}

      {stores ? (
        stores.length === 0 ? (
          <p className="rounded-lg border border-slate-200 bg-white px-4 py-6 text-sm text-slate-600 shadow-sm">
            Todavía no hay locales disponibles en el mapa.
          </p>
        ) : (
          <MapLayout stores={stores} />
        )
      ) : null}
    </main>
  )
}
