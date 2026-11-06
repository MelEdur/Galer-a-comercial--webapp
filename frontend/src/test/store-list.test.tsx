import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { listPublicStores } from '../features/explore/api'
import { StoreListPage } from '../features/explore/StoreListPage'
import type { ExploreStore } from '../features/explore/types'
import { ApiError } from '../lib/http'

vi.mock('../features/explore/api')

const mockedListPublicStores = vi.mocked(listPublicStores)

const STORES: ExploreStore[] = [
  {
    id: 1,
    number: 1,
    name: 'Local Uno',
    description: 'Ropa',
    logo_url: null,
  },
  {
    id: 2,
    number: 2,
    name: 'Local Dos',
    description: null,
    logo_url: 'https://images.test/logo.png',
  },
  {
    id: 3,
    number: 3,
    name: 'Local Tres',
    description: 'Accesorios',
    logo_url: null,
  },
]

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

function renderStoreList() {
  return render(
    <QueryClientProvider client={createQueryClient()}>
      <MemoryRouter initialEntries={['/locales']}>
        <Routes>
          <Route path="/locales" element={<StoreListPage />} />
          <Route
            path="/locales/:storeId"
            element={<h1>Ficha del local</h1>}
          />
          <Route path="/explorar" element={<h1>Explorar</h1>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  mockedListPublicStores.mockResolvedValue(STORES)
})

afterEach(() => {
  vi.clearAllMocks()
})

describe('Listado público de locales', () => {
  it('muestra todos los locales con su número y nombre', async () => {
    renderStoreList()

    expect(
      await screen.findByRole('heading', { name: 'Locales' }),
    ).toBeInTheDocument()
    expect(await screen.findByText('Local Uno')).toBeInTheDocument()
    expect(screen.getByText('Local Dos')).toBeInTheDocument()
    expect(screen.getByText('Local Tres')).toBeInTheDocument()
    expect(screen.getByText('Ropa')).toBeInTheDocument()
    expect(screen.getByText('Accesorios')).toBeInTheDocument()
  })

  it('enlaza cada local a su ficha', async () => {
    renderStoreList()

    const link = (await screen.findByText('Local Dos')).closest('a')
    expect(link).toHaveAttribute('href', '/locales/2')
  })

  it('navega a la ficha al seleccionar un local', async () => {
    renderStoreList()

    const localUno = (await screen.findByText('Local Uno')).closest('a')
    expect(localUno).not.toBeNull()
    fireEvent.click(localUno as HTMLAnchorElement)

    expect(
      await screen.findByRole('heading', { name: 'Ficha del local' }),
    ).toBeInTheDocument()
  })

  it('muestra el estado de carga', () => {
    mockedListPublicStores.mockReturnValue(new Promise<ExploreStore[]>(() => {}))

    renderStoreList()

    expect(screen.getByText('Cargando locales…')).toBeInTheDocument()
  })

  it('muestra un error cuando la consulta falla', async () => {
    mockedListPublicStores.mockRejectedValue(
      new ApiError(500, 'No se pudieron cargar los locales.'),
    )

    renderStoreList()

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/no se han podido cargar los locales/i)
  })

  it('muestra el estado vacío sin locales', async () => {
    mockedListPublicStores.mockResolvedValue([])

    renderStoreList()

    expect(
      await screen.findByText(/todavía no hay locales disponibles/i),
    ).toBeInTheDocument()
  })

  it('permite volver a la exploración', async () => {
    renderStoreList()

    expect(
      await screen.findByRole('link', { name: '← Volver a explorar' }),
    ).toHaveAttribute('href', '/explorar')
  })
})
