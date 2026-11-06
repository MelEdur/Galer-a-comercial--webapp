import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import type { ReactElement } from 'react'
import { ProductCard } from '../product-search/ProductCard'
import { listStoreProducts } from './api'
import { storeDetailKeys } from './queryKeys'

interface StoreCatalogProps {
  storeId: string
}

export function StoreCatalog({ storeId }: StoreCatalogProps): ReactElement {
  const [page, setPage] = useState(1)

  const productsQuery = useQuery({
    queryKey: storeDetailKeys.products(storeId, page),
    queryFn: () => listStoreProducts(storeId, page),
    enabled: storeId.trim().length > 0,
  })

  const data = productsQuery.data
  const totalPages = data ? Math.max(data.pages, 1) : 1

  return (
    <section
      aria-labelledby="store-catalog-title"
      className="space-y-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
    >
      <h2
        id="store-catalog-title"
        className="text-lg font-semibold text-slate-900"
      >
        Catálogo
      </h2>

      {productsQuery.isPending ? (
        <p aria-live="polite" className="text-sm text-slate-600">
          Cargando catálogo…
        </p>
      ) : null}

      {productsQuery.isError ? (
        <p
          role="alert"
          className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          No se ha podido cargar el catálogo. Inténtalo de nuevo más tarde.
        </p>
      ) : null}

      {data && data.items.length === 0 ? (
        <p className="text-sm text-slate-600">
          Este local todavía no tiene productos disponibles
        </p>
      ) : null}

      {data && data.items.length > 0 ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {data.items.map((product) => (
            <ProductCard key={product.id} product={product} showStore={false} />
          ))}
        </div>
      ) : null}

      {data && data.pages > 1 ? (
        <div className="flex flex-col gap-3 border-t border-slate-200 pt-4 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-slate-600">
            Página {data.page} de {totalPages} · {data.total} producto
            {data.total === 1 ? '' : 's'}
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setPage((current) => Math.max(current - 1, 1))}
              disabled={page <= 1}
              className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Anterior
            </button>
            <button
              type="button"
              onClick={() =>
                setPage((current) => Math.min(current + 1, totalPages))
              }
              disabled={page >= totalPages}
              className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Siguiente
            </button>
          </div>
        </div>
      ) : null}
    </section>
  )
}
