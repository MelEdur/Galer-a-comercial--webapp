import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, useLocation } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AppRoutes } from '../app/router'
import { getCurrentUser } from '../features/auth/api'
import { AuthProvider } from '../features/auth/AuthContext'
import type { CurrentUser } from '../features/auth/types'
import { getExplore, listPublicStores } from '../features/explore/api'
import type { ExploreResponse, ExploreStore } from '../features/explore/types'
import {
  listPublicCategories,
  searchProducts,
} from '../features/product-search/api'
import type {
  PaginatedPublicProducts,
  PublicCategory,
} from '../features/product-search/types'

vi.mock('../features/auth/api')
vi.mock('../features/explore/api')
vi.mock('../features/product-search/api')

const mockedGetCurrentUser = vi.mocked(getCurrentUser)
const mockedGetExplore = vi.mocked(getExplore)
const mockedListPublicStores = vi.mocked(listPublicStores)
const mockedListPublicCategories = vi.mocked(listPublicCategories)
const mockedSearchProducts = vi.mocked(searchProducts)

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

const CATEGORY: PublicCategory = { id: 1, name: 'Indumentaria' }

function emptyExplore(): ExploreResponse {
  return { featured: [], offers: [], categories: [], stores: [] }
}

function emptyPage(): PaginatedPublicProducts {
  return { items: [], total: 0, page: 1, page_size: 20, pages: 1 }
}

function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: Infinity,
      },
    },
  })
}

function LocationProbe() {
  const location = useLocation()
  return <p data-testid="location">{`${location.pathname}${location.search}`}</p>
}

