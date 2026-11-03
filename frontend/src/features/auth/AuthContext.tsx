import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'
import type { ReactNode } from 'react'
import { getCurrentUser, login as requestLogin } from './api'
import type { CurrentUser } from './types'
import { clearStoredToken, getStoredToken, setStoredToken } from '../../lib/token'

interface AuthContextValue {
  user: CurrentUser | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<CurrentUser>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [token, setToken] = useState<string | null>(() => getStoredToken())
  const [user, setUser] = useState<CurrentUser | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(() => Boolean(getStoredToken()))

  useEffect(() => {
    const storedToken = getStoredToken()

    if (!storedToken) {
      setIsLoading(false)
      return
    }

    let cancelled = false

    setIsLoading(true)

    getCurrentUser()
      .then((currentUser) => {
        if (!cancelled) {
          setUser(currentUser)
        }
      })
      .catch(() => {
        if (!cancelled) {
          clearStoredToken()
          setToken(null)
          setUser(null)
        }
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const response = await requestLogin({ email, password })

    setStoredToken(response.access_token)
    setToken(response.access_token)

    try {
      const currentUser = await getCurrentUser()
      setUser(currentUser)
      return currentUser
    } catch (error) {
      clearStoredToken()
      setToken(null)
      setUser(null)
      throw error
    }
  }, [])

  const logout = useCallback(() => {
    clearStoredToken()
    setToken(null)
    setUser(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      isLoading,
      isAuthenticated: Boolean(token && user),
      login,
      logout,
    }),
    [user, token, isLoading, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider.')
  }

  return context
}
