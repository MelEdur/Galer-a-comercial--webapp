import type { ReactElement } from 'react'
import type { ProductStatItem } from './types'

interface ProductStatsTableProps {
  items: ProductStatItem[]
}

function formatLastSearched(value: string): string {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return '—'
  }

  return date.toLocaleString('es-AR', { dateStyle: 'short', timeStyle: 'short' })
}

export function ProductStatsTable({ items }: ProductStatsTableProps): ReactElement {
  const maxCount = Math.max(1, ...items.map((item) => item.search_count))

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead>
          <tr className="text-left text-xs font-semibold tracking-wide text-slate-500 uppercase">
            <th className="px-3 py-2">#</th>
            <th className="px-3 py-2">Producto</th>
            <th className="px-3 py-2">Búsquedas</th>
            <th className="px-3 py-2">Última búsqueda</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {items.map((item, index) => (
            <tr key={item.product_id}>
              <td className="px-3 py-3 font-semibold text-slate-500">{index + 1}</td>
              <td className="px-3 py-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-medium text-slate-900">{item.name}</span>
                  {item.is_deleted ? (
                    <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-500">
                      Eliminado
                    </span>
                  ) : null}
                </div>
              </td>
              <td className="px-3 py-3">
                <div className="flex items-center gap-3">
                  <span className="w-10 text-right font-semibold text-slate-900">
                    {item.search_count}
                  </span>
                  <div
                    className="h-2 w-32 min-w-16 overflow-hidden rounded-full bg-slate-100"
                    role="img"
                    aria-label={`${item.search_count} búsquedas`}
                  >
                    <div
                      className="h-full rounded-full bg-indigo-500"
                      style={{ width: `${(item.search_count / maxCount) * 100}%` }}
                    />
                  </div>
                </div>
              </td>
              <td className="px-3 py-3 whitespace-nowrap text-slate-700">
                {formatLastSearched(item.last_searched_at)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