function renderApp(initialEntry = '/') {
  return render(
    <QueryClientProvider client={createQueryClient()}>
      <MemoryRouter initialEntries={[initialEntry]}>
        <AuthProvider>
          <AppRoutes />
          <LocationProbe />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function authenticate(user: CurrentUser) {
  sessionStorage.setItem(TOKEN_KEY, 'token-123')
  mockedGetCurrentUser.mockResolvedValue(user)
}

beforeEach(() => {
  sessionStorage.clear()
  vi.clearAllMocks()
  mockedGetExplore.mockResolvedValue(emptyExplore())
  mockedListPublicStores.mockResolvedValue([] as ExploreStore[])
  mockedListPublicCategories.mockResolvedValue([CATEGORY])
  mockedSearchProducts.mockResolvedValue(emptyPage())
})

afterEach(() => {
  sessionStorage.clear()
  vi.clearAllMocks()
})

describe('Header persistente', () => {
  it.each(['/', '/buscar', '/locales'])(
    'muestra el header en la ruta pública %s',
    (route) => {
      renderApp(route)

      expect(
        screen.getByRole('link', { name: 'Galería Comercial' }),
      ).toBeInTheDocument()
    },
  )

  it('muestra el header en el panel de administración', async () => {
    authenticate(ADMIN_USER)
    renderApp('/admin')

    expect(
      await screen.findByRole('heading', { name: 'Panel de administración' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Galería Comercial' }),
    ).toBeInTheDocument()
  })

  it('muestra el header en el panel del comerciante', async () => {
    authenticate(MERCHANT_USER)
    renderApp('/comerciante')

    expect(
      await screen.findByRole('heading', { name: 'Panel del comerciante' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Galería Comercial' }),
    ).toBeInTheDocument()
  })

  it('muestra el header sobre la página 404', () => {
    renderApp('/ruta-inexistente')

    expect(
      screen.getByRole('heading', { name: 'Página no encontrada' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Galería Comercial' }),
    ).toBeInTheDocument()
  })

  it('enlaza el nombre del sitio a la página principal', () => {
    renderApp('/buscar')

    expect(
      screen.getByRole('link', { name: 'Galería Comercial' }),
    ).toHaveAttribute('href', '/')
  })
})

describe('Búsqueda global del header', () => {
  it('envía el término a /buscar al enviar el formulario', async () => {
    renderApp('/')

    fireEvent.change(screen.getByLabelText('Buscar en la galería'), {
      target: { value: 'auriculares' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Buscar' }))

    await waitFor(() =>
      expect(screen.getByTestId('location')).toHaveTextContent(
        '/buscar?search=auriculares',
      ),
    )
  })

  it('envía la búsqueda vacía a /buscar sin filtro de texto', async () => {
    renderApp('/locales')

    fireEvent.click(screen.getByRole('button', { name: 'Buscar' }))

    await waitFor(() =>
      expect(screen.getByTestId('location')).toHaveTextContent('/buscar'),
    )
    expect(screen.getByTestId('location')).not.toHaveTextContent('search=')
  })

  it('aplica los filtros del panel en la URL del buscador', async () => {
    renderApp('/')

    fireEvent.click(screen.getByRole('button', { name: /filtros/i }))

    const categorySelect = await screen.findByLabelText('Categoría')
    await screen.findByRole('option', { name: 'Indumentaria' })
    fireEvent.change(categorySelect, { target: { value: '1' } })
    fireEvent.change(screen.getByLabelText('Precio mínimo'), {
      target: { value: '100' },
    })
    fireEvent.change(screen.getByLabelText('Precio máximo'), {
      target: { value: '500' },
    })
    fireEvent.click(screen.getByLabelText('Solo ofertas'))
    fireEvent.change(screen.getByLabelText('Ordenar por'), {
      target: { value: 'price_asc' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Aplicar' }))

    const location = screen.getByTestId('location')
    expect(location).toHaveTextContent('/buscar')
    expect(location).toHaveTextContent('category=1')
    expect(location).toHaveTextContent('min_price=100')
    expect(location).toHaveTextContent('max_price=500')
    expect(location).toHaveTextContent('has_offer=true')
    expect(location).toHaveTextContent('sort=price_asc')
  })

  it('sincroniza el campo de búsqueda con la URL en /buscar', async () => {
    renderApp('/buscar?search=audio')

    await waitFor(() =>
      expect(screen.getByLabelText('Buscar en la galería')).toHaveValue('audio'),
    )
  })

  it('cierra el panel de filtros con Escape', async () => {
    renderApp('/')

    fireEvent.click(screen.getByRole('button', { name: /filtros/i }))
    expect(await screen.findByLabelText('Categoría')).toBeInTheDocument()

    fireEvent.keyDown(document, { key: 'Escape' })

    expect(screen.queryByLabelText('Categoría')).not.toBeInTheDocument()
  })
})

describe('Acciones de cuenta', () => {
  it('muestra "Iniciar sesión" para visitantes', () => {
    renderApp('/')

    expect(
      screen.getByRole('link', { name: 'Iniciar sesión' }),
    ).toHaveAttribute('href', '/login')
    expect(
      screen.queryByRole('button', { name: 'Cerrar sesión' }),
    ).not.toBeInTheDocument()
  })

  it('muestra "Mi local" y el cierre de sesión para el comerciante', async () => {
    authenticate(MERCHANT_USER)
    renderApp('/')

    expect(
      await screen.findByRole('link', { name: 'Mi local' }),
    ).toHaveAttribute('href', '/comerciante')
    expect(
      screen.getByRole('button', { name: 'Cerrar sesión' }),
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('link', { name: 'Iniciar sesión' }),
    ).not.toBeInTheDocument()
  })

  it('muestra el panel de administración para el administrador', async () => {
    authenticate(ADMIN_USER)
    renderApp('/')

    expect(
      await screen.findByRole('link', { name: 'Panel de administración' }),
    ).toHaveAttribute('href', '/admin')
    expect(
      screen.getByRole('button', { name: 'Cerrar sesión' }),
    ).toBeInTheDocument()
  })

  it('no muestra la acción de cuenta en /login', () => {
    renderApp('/login')

    expect(
      screen.queryByRole('link', { name: 'Iniciar sesión' }),
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Cerrar sesión' }),
    ).not.toBeInTheDocument()
  })

  it('cierra la sesión y vuelve a la página principal', async () => {
    authenticate(ADMIN_USER)
    renderApp('/admin')

    const logoutButton = await screen.findByRole('button', {
      name: 'Cerrar sesión',
    })
    fireEvent.click(logoutButton)

    await waitFor(() =>
      expect(screen.getByTestId('location')).toHaveTextContent('/'),
    )
    expect(sessionStorage.getItem(TOKEN_KEY)).toBeNull()
    expect(
      await screen.findByRole('link', { name: 'Iniciar sesión' }),
    ).toBeInTheDocument()
  })
})

describe('Redirección de exploración', () => {
  it('redirige /explorar a la página principal', async () => {
    renderApp('/explorar')

    await waitFor(() =>
      expect(screen.getByTestId('location')).toHaveTextContent('/'),
    )
  })
})
