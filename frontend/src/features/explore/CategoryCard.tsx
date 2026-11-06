import type { ReactElement } from 'react'
import { Link } from 'react-router-dom'
import type { ExploreCategory } from './types'

interface CategoryCardProps {
  category: ExploreCategory
}

export function CategoryCard({ category }: CategoryCardProps): ReactElement {
  const productLabel =
    category.product_count === 1 ? 'producto' : 'productos'

  return (
    <Link
      to={`/buscar?category=${category.id}`}
      className="group block h-full rounded-lg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
    >
      <article className="flex h-full flex-col justify-between gap-2 rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition-shadow group-hover:shadow-md">
        <h3 className="text-base font-semibold text-slate-900">{category.name}</h3>
        <p className="text-sm text-slate-500">
          {category.product_count} {productLabel}
        </p>
      </article>
    </Link>
  )
}
