import type { ReactElement } from 'react'
import type { PublicCategory, PublicProductSort } from './types'

const SORT_OPTIONS: { value: PublicProductSort; label: string }[] = [
  { value: 'name', label: 'Nombre' },
  { value: 'price_asc', label: 'Precio: menor a mayor' },
  { value: 'price_desc', label: 'Precio: mayor a menor' },
]

export interface SearchFiltersProps {
  search: string
  onSearchChange: (value: string) => void
  categories: PublicCategory[]
  categoryId: number | null
  onCategoryChange: (value: string) => void
  minPrice: string
  onMinPriceChange: (value: string) => void
  maxPrice: string
  onMaxPriceChange: (value: string) => void
  sort: PublicProductSort
  onSortChange: (value: string) => void
}

export function SearchFilters({
  search,
  onSearchChange,
  categories,
  categoryId,
  onCategoryChange,
  minPrice,
  onMinPriceChange,
  maxPrice,
  onMaxPriceChange,
  sort,
  onSortChange,
}: SearchFiltersProps): ReactElement {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <div className="space-y-1 lg:col-span-2">
          <label
            htmlFor="public-product-search"
            className="block text-sm font-medium text-slate-700"
          >
            Buscar productos
          </label>
          <input
            id="public-product-search"
            type="search"
            value={search}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder="Nombre del producto"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          />
        </div>

        <div className="space-y-1">
          <label
            htmlFor="public-product-category"
            className="block text-sm font-medium text-slate-700"
          >
            Categoría
          </label>
          <select
            id="public-product-category"
            value={categoryId !== null ? String(categoryId) : ''}
            onChange={(event) => onCategoryChange(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          >
            <option value="">Todas las categorías</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-1">
          <label
            htmlFor="public-product-min-price"
            className="block text-sm font-medium text-slate-700"
          >
            Precio mínimo
          </label>
          <input
            id="public-product-min-price"
            type="number"
            min="0"
            inputMode="decimal"
            value={minPrice}
            onChange={(event) => onMinPriceChange(event.target.value)}
            placeholder="0"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          />
        </div>

        <div className="space-y-1">
          <label
            htmlFor="public-product-max-price"
            className="block text-sm font-medium text-slate-700"
          >
            Precio máximo
          </label>
          <input
            id="public-product-max-price"
            type="number"
            min="0"
            inputMode="decimal"
            value={maxPrice}
            onChange={(event) => onMaxPriceChange(event.target.value)}
            placeholder="Sin límite"
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          />
        </div>

        <div className="space-y-1 sm:col-span-2 lg:col-span-1">
          <label
            htmlFor="public-product-sort"
            className="block text-sm font-medium text-slate-700"
          >
            Ordenar por
          </label>
          <select
            id="public-product-sort"
            value={sort}
            onChange={(event) => onSortChange(event.target.value)}
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
    </section>
  )
}
