import type { ReactElement } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../features/auth/AuthContext'

export function AdminPage(): ReactElement {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col gap-8 px-6 py-16">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-2">
          <p className="text-xs font-semibold tracking-wide text-indigo-600 uppercase">
            Administración
          </p>
          <h1 className="text-3xl font-bold text-slate-900">Panel de administración</h1>
          {user ? (
            <p className="text-sm text-slate-600">
              Sesión iniciada como <span className="font-medium">{user.full_name}</span>.
            </p>
          ) : null}
        </div>
        <button
          type="button"
          onClick={handleLogout}
          className="self-start rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400"
        >
          Cerrar sesión
        </button>
      </header>

      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Gestión de comerciantes</h2>
        <p className="mt-2 text-sm text-slate-600">
          Da de alta comerciantes y asígnales un local de la galería.
        </p>
        <p className="mt-4">
          <Link
            to="/admin/comerciantes"
            className="inline-block rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            Gestionar comerciantes
          </Link>
        </p>
      </section>
    </main>
  )
}
