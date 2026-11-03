import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import type { ReactElement } from 'react'
import { deactivateMerchant } from './api'
import type { Merchant } from './types'

interface MerchantTableProps {
  merchants: Merchant[]
}

function describeStore(merchant: Merchant): string {
  if (!merchant.store) {
    return 'Sin local'
  }

  return `Local ${merchant.store.number} · ${merchant.store.name}`
}

export function MerchantTable({ merchants }: MerchantTableProps): ReactElement {
  const queryClient = useQueryClient()
  const [pendingId, setPendingId] = useState<number | null>(null)

  const mutation = useMutation({
    mutationFn: deactivateMerchant,
    onMutate: (merchantId) => {
      setPendingId(merchantId)
    },
    onSettled: () => {
      setPendingId(null)
      void queryClient.invalidateQueries({ queryKey: ['admin', 'merchants'] })
      void queryClient.invalidateQueries({ queryKey: ['admin', 'stores'] })
    },
  })

  function handleDeactivate(merchant: Merchant) {
    const confirmed = window.confirm(
      `¿Dar de baja a ${merchant.full_name}? Su local quedará disponible.`,
    )

    if (!confirmed) {
      return
    }

    mutation.mutate(merchant.id)
  }

  if (merchants.length === 0) {
    return (
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Comerciantes</h2>
        <p className="mt-2 text-sm text-slate-600">
          Todavía no hay comerciantes registrados.
        </p>
      </section>
    )
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">Comerciantes</h2>

      {mutation.isError ? (
        <p
          role="alert"
          className="mt-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          No se ha podido dar de baja al comerciante. Inténtalo de nuevo.
        </p>
      ) : null}

      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead>
            <tr className="text-left text-xs font-semibold tracking-wide text-slate-500 uppercase">
              <th className="px-3 py-2">Correo</th>
              <th className="px-3 py-2">Nombre</th>
              <th className="px-3 py-2">Local</th>
              <th className="px-3 py-2">Estado</th>
              <th className="px-3 py-2 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {merchants.map((merchant) => (
              <tr key={merchant.id}>
                <td className="px-3 py-3 text-slate-700">{merchant.email}</td>
                <td className="px-3 py-3 font-medium text-slate-900">
                  {merchant.full_name}
                </td>
                <td className="px-3 py-3 text-slate-700">{describeStore(merchant)}</td>
                <td className="px-3 py-3">
                  <span
                    className={
                      merchant.is_active
                        ? 'rounded-full bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700'
                        : 'rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-500'
                    }
                  >
                    {merchant.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td className="px-3 py-3 text-right">
                  {merchant.is_active ? (
                    <button
                      type="button"
                      onClick={() => handleDeactivate(merchant)}
                      disabled={pendingId === merchant.id}
                      className="rounded-md border border-red-300 px-3 py-1.5 text-xs font-semibold text-red-700 transition-colors hover:bg-red-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-400 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {pendingId === merchant.id ? 'Dando de baja…' : 'Dar de baja'}
                    </button>
                  ) : (
                    <span className="text-xs text-slate-400">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
