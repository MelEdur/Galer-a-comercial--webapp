import type { ReactElement, ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from './AuthContext'
import type { Role } from './types'

interface ProtectedRouteProps {
  children: ReactNode
  role?: Role
}

const HOME_PATH_BY_ROLE: Record<Role, string> = {
  admin: '/admin',
  merchant: '/comerciante',
}

export function ProtectedRoute({
  children,
  role = 'admin',
}: ProtectedRouteProps): ReactElement {
  const { token, user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <main
        aria-live="polite"
        className="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center px-6 py-16 text-center"
      >
        <p className="text-sm text-slate-600">Comprobando la sesión…</p>
      </main>
    )
  }

  if (!token || !user) {
    return <Navigate to="/login" replace />
  }

  if (user.role !== role) {
    return <Navigate to={HOME_PATH_BY_ROLE[user.role]} replace />
  }

  return <>{children}</>
}
