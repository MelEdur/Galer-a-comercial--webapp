import type { ReactElement } from 'react'
import { ProductCard } from '../product-search/ProductCard'
import type { PublicProduct } from '../product-search/types'

interface SimilarProductsProps {
  products: PublicProduct[]
}

export function SimilarProducts({
  products,
}: SimilarProductsProps): ReactElement | null {
  if (products.length === 0) {
    return null
  }

  return (
    <section aria-labelledby="similar-products-title" className="space-y-4">
      <h2 id="similar-products-title" className="text-xl font-semibold text-slate-900">
        Productos similares
      </h2>

      <ul className="-mx-1 flex snap-x gap-4 overflow-x-auto px-1 pb-2">
        {products.map((product) => (
          <li key={product.id} className="w-64 shrink-0 snap-start">
            <ProductCard product={product} />
          </li>
        ))}
      </ul>
    </section>
  )
}
