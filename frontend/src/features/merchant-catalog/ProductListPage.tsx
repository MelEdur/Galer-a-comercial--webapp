import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import type { ReactElement } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { listCategories, listProducts } from './api'
import { ProductTable } from './ProductTable'
import { merchantCatalogKeys } from './queryKeys'
import type { ProductFilters, ProductStatus } from './types'

const STATUS_OPTIONS: { value: ProductStatus; label: string }[] = [
  { value: 'active', label: 'Vigentes' },
  { value: 'deleted', label: 'Eliminados' },
  { value: 'all', label: 'Todos' },
]

const SEARCH_DEBOUNCE_MS = 300

function parseStatus(value: string | null): ProductStatus {
  return value === 'deleted' || value === 'all' ? value : 'active'
}

function parsePage(value: string | null): number {
  const parsed = Number(value)
  return Number.isInteger(parsed) && parsed >= 1 ? parsed : 1
}

export function ProductListPage(): ReactElement {
  const [searchParams, setSearchParams] = useSearchParams()

  const search = searchParams.get('search') ?? ''
  const status = parseStatus(searchParams.get('status'))
  const categoryParam = searchParams.get('category')
  const categoryId = categoryParam ? Number(categoryParam) : null
  const page = parsePage(searchParams.get('page'))

  const [searchInput, setSearchInput] = useState(search)

  function updateParams(next: Record<string, string | null>) {
    setSearchParams(
      (previous) => {
        const params = new URLSearchParams(previous)

        for (const [key, value] of Object.entries(next)) {
          if (value === null || value.length === 0) {
            params.delete(key)
          } else {
            params.set(key, value)
          }
        }

        return params
      },
      { replace: true },
    )
  }

  useEffect(() => {
    if (searchInput === search) {
      return
    }

    const timeout = window.setTimeout(() => {
      updateParams({ search: searchInput, page: null })
    }, SEARCH_DEBOUNCE_MS)

    return () => window.clearTimeout(timeout)
    // `updateParams` se recrea en cada render, pero solo depende del setter de la URL.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchInput, search])

  const filters: ProductFilters = {
    search,
    status,
    categoryId: Number.isInteger(categoryId) ? categoryId : null,
    page,
  }

  const productsQuery = useQuery({
    queryKey: merchantCatalogKeys.productsList(filters),
    queryFn: () => listProducts(filters),
  })

  const categoriesQuery = useQuery({
    queryKey: merchantCatalogKeys.categories,
    queryFn: listCategories,
  })

  const data = productsQuery.data
  const totalPages = data ? Math.max(data.pages, 1) : 1

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-6 py-16">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-2">
          <p className="text-xs font-semibold tracking-wide text-indigo-600 uppercase">
            Mi local
          </p>
          <h1 className="text-3xl font-bold text-slate-900">Productos</h1>
          <p className="text-sm text-slate-600">
            Administra el catálogo de productos de tu local.
          </p>
          <p>
            <Link
              to="/comerciante"
              className="text-sm font-medium text-indigo-600 hover:text-indigo-700"
            >
              ← Volver al panel
            </Link>
          </p>
        </div>
        <Link
          to="/comerciante/productos/nuevo"
          className="self-start rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
        >
          Nuevo producto
        </Link>
      </header>

      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="space-y-1">
            <label
              htmlFor="product-search"
              className="block text-sm font-medium text-slate-700"
            >
              Buscar productos
            </label>
            <input
              id="product-search"
              type="search"
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="Nombre del producto"
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            />
          </div>

          <div className="space-y-1">
            <label
              htmlFor="product-status"
              className="block text-sm font-medium text-slate-700"
            >
              Estado
            </label>
            <select
              id="product-status"
              value={status}
              onChange={(event) =>
                updateParams({ status: event.target.value, page: null })
              }
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            >
              {STATUS_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <label
              htmlFor="product-category"
              className="block text-sm font-medium text-slate-700"
            >
              Categoría
            </label>
            <select
              id="product-category"
              value={categoryParam ?? ''}
              onChange={(event) =>
                updateParams({ category: event.target.value, page: null })
              }
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            >
              <option value="">Todas las categorías</option>
              {categoriesQuery.data?.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </section>

      {productsQuery.isPending ? (
        <p aria-live="polite" className="text-sm text-slate-600">
          Cargando productos…
        </p>
      ) : null}

      {productsQuery.isError ? (
        <p
          role="alert"
          className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          No se han podido cargar los productos. Revisa tu sesión e inténtalo de nuevo.
        </p>
      ) : null}

      {data ? (
        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          {data.items.length === 0 ? (
            <p className="text-sm text-slate-600">
              No hay productos que coincidan con los filtros seleccionados.
            </p>
          ) : (
            <ProductTable products={data.items} />
          )}

          <div className="mt-6 flex flex-col gap-3 border-t border-slate-200 pt-4 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-slate-600">
              Página {data.page} de {totalPages} · {data.total} producto
              {data.total === 1 ? '' : 's'}
            </p>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => updateParams({ page: String(page - 1) })}
                disabled={page <= 1}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Anterior
              </button>
              <button
                type="button"
                onClick={() => updateParams({ page: String(page + 1) })}
                disabled={page >= totalPages}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Siguiente
              </button>
            </div>
          </div>
        </section>
      ) : null}
    </main>
  )
}
