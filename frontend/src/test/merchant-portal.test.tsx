import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { getCurrentUser, login } from '../features/auth/api'
import { AuthProvider } from '../features/auth/AuthContext'
import { LoginPage } from '../features/auth/LoginPage'
import { ProtectedRoute } from '../features/auth/ProtectedRoute'
import type { CurrentUser } from '../features/auth/types'
import { MerchantPage } from '../pages/MerchantPage'
import { ApiError } from '../lib/http'

vi.mock('../features/auth/api')

const mockedLogin = vi.mocked(login)
const mockedGetCurrentUser = vi.mocked(getCurrentUser)

const TOKEN_KEY = 'galeria.auth.token'

const ADMIN_USER: CurrentUser = {
  id: 1,
  email: 'admin@galeria.test',
  full_name: 'Admin de Prueba',
  role: 'admin',
  is_active: true,
  store_id: null,
  store: null,
}

const MERCHANT_USER: CurrentUser = {
  id: 2,
  email: 'ana@galeria.test',
  full_name: 'Ana Pérez',
  role: 'merchant',
  is_active: true,
  store_id: 2,
  store: { id: 2, number: 2, name: 'Local Dos' },
}

function renderApp(initialEntries: string[] = ['/login']) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/admin"
            element={
              <ProtectedRoute role="admin">
                <h1>Panel de administración</h1>
              </ProtectedRoute>
            }
          />
          <Route
            path="/comerciante"
            element={
              <ProtectedRoute role="merchant">
                <MerchantPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  )
}

function fillLoginForm(email = 'ana@galeria.test', password = 'secreto123') {
  fireEvent.change(screen.getByLabelText(/correo electrónico/i), {
    target: { value: email },
  })
  fireEvent.change(screen.getByLabelText(/contraseña/i), {
    target: { value: password },
  })
  fireEvent.click(screen.getByRole('button', { name: /iniciar sesión/i }))
}

beforeEach(() => {
  sessionStorage.clear()
  vi.clearAllMocks()
})

afterEach(() => {
  sessionStorage.clear()
})

describe('Login del comerciante', () => {
  it('redirige a /comerciante y muestra su local', async () => {
    mockedLogin.mockResolvedValue({ access_token: 'token-merchant', token_type: 'bearer' })
    mockedGetCurrentUser.mockResolvedValue(MERCHANT_USER)

    renderApp()
    fillLoginForm()

    expect(
      await screen.findByRole('heading', { name: 'Panel del comerciante' }),
    ).toBeInTheDocument()
    expect(screen.getAllByText('Ana Pérez').length).toBeGreaterThan(0)
    expect(screen.getByText('ana@galeria.test')).toBeInTheDocument()
    expect(screen.getByText('Local Dos')).toBeInTheDocument()
    expect(sessionStorage.getItem(TOKEN_KEY)).toBe('token-merchant')
    expect(screen.queryByRole('heading', { name: 'Panel de administración' })).not.toBeInTheDocument()
  })
})

describe('Panel del comerciante', () => {
  it('muestra nombre, correo, número y nombre del local', async () => {
    sessionStorage.setItem(TOKEN_KEY, 'token-merchant')
    mockedGetCurrentUser.mockResolvedValue(MERCHANT_USER)

    renderApp(['/comerciante'])

    expect(
      await screen.findByRole('heading', { name: 'Panel del comerciante' }),
    ).toBeInTheDocument()
    expect(screen.getAllByText('Ana Pérez').length).toBeGreaterThan(0)
    expect(screen.getByText('ana@galeria.test')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('Local Dos')).toBeInTheDocument()
    expect(screen.getByText('Productos')).toBeInTheDocument()
    expect(screen.getByText('Información del local')).toBeInTheDocument()
    expect(screen.getByText('Estadísticas')).toBeInTheDocument()
    expect(screen.getAllByText('Próximamente')).toHaveLength(3)
  })

  it('avisa cuando no hay local asignado', async () => {
    sessionStorage.setItem(TOKEN_KEY, 'token-merchant')
    mockedGetCurrentUser.mockResolvedValue({
      ...MERCHANT_USER,
      store_id: null,
      store: null,
    })

    renderApp(['/comerciante'])

    expect(
      await screen.findByText(/no tiene un local asignado/i),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Panel del comerciante' }),
    ).toBeInTheDocument()
  })
})

describe('Separación de rutas por rol', () => {
  it('redirige al administrador de /comerciante a /admin', async () => {
    sessionStorage.setItem(TOKEN_KEY, 'token-admin')
    mockedGetCurrentUser.mockResolvedValue(ADMIN_USER)

    renderApp(['/comerciante'])

    expect(
      await screen.findByRole('heading', { name: 'Panel de administración' }),
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('heading', { name: 'Panel del comerciante' }),
    ).not.toBeInTheDocument()
  })

  it('redirige al comerciante de /admin a /comerciante', async () => {
    sessionStorage.setItem(TOKEN_KEY, 'token-merchant')
    mockedGetCurrentUser.mockResolvedValue(MERCHANT_USER)

    renderApp(['/admin'])

    expect(
      await screen.findByRole('heading', { name: 'Panel del comerciante' }),
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('heading', { name: 'Panel de administración' }),
    ).not.toBeInTheDocument()
  })
})

describe('Sesión no válida', () => {
  it('limpia el token y redirige a /login cuando /auth/me responde 401', async () => {
    sessionStorage.setItem(TOKEN_KEY, 'token-vencido')
    mockedGetCurrentUser.mockRejectedValue(new ApiError(401, 'Token inválido.'))

    renderApp(['/comerciante'])

    expect(
      await screen.findByRole('heading', { name: 'Iniciar sesión' }),
    ).toBeInTheDocument()
    await waitFor(() => expect(sessionStorage.getItem(TOKEN_KEY)).toBeNull())
    expect(
      screen.queryByRole('heading', { name: 'Panel del comerciante' }),
    ).not.toBeInTheDocument()
  })
})
