import { useEffect, useState } from 'react'
import type { ReactElement } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../features/auth/AuthContext'

const LINK_CLASSES =
  'rounded-md border border-slate-300 px-3 py-1.5 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400'

export function AccountActions(): ReactElement | null {
  const { user, isLoading, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  // Log out only after the public home route has rendered, so a protected
  // route cannot redirect to /login before the navigation completes.
  useEffect(() => {
    if (!isLoggingOut || location.pathname !== '/') {
      return
    }

    setIsLoggingOut(false)
    logout()
  }, [isLoggingOut, location.pathname, logout])

  if (location.pathname === '/login') {
    return null
  }

  if (isLoading) {
    return null
  }

  if (!user) {
    return (
      <Link to="/login" className={LINK_CLASSES}>
        Iniciar sesión
      </Link>
    )
  }

  function handleLogout() {
    setIsLoggingOut(true)
    navigate('/', { replace: true })
  }

  return (
    <nav aria-label="Cuenta" className="flex flex-wrap items-center gap-2">
      {user.role === 'merchant' ? (
        <Link to="/comerciante" className={LINK_CLASSES}>
          Mi local
        </Link>
      ) : (
        <Link to="/admin" className={LINK_CLASSES}>
          Panel de administración
        </Link>
      )}
      <button type="button" onClick={handleLogout} className={LINK_CLASSES}>
        Cerrar sesión
      </button>
    </nav>
  )
}
