import { useQuery } from '@tanstack/react-query'
import type { ReactElement } from 'react'
import { Link } from 'react-router-dom'
import { ProductCard } from '../product-search/ProductCard'
import type { PublicProduct } from '../product-search/types'
import { getExplore } from './api'
import { CategoryCard } from './CategoryCard'
import { exploreKeys } from './queryKeys'
import { StoreCard } from './StoreCard'

const GRID_CLASSES = 'grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4'

interface ProductSectionProps {
  title: string
  products: PublicProduct[]
  emptyMessage: string
  action?: { to: string; label: string }
}

function ProductSection({
  title,
  products,
  emptyMessage,
  action,
}: ProductSectionProps): ReactElement {
  return (
    <section aria-labelledby={`explore-${title}`} className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2
          id={`explore-${title}`}
          className="text-2xl font-bold text-slate-900"
        >
          {title}
        </h2>
        {action ? (
          <Link
            to={action.to}
            className="text-sm font-semibold text-indigo-600 hover:text-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            {action.label}
          </Link>
        ) : null}
      </div>

      {products.length === 0 ? (
        <p className="rounded-lg border border-slate-200 bg-white px-4 py-6 text-sm text-slate-600 shadow-sm">
          {emptyMessage}
        </p>
      ) : (
        <div className={GRID_CLASSES}>
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </section>
  )
}

export function ExplorePage(): ReactElement {
  const exploreQuery = useQuery({
    queryKey: exploreKeys.explore,
    queryFn: getExplore,
  })

  const data = exploreQuery.data

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-12 px-6 py-16">
      <header className="space-y-3">
        <p className="text-xs font-semibold tracking-wide text-indigo-600 uppercase">
          Galería Comercial
        </p>
        <h1 className="text-3xl font-bold text-slate-900 sm:text-4xl">
          Explora la galería
        </h1>
        <p className="max-w-2xl text-base text-slate-600">
          Descubre productos destacados, ofertas, categorías y los locales de la
          galería.
        </p>
      </header>

      {exploreQuery.isPending ? (
        <p aria-live="polite" className="text-sm text-slate-600">
          Cargando exploración…
        </p>
      ) : null}

      {exploreQuery.isError ? (
        <p
          role="alert"
          className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          No se ha podido cargar la exploración. Inténtalo de nuevo más tarde.
        </p>
      ) : null}

      {data ? (
        <>
          <ProductSection
            title="Destacados"
            products={data.featured}
            emptyMessage="Todavía no hay productos destacados."
            action={{ to: '/buscar', label: 'Ver todos los productos' }}
          />

          <ProductSection
            title="Ofertas"
            products={data.offers}
            emptyMessage="No hay ofertas disponibles por ahora."
            action={{ to: '/buscar?has_offer=true', label: 'Ver todas las ofertas' }}
          />

          <section aria-labelledby="explore-categories" className="space-y-4">
            <h2
              id="explore-categories"
              className="text-2xl font-bold text-slate-900"
            >
              Categorías
            </h2>

            {data.categories.length === 0 ? (
              <p className="rounded-lg border border-slate-200 bg-white px-4 py-6 text-sm text-slate-600 shadow-sm">
                No hay categorías disponibles.
              </p>
            ) : (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {data.categories.map((category) => (
                  <CategoryCard key={category.id} category={category} />
                ))}
              </div>
            )}
          </section>

          <section aria-labelledby="explore-stores" className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2
                id="explore-stores"
                className="text-2xl font-bold text-slate-900"
              >
                Locales
              </h2>
              <Link
                to="/locales"
                className="text-sm font-semibold text-indigo-600 hover:text-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
              >
                Ver todos los locales
              </Link>
            </div>

            {data.stores.length === 0 ? (
              <p className="rounded-lg border border-slate-200 bg-white px-4 py-6 text-sm text-slate-600 shadow-sm">
                No hay locales disponibles.
              </p>
            ) : (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {data.stores.slice(0, 6).map((store) => (
                  <StoreCard key={store.id} store={store} />
                ))}
              </div>
            )}
          </section>
        </>
      ) : null}
    </main>
  )
}
