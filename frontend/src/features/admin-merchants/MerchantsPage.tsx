import { useQuery } from '@tanstack/react-query'
import type { ReactElement } from 'react'
import { Link } from 'react-router-dom'
import { listAdminStores, listMerchants } from './api'
import { MerchantForm } from './MerchantForm'
import { MerchantTable } from './MerchantTable'

export function MerchantsPage(): ReactElement {
  const merchantsQuery = useQuery({
    queryKey: ['admin', 'merchants'],
    queryFn: listMerchants,
  })

  const storesQuery = useQuery({
    queryKey: ['admin', 'stores'],
    queryFn: listAdminStores,
  })

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-8 px-6 py-16">
      <header className="space-y-2">
        <p className="text-xs font-semibold tracking-wide text-indigo-600 uppercase">
          Administración
        </p>
        <h1 className="text-3xl font-bold text-slate-900">Comerciantes</h1>
        <p className="text-sm text-slate-600">
          Gestiona las cuentas de comerciante y la asignación de locales.
        </p>
        <p>
          <Link to="/admin" className="text-sm font-medium text-indigo-600 hover:text-indigo-700">
            ← Volver al panel
          </Link>
        </p>
      </header>

      {merchantsQuery.isPending || storesQuery.isPending ? (
        <p aria-live="polite" className="text-sm text-slate-600">
          Cargando comerciantes y locales…
        </p>
      ) : null}

      {merchantsQuery.isError || storesQuery.isError ? (
        <p
          role="alert"
          className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          No se han podido cargar los datos. Revisa tu sesión e inténtalo de nuevo.
        </p>
      ) : null}

      {merchantsQuery.data && storesQuery.data ? (
        <>
          <MerchantForm stores={storesQuery.data} />
          <MerchantTable merchants={merchantsQuery.data} />
        </>
      ) : null}
    </main>
  )
}
