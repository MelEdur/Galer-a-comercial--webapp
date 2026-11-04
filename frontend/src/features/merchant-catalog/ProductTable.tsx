import type { ReactElement } from 'react'
import { Link } from 'react-router-dom'
import { DeleteProductButton } from './DeleteProductButton'
import { RestoreProductButton } from './RestoreProductButton'
import { formatPrice } from './format'
import type { Product } from './types'

interface ProductTableProps {
  products: Product[]
}

export function ProductTable({ products }: ProductTableProps): ReactElement {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead>
          <tr className="text-left text-xs font-semibold tracking-wide text-slate-500 uppercase">
            <th className="px-3 py-2">Nombre</th>
            <th className="px-3 py-2">Precio</th>
            <th className="px-3 py-2">Oferta</th>
            <th className="px-3 py-2">Categorías</th>
            <th className="px-3 py-2">Imágenes</th>
            <th className="px-3 py-2">Estado</th>
            <th className="px-3 py-2 text-right">Acciones</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {products.map((product) => {
            const isDeleted = Boolean(product.deleted_at)

            return (
              <tr key={product.id}>
                <td className="px-3 py-3 font-medium text-slate-900">{product.name}</td>
                <td className="px-3 py-3 text-slate-700">{formatPrice(product.price)}</td>
                <td className="px-3 py-3 text-slate-700">
                  {product.offer_price ? formatPrice(product.offer_price) : '—'}
                </td>
                <td className="px-3 py-3 text-slate-700">
                  {product.categories.length > 0
                    ? product.categories.map((category) => category.name).join(', ')
                    : '—'}
                </td>
                <td className="px-3 py-3 text-slate-700">{product.images.length}</td>
                <td className="px-3 py-3">
                  <span
                    className={
                      isDeleted
                        ? 'rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-500'
                        : 'rounded-full bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700'
                    }
                  >
                    {isDeleted ? 'Eliminado' : 'Vigente'}
                  </span>
                </td>
                <td className="px-3 py-3">
                  <div className="flex flex-col items-end gap-2">
                    {isDeleted ? (
                      <RestoreProductButton product={product} />
                    ) : (
                      <Link
                        to={`/comerciante/productos/${product.id}/editar`}
                        className="rounded-md border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400"
                      >
                        Editar
                      </Link>
                    )}
                    <DeleteProductButton product={product} />
                  </div>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
