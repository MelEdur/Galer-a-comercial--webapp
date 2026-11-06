import { useQuery } from '@tanstack/react-query'
import { useEffect, useRef, useState } from 'react'
import type { FormEvent, ReactElement } from 'react'
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom'
import { listPublicCategories } from '../../features/product-search/api'
import { productSearchKeys } from '../../features/product-search/queryKeys'
import type { PublicProductSort } from '../../features/product-search/types'

const SORT_OPTIONS: { value: PublicProductSort; label: string }[] = [
  { value: 'name', label: 'Nombre' },
  { value: 'price_asc', label: 'Precio: menor a mayor' },
  { value: 'price_desc', label: 'Precio: mayor a menor' },
]

function parseSort(value: string | null): PublicProductSort {
  return value === 'price_asc' || value === 'price_desc' ? value : 'name'
}

export function HeaderSearch(): ReactElement {
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const queryString = searchParams.toString()

  const [isPanelOpen, setIsPanelOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [minPrice, setMinPrice] = useState('')
  const [maxPrice, setMaxPrice] = useState('')
  const [hasOffer, setHasOffer] = useState(false)
  const [sort, setSort] = useState<PublicProductSort>('name')

  const containerRef = useRef<HTMLDivElement | null>(null)

  const categoriesQuery = useQuery({
    queryKey: productSearchKeys.categories,
    queryFn: listPublicCategories,
  })

  // When the visitor is on the search page, the URL is the source of truth.
  useEffect(() => {
    if (location.pathname !== '/buscar') {
      return
    }

    const params = new URLSearchParams(queryString)
    setSearch(params.get('search') ?? '')
    setCategory(params.get('category') ?? '')
    setMinPrice(params.get('min_price') ?? '')
    setMaxPrice(params.get('max_price') ?? '')
    setHasOffer(params.get('has_offer') === 'true')
    setSort(parseSort(params.get('sort')))
  }, [location.pathname, queryString])

  useEffect(() => {
    if (!isPanelOpen) {
      return
    }

    function handlePointerDown(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsPanelOpen(false)
      }
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setIsPanelOpen(false)
      }
    }

    document.addEventListener('mousedown', handlePointerDown)
    document.addEventListener('keydown', handleKeyDown)

    return () => {
      document.removeEventListener('mousedown', handlePointerDown)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isPanelOpen])

  function buildSearchUrl(): string {
    const params = new URLSearchParams()

    const term = search.trim()
    if (term.length > 0) {
      params.set('search', term)
    }

    if (category.length > 0) {
      params.set('category', category)
    }

    const min = minPrice.trim()
    if (min.length > 0) {
      params.set('min_price', min)
    }

    const max = maxPrice.trim()
    if (max.length > 0) {
      params.set('max_price', max)
    }

    if (hasOffer) {
      params.set('has_offer', 'true')
    }

    if (sort !== 'name') {
      params.set('sort', sort)
    }

    const query = params.toString()
    return query.length > 0 ? `/buscar?${query}` : '/buscar'
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsPanelOpen(false)
    navigate(buildSearchUrl())
  }

  function handleApply() {
    setIsPanelOpen(false)
    navigate(buildSearchUrl())
  }

  const hasActiveFilters =
    category.length > 0 ||
    minPrice.trim().length > 0 ||
    maxPrice.trim().length > 0 ||
    hasOffer ||
    sort !== 'name'

  const categories = categoriesQuery.data ?? []

  return (
    <div ref={containerRef} className="relative">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
        <form onSubmit={handleSubmit} role="search" className="flex flex-1 gap-2">
          <label htmlFor="header-search" className="sr-only">
            Buscar en la galería
          </label>
          <input
            id="header-search"
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Buscar productos en la galería"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          />
          <button
            type="submit"
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            Buscar
          </button>
        </form>

        <button
          type="button"
          onClick={() => setIsPanelOpen((previous) => !previous)}
          aria-expanded={isPanelOpen}
          aria-controls="header-filters"
          className="inline-flex items-center justify-center gap-1 rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400"
        >
          Filtros
          {hasActiveFilters ? (
            <span
              aria-hidden="true"
              className="inline-block h-2 w-2 rounded-full bg-indigo-600"
            />
          ) : null}
        </button>
      </div>

      {isPanelOpen ? (
        <div
          id="header-filters"
          className="absolute top-full right-0 left-0 z-40 mt-2 max-h-[70vh] overflow-y-auto rounded-lg border border-slate-200 bg-white p-4 shadow-lg"
        >
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-1">
              <label
                htmlFor="header-filter-category"
                className="block text-sm font-medium text-slate-700"
              >
                Categoría
              </label>
              <select
                id="header-filter-category"
                value={category}
                onChange={(event) => setCategory(event.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              >
                <option value="">Todas las categorías</option>
                {categories.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-1">
              <label
                htmlFor="header-filter-min-price"
                className="block text-sm font-medium text-slate-700"
              >
                Precio mínimo
              </label>
              <input
                id="header-filter-min-price"
                type="number"
                min="0"
                inputMode="decimal"
                value={minPrice}
                onChange={(event) => setMinPrice(event.target.value)}
                placeholder="0"
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              />
            </div>

            <div className="space-y-1">
              <label
                htmlFor="header-filter-max-price"
                className="block text-sm font-medium text-slate-700"
              >
                Precio máximo
              </label>
              <input
                id="header-filter-max-price"
                type="number"
                min="0"
                inputMode="decimal"
                value={maxPrice}
                onChange={(event) => setMaxPrice(event.target.value)}
                placeholder="Sin límite"
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              />
            </div>

            <div className="space-y-1">
              <label
                htmlFor="header-filter-sort"
                className="block text-sm font-medium text-slate-700"
              >
                Ordenar por
              </label>
              <select
                id="header-filter-sort"
                value={sort}
                onChange={(event) =>
                  setSort(parseSort(event.target.value))
                }
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              >
                {SORT_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <input
                id="header-filter-offer"
                type="checkbox"
                checked={hasOffer}
                onChange={(event) => setHasOffer(event.target.checked)}
                className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
              />
              <label
                htmlFor="header-filter-offer"
                className="text-sm font-medium text-slate-700"
              >
                Solo ofertas
              </label>
            </div>

            <button
              type="button"
              onClick={handleApply}
              className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            >
              Aplicar
            </button>
          </div>
        </div>
      ) : null}
    </div>
  )
}
