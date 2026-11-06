import type { ReactElement } from 'react'
import { Link } from 'react-router-dom'
import { formatPrice } from './format'
import type { PublicProduct } from './types'

interface ProductCardProps {
  product: PublicProduct
  showStore?: boolean
}

export function ProductCard({
  product,
  showStore = true,
}: ProductCardProps): ReactElement {
  const hasOffer = product.offer_price !== null

  return (
    <Link
      to={`/productos/${product.id}`}
      className="group block h-full rounded-lg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
    >
      <article className="flex h-full flex-col overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm transition-shadow group-hover:shadow-md">
        <div className="flex h-40 items-center justify-center bg-slate-100">
          {product.primary_image ? (
            <img
              src={product.primary_image.url}
              alt={product.primary_image.alt_text ?? product.name}
              className="h-full w-full object-cover"
            />
          ) : (
            <span className="text-sm text-slate-400">Sin imagen</span>
          )}
        </div>

        <div className="flex flex-1 flex-col gap-3 p-4">
          <div className="space-y-1">
            <h2 className="text-base font-semibold text-slate-900">{product.name}</h2>
            {product.description ? (
              <p className="text-sm text-slate-600">{product.description}</p>
            ) : null}
          </div>

          <div className="space-y-1">
            {hasOffer ? (
              <p className="flex flex-wrap items-baseline gap-2">
                <span className="text-sm text-slate-400 line-through">
                  {formatPrice(product.price)}
                </span>
                <span className="text-lg font-bold text-emerald-700">
                  {formatPrice(product.effective_price)}
                </span>
                <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-semibold text-emerald-700">
                  Oferta
                </span>
              </p>
            ) : (
              <p className="text-lg font-bold text-slate-900">
                {formatPrice(product.price)}
              </p>
            )}
          </div>

          {product.categories.length > 0 ? (
            <ul className="flex flex-wrap gap-1.5">
              {product.categories.map((category) => (
                <li
                  key={category.id}
                  className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600"
                >
                  {category.name}
                </li>
              ))}
            </ul>
          ) : null}

          {showStore ? (
            <p className="mt-auto text-sm text-slate-500">
              Local {product.store.number} · {product.store.name}
            </p>
          ) : null}
        </div>
      </article>
    </Link>
  )
}
