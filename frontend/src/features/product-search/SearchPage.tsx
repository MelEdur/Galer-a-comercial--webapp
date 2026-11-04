import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import type { ReactElement } from 'react'
import { useSearchParams } from 'react-router-dom'
import { ApiError } from '../../lib/http'
import { listPublicCategories, searchProducts } from './api'
import { ProductCard } from './ProductCard'
import { SearchFilters } from './SearchFilters'
import { productSearchKeys } from './queryKeys'
import type { PublicProductFilters, PublicProductSort } from './types'

const SEARCH_DEBOUNCE_MS = 300

function parseSort(value: string | null): PublicProductSort {
  return value === 'price_asc' || value === 'price_desc' ? value : 'name'
}

function parsePage(value: string | null): number {
  const parsed = Number(value)
  return Number.isInteger(parsed) && parsed >= 1 ? parsed : 1
}

function parseCategoryId(value: string | null): number | null {
  if (value === null || value.trim().length === 0) {
    return null
  }

  const parsed = Number(value)
  return Number.isInteger(parsed) && parsed >= 1 ? parsed : null
}

export function SearchPage(): ReactElement {
  const [searchParams, setSearchParams] = useSearchParams()

  const search = searchParams.get('search') ?? ''
  const categoryId = parseCategoryId(searchParams.get('category'))
  const minPrice = searchParams.get('min_price') ?? ''
  const maxPrice = searchParams.get('max_price') ?? ''
  const sort = parseSort(searchParams.get('sort'))
  const page = parsePage(searchParams.get('page'))

  const [searchInput, setSearchInput] = useState(search)
  const [minPriceInput, setMinPriceInput] = useState(minPrice)
  const [maxPriceInput, setMaxPriceInput] = useState(maxPrice)

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
    const isUnchanged =
      searchInput === search &&
      minPriceInput === minPrice &&
      maxPriceInput === maxPrice

    if (isUnchanged) {
      return
    }

    const timeout = window.setTimeout(() => {
      updateParams({
        search: searchInput,
        min_price: minPriceInput,
        max_price: maxPriceInput,
        page: null,
      })
    }, SEARCH_DEBOUNCE_MS)

    return () => window.clearTimeout(timeout)
    // `updateParams` se recrea en cada render, pero solo depende del setter de la URL.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchInput, minPriceInput, maxPriceInput, search, minPrice, maxPrice])

  const filters: PublicProductFilters = {
    search,
    categoryId,
    minPrice,
    maxPrice,
    sort,
    page,
  }

  const productsQuery = useQuery({
    queryKey: productSearchKeys.productsList(filters),
    queryFn: () => searchProducts(filters),
  })

  const categoriesQuery = useQuery({
    queryKey: productSearchKeys.categories,
    queryFn: listPublicCategories,
  })

  const data = productsQuery.data
  const totalPages = data ? Math.max(data.pages, 1) : 1
  const hasCriteria =
    search.trim().length > 0 ||
    categoryId !== null ||
    minPrice.trim().length > 0 ||
    maxPrice.trim().length > 0

  const errorMessage =
    productsQuery.error instanceof ApiError && productsQuery.error.status === 422
      ? 'El rango de precio no es válido. Verifica el precio mínimo y máximo.'
      : 'No se han podido cargar los productos. Inténtalo de nuevo más tarde.'

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-6 py-16">
      <header className="space-y-2">
        <p className="text-xs font-semibold tracking-wide text-indigo-600 uppercase">
          Galería Comercial
        </p>
        <h1 className="text-3xl font-bold text-slate-900">Buscar productos</h1>
        <p className="text-sm text-slate-600">
          Encuentra productos de los locales de la galería por nombre, categoría o precio.
        </p>
      </header>

      <SearchFilters
        search={searchInput}
        onSearchChange={setSearchInput}
        categories={categoriesQuery.data ?? []}
        categoryId={categoryId}
        onCategoryChange={(value) => updateParams({ category: value, page: null })}
        minPrice={minPriceInput}
        onMinPriceChange={setMinPriceInput}
        maxPrice={maxPriceInput}
        onMaxPriceChange={setMaxPriceInput}
        sort={sort}
        onSortChange={(value) => updateParams({ sort: value, page: null })}
      />

      {productsQuery.isPending ? (
        <p aria-live="polite" className="text-sm text-slate-600">
          Buscando productos…
        </p>
      ) : null}

      {productsQuery.isError ? (
        <p
          role="alert"
          className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          {errorMessage}
        </p>
      ) : null}

      {data ? (
        <section className="space-y-6">
          {data.items.length === 0 ? (
            <p className="rounded-lg border border-slate-200 bg-white px-4 py-6 text-sm text-slate-600 shadow-sm">
              {hasCriteria
                ? 'No hay productos que coincidan con tu búsqueda.'
                : 'Todavía no hay productos disponibles en el catálogo.'}
            </p>
          ) : (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {data.items.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          )}

          <div className="flex flex-col gap-3 border-t border-slate-200 pt-4 sm:flex-row sm:items-center sm:justify-between">
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
