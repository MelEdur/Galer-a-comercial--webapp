import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { getCurrentUser, login } from '../features/auth/api'
import { AuthProvider, useAuth } from '../features/auth/AuthContext'
import { LoginPage } from '../features/auth/LoginPage'
import { ProtectedRoute } from '../features/auth/ProtectedRoute'
import type { CurrentUser } from '../features/auth/types'
import { ApiError } from '../lib/http'

vi.mock('../features/auth/api')

const mockedLogin = vi.mocked(login)
const mockedGetCurrentUser = vi.mocked(getCurrentUser)

const ADMIN_USER: CurrentUser = {
  id: 1,
  email: 'admin@galeria.test',
  full_name: 'Admin de Prueba',
  role: 'admin',
  is_active: true,
  store_id: null,
  store: null,
}

const TOKEN_KEY = 'galeria.auth.token'

function renderLoginFlow() {
  return render(
    <MemoryRouter initialEntries={['/login']}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/admin"
            element={
              <ProtectedRoute>
                <h1>Panel de administración</h1>
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  )
}

function fillLoginForm(email = 'admin@galeria.test', password = 'secreto123') {
  fireEvent.change(screen.getByLabelText(/correo electrónico/i), {
    target: { value: email },
  })
  fireEvent.change(screen.getByLabelText(/contraseña/i), {
    target: { value: password },
  })
  fireEvent.click(screen.getByRole('button', { name: /iniciar sesión/i }))
}

function LogoutProbe() {
  const { logout } = useAuth()
  return (
    <button type="button" onClick={logout}>
      Cerrar sesión
    </button>
  )
}

beforeEach(() => {
  sessionStorage.clear()
  vi.clearAllMocks()
})

afterEach(() => {
  sessionStorage.clear()
})

describe('LoginPage', () => {
  it('inicia sesión, guarda el token y navega al panel', async () => {
    mockedLogin.mockResolvedValue({ access_token: 'token-123', token_type: 'bearer' })
    mockedGetCurrentUser.mockResolvedValue(ADMIN_USER)

    renderLoginFlow()
    fillLoginForm()

    expect(await screen.findByRole('heading', { name: 'Panel de administración' })).toBeInTheDocument()
    expect(mockedLogin).toHaveBeenCalledWith({
      email: 'admin@galeria.test',
      password: 'secreto123',
    })
    expect(sessionStorage.getItem(TOKEN_KEY)).toBe('token-123')
  })

  it('muestra un mensaje de credenciales inválidas ante un 401', async () => {
    mockedLogin.mockRejectedValue(new ApiError(401, 'Credenciales inválidas.'))

    renderLoginFlow()
    fillLoginForm()

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/credenciales inválidas/i)
    expect(mockedLogin).toHaveBeenCalledTimes(1)
    expect(sessionStorage.getItem(TOKEN_KEY)).toBeNull()
  })
})

describe('ProtectedRoute', () => {
  it('redirige al login cuando no hay token', async () => {
    render(
      <MemoryRouter initialEntries={['/admin']}>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<h1>Iniciar sesión</h1>} />
            <Route
              path="/admin"
              element={
                <ProtectedRoute>
                  <h1>Panel de administración</h1>
                </ProtectedRoute>
              }
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>,
    )

    expect(await screen.findByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Panel de administración' })).not.toBeInTheDocument()
    expect(mockedGetCurrentUser).not.toHaveBeenCalled()
  })
})

describe('AuthContext', () => {
  it('logout elimina el token de sessionStorage', async () => {
    sessionStorage.setItem(TOKEN_KEY, 'token-123')
    mockedGetCurrentUser.mockResolvedValue(ADMIN_USER)

    render(
      <AuthProvider>
        <LogoutProbe />
      </AuthProvider>,
    )

    await waitFor(() => expect(mockedGetCurrentUser).toHaveBeenCalledTimes(1))

    fireEvent.click(screen.getByRole('button', { name: 'Cerrar sesión' }))

    expect(sessionStorage.getItem(TOKEN_KEY)).toBeNull()
  })
})
