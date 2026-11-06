import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { getCurrentUser } from '../features/auth/api'
import { AuthProvider } from '../features/auth/AuthContext'
import type { CurrentUser } from '../features/auth/types'
import { getProductStats } from '../features/product-stats/api'
import { ProductStatsPage } from '../features/product-stats/ProductStatsPage'
import type { ProductStatsResponse } from '../features/product-stats/types'
import { ApiError } from '../lib/http'
import { MerchantPage } from '../pages/MerchantPage'

vi.mock('../features/product-stats/api')
vi.mock('../features/auth/api')

const mockedGetProductStats = vi.mocked(getProductStats)
const mockedGetCurrentUser = vi.mocked(getCurrentUser)

const TOKEN_KEY = 'galeria.auth.token'

const MERCHANT_USER: CurrentUser = {
  id: 2,
  email: 'ana@galeria.test',
  full_name: 'Ana Pérez',
  role: 'merchant',
  is_active: true,
  store_id: 2,
  store: { id: 2, number: 2, name: 'Local Dos' },
}

function statsResponse(overrides: Partial<ProductStatsResponse> = {}): ProductStatsResponse {
  return {
    from_date: '2026-10-02',
    to_date: '2026-10-31',
    total_searches: 128,
    items: [
      {
        product_id: 1,
        name: 'Remera',
        search_count: 42,
        is_deleted: false,
        last_searched_at: '2026-10-31T18:12:00-03:00',
      },
      {
        product_id: 2,
        name: 'Pantalón',
        search_count: 20,
        is_deleted: false,
        last_searched_at: '2026-10-30T09:05:00-03:00',
      },
      {
        product_id: 3,
        name: 'Zapatilla',
        search_count: 10,
        is_deleted: false,
        last_searched_at: '2026-10-29T12:30:00-03:00',
      },
    ],
    ...overrides,
  }
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

function renderStats(initialEntry = '/comerciante/estadisticas') {
  return render(
    <QueryClientProvider client={createQueryClient()}>
      <MemoryRouter initialEntries={[initialEntry]}>
        <Routes>
          <Route path="/comerciante/estadisticas" element={<ProductStatsPage />} />
          <Route path="/comerciante" element={<h1>Panel del comerciante</h1>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function renderPanel() {
  return render(
    <MemoryRouter initialEntries={['/comerciante']}>
      <AuthProvider>
        <Routes>
          <Route path="/comerciante" element={<MerchantPage />} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  sessionStorage.clear()
  mockedGetProductStats.mockResolvedValue(statsResponse())
})

afterEach(() => {
  sessionStorage.clear()
})

describe('Estadísticas de productos', () => {
  it('carga el ranking en orden y muestra el total del período', async () => {
    renderStats()

    const table = await screen.findByRole('table')
    const rows = within(table).getAllByRole('row').slice(1)

    expect(rows).toHaveLength(3)
    expect(rows[0]).toHaveTextContent('1')
    expect(rows[0]).toHaveTextContent('Remera')
    expect(rows[0]).toHaveTextContent('42')
    expect(rows[1]).toHaveTextContent('Pantalón')
    expect(rows[2]).toHaveTextContent('Zapatilla')
    expect(screen.getByText('128')).toBeInTheDocument()
    expect(within(rows[0]).getByRole('img')).toHaveAccessibleName('42 búsquedas')
    expect(mockedGetProductStats).toHaveBeenCalledWith({ mode: 'days', days: 30 })
  })

  it('actualiza la petición al cambiar entre 7, 30 y 90 días', async () => {
    renderStats()

    await screen.findByRole('table')

    fireEvent.click(screen.getByRole('button', { name: '7 días' }))
    await waitFor(() =>
      expect(mockedGetProductStats).toHaveBeenCalledWith({ mode: 'days', days: 7 }),
    )

    fireEvent.click(screen.getByRole('button', { name: '90 días' }))
    await waitFor(() =>
      expect(mockedGetProductStats).toHaveBeenCalledWith({ mode: 'days', days: 90 }),
    )
  })

  it('aplica un rango personalizado válido', async () => {
    renderStats()

    await screen.findByRole('table')

    fireEvent.change(screen.getByLabelText('Desde'), {
      target: { value: '2026-10-01' },
    })
    fireEvent.change(screen.getByLabelText('Hasta'), {
      target: { value: '2026-10-15' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Aplicar' }))

    await waitFor(() =>
      expect(mockedGetProductStats).toHaveBeenCalledWith({
        mode: 'range',
        fromDate: '2026-10-01',
        toDate: '2026-10-15',
      }),
    )
  })

  it('rechaza un rango con la fecha desde posterior a la hasta', async () => {
    renderStats()

    await screen.findByRole('table')

    fireEvent.change(screen.getByLabelText('Desde'), {
      target: { value: '2026-10-20' },
    })
    fireEvent.change(screen.getByLabelText('Hasta'), {
      target: { value: '2026-10-10' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Aplicar' }))

    expect(
      await screen.findByText(/la fecha desde no puede ser posterior/i),
    ).toBeInTheDocument()
    expect(
      mockedGetProductStats.mock.calls.some(([period]) => period.mode === 'range'),
    ).toBe(false)
  })

  it('marca los productos eliminados', async () => {
    mockedGetProductStats.mockResolvedValue(
      statsResponse({
        items: [
          {
            product_id: 2,
            name: 'Pantalón',
            search_count: 20,
            is_deleted: true,
            last_searched_at: '2026-10-30T09:05:00-03:00',
          },
        ],
      }),
    )

    renderStats()

    expect(await screen.findByText('Pantalón')).toBeInTheDocument()
    expect(screen.getByText('Eliminado')).toBeInTheDocument()
  })

  it('muestra el estado vacío cuando no hay búsquedas en el período', async () => {
    mockedGetProductStats.mockResolvedValue(
      statsResponse({ total_searches: 0, items: [] }),
    )

    renderStats()

    expect(
      await screen.findByText('Sin búsquedas en el período'),
    ).toBeInTheDocument()
    expect(screen.queryByRole('table')).not.toBeInTheDocument()
  })

  it('muestra un mensaje de error cuando falla la consulta', async () => {
    mockedGetProductStats.mockRejectedValue(new ApiError(500, 'Error interno.'))

    renderStats()

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/no se han podido cargar las estadísticas/i)
    expect(screen.queryByRole('table')).not.toBeInTheDocument()
  })

  it('recupera el período desde la URL al cargar la página', async () => {
    renderStats('/comerciante/estadisticas?days=7')

    await screen.findByRole('table')

    expect(mockedGetProductStats).toHaveBeenCalledWith({ mode: 'days', days: 7 })
    expect(screen.getByRole('button', { name: '7 días' })).toHaveAttribute(
      'aria-pressed',
      'true',
    )
  })
})

describe('Acceso desde el panel del comerciante', () => {
  it('enlaza a la página de estadísticas y ya no muestra "Próximamente"', async () => {
    sessionStorage.setItem(TOKEN_KEY, 'token-merchant')
    mockedGetCurrentUser.mockResolvedValue(MERCHANT_USER)

    renderPanel()

    expect(
      await screen.findByRole('heading', { name: 'Panel del comerciante' }),
    ).toBeInTheDocument()

    expect(
      screen.getByRole('link', { name: /estadísticas/i }),
    ).toHaveAttribute('href', '/comerciante/estadisticas')
    expect(screen.queryByText('Próximamente')).not.toBeInTheDocument()
  })
})
