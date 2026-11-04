import type { ReactElement } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../features/auth/AuthContext'

interface UpcomingSectionProps {
  title: string
  description: string
}

function UpcomingSection({ title, description }: UpcomingSectionProps): ReactElement {
  return (
    <section className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-6">
      <h2 className="text-lg font-semibold text-slate-700">{title}</h2>
      <p className="mt-2 text-sm text-slate-500">{description}</p>
      <p className="mt-4 inline-block rounded-full bg-slate-200 px-3 py-1 text-xs font-semibold text-slate-600 uppercase">
        Próximamente
      </p>
    </section>
  )
}

interface SectionLinkProps {
  title: string
  description: string
  to: string
  actionLabel: string
}

function SectionLink({ title, description, to, actionLabel }: SectionLinkProps): ReactElement {
  return (
    <Link
      to={to}
      className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm transition-colors hover:border-indigo-300 hover:bg-indigo-50/40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500"
    >
      <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
      <p className="mt-2 text-sm text-slate-600">{description}</p>
      <span className="mt-4 inline-block text-sm font-semibold text-indigo-600">
        {actionLabel} →
      </span>
    </Link>
  )
}

export function MerchantPage(): ReactElement {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  const store = user?.store ?? null

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col gap-8 px-6 py-16">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-2">
          <p className="text-xs font-semibold tracking-wide text-indigo-600 uppercase">
            Mi local
          </p>
          <h1 className="text-3xl font-bold text-slate-900">Panel del comerciante</h1>
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
        <h2 className="text-lg font-semibold text-slate-900">Mis datos</h2>
        <dl className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-xs font-semibold tracking-wide text-slate-500 uppercase">
              Nombre completo
            </dt>
            <dd className="mt-1 text-sm text-slate-900">{user?.full_name ?? '—'}</dd>
          </div>
          <div>
            <dt className="text-xs font-semibold tracking-wide text-slate-500 uppercase">
              Correo electrónico
            </dt>
            <dd className="mt-1 text-sm text-slate-900">{user?.email ?? '—'}</dd>
          </div>
        </dl>

        {store ? (
          <div className="mt-6 border-t border-slate-200 pt-4">
            <h3 className="text-sm font-semibold text-slate-900">Local asignado</h3>
            <dl className="mt-3 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt className="text-xs font-semibold tracking-wide text-slate-500 uppercase">
                  Número
                </dt>
                <dd className="mt-1 text-sm text-slate-900">{store.number}</dd>
              </div>
              <div>
                <dt className="text-xs font-semibold tracking-wide text-slate-500 uppercase">
                  Nombre
                </dt>
                <dd className="mt-1 text-sm text-slate-900">{store.name}</dd>
              </div>
            </dl>
          </div>
        ) : (
          <p
            role="alert"
            className="mt-6 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800"
          >
            Tu cuenta no tiene un local asignado todavía.
          </p>
        )}
      </section>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
        <SectionLink
          title="Productos"
          description="Gestiona el catálogo de productos de tu local."
          to="/comerciante/productos"
          actionLabel="Administrar catálogo"
        />
        <SectionLink
          title="Información del local"
          description="Edita los datos públicos de tu local."
          to="/comerciante/local"
          actionLabel="Editar información"
        />
        <UpcomingSection
          title="Estadísticas"
          description="Consulta las búsquedas de tus productos."
        />
      </div>
    </main>
  )
}
