import { useQuery } from '@tanstack/react-query'
import type { ReactElement } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { listAdminStores, listMerchants } from './api'
import { MerchantForm } from './MerchantForm'
import { MerchantTable } from './MerchantTable'

export function MerchantsPage(): ReactElement {
  const { logout } = useAuth()
  const navigate = useNavigate()

  const merchantsQuery = useQuery({
    queryKey: ['admin', 'merchants'],
    queryFn: listMerchants,
  })

  const storesQuery = useQuery({
    queryKey: ['admin', 'stores'],
    queryFn: listAdminStores,
  })

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-8 px-6 py-16">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-2">
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
        </div>
        <button
          type="button"
          onClick={handleLogout}
          className="self-start rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400"
        >
          Cerrar sesión
        </button>
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
