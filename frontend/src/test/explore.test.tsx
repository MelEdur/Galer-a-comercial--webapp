import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { getExplore } from '../features/explore/api'
import { ExplorePage } from '../features/explore/ExplorePage'
import type { ExploreResponse } from '../features/explore/types'
import {
  listPublicCategories,
  searchProducts,
} from '../features/product-search/api'
import { SearchPage } from '../features/product-search/SearchPage'
import type {
  PaginatedPublicProducts,
  PublicCategory,
  PublicProduct,
} from '../features/product-search/types'
import { ApiError } from '../lib/http'

vi.mock('../features/explore/api')
vi.mock('../features/product-search/api')

const mockedGetExplore = vi.mocked(getExplore)
const mockedSearchProducts = vi.mocked(searchProducts)
const mockedListPublicCategories = vi.mocked(listPublicCategories)

const CATEGORY: PublicCategory = { id: 1, name: 'Indumentaria' }

const FEATURED_PRODUCT: PublicProduct = {
  id: 10,
  name: 'Campera destacada',
  description: 'Abrigo',
  price: '5000.00',
  offer_price: null,
  effective_price: '5000.00',
  categories: [CATEGORY],
  primary_image: null,
  store: { id: 1, number: 2, name: 'Boutique Centro' },
}

const OFFER_PRODUCT: PublicProduct = {
  id: 20,
  name: 'Remera en oferta',
  description: null,
  price: '1500.00',
  offer_price: '1200.00',
  effective_price: '1200.00',
  categories: [CATEGORY],
  primary_image: null,
  store: { id: 2, number: 5, name: 'Local de ropa' },
}

function buildExplore(overrides: Partial<ExploreResponse> = {}): ExploreResponse {
  return {
    featured: [FEATURED_PRODUCT],
    offers: [OFFER_PRODUCT],
    categories: [{ id: 1, name: 'Indumentaria', product_count: 12 }],
    stores: [
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
    ],
    ...overrides,
  }
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

function LocationDisplay() {
  const location = useLocation()
  return <p data-testid="location">{location.search}</p>
}

function renderExplorePage() {
  return render(
    <QueryClientProvider client={createQueryClient()}>
      <MemoryRouter initialEntries={['/explorar']}>
        <Routes>
          <Route path="/explorar" element={<ExplorePage />} />
          <Route path="/buscar" element={<h1>Buscador</h1>} />
          <Route path="/productos/:productId" element={<h1>Producto</h1>} />
          <Route path="/locales/:storeId" element={<h1>Local</h1>} />
          <Route path="/locales" element={<h1>Locales</h1>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function renderSearchPage(initialEntry = '/buscar') {
  return render(
    <QueryClientProvider client={createQueryClient()}>
      <MemoryRouter initialEntries={[initialEntry]}>
        <Routes>
          <Route
            path="/buscar"
            element={
              <>
                <SearchPage />
                <LocationDisplay />
              </>
            }
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  mockedGetExplore.mockResolvedValue(buildExplore())
  mockedSearchProducts.mockResolvedValue(emptyPage())
  mockedListPublicCategories.mockResolvedValue([CATEGORY])
})

afterEach(() => {
  vi.clearAllMocks()
})

describe('Página de exploración', () => {
  it('muestra destacados, ofertas, categorías y locales', async () => {
    renderExplorePage()

    expect(await screen.findByText('Campera destacada')).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Destacados' }),
    ).toBeInTheDocument()

    expect(screen.getByText('Remera en oferta')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Ofertas' })).toBeInTheDocument()

    const categoriesSection = screen
      .getByRole('heading', { name: 'Categorías' })
      .closest('section')
    expect(categoriesSection).not.toBeNull()
    expect(
      within(categoriesSection as HTMLElement).getByText('Indumentaria'),
    ).toBeInTheDocument()
    expect(
      within(categoriesSection as HTMLElement).getByText('12 productos'),
    ).toBeInTheDocument()

    expect(await screen.findByText('Local Uno')).toBeInTheDocument()
    expect(screen.getByText('Local Dos')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Locales' })).toBeInTheDocument()
  })

  it('enlaza los productos a su detalle', async () => {
    renderExplorePage()

    const featured = await screen.findByText('Campera destacada')
    expect(featured.closest('a')).toHaveAttribute('href', '/productos/10')

    const offer = screen.getByText('Remera en oferta')
    expect(offer.closest('a')).toHaveAttribute('href', '/productos/20')
  })

  it('enlaza a todas las ofertas con has_offer=true', async () => {
    renderExplorePage()

    expect(
      await screen.findByRole('link', { name: 'Ver todas las ofertas' }),
    ).toHaveAttribute('href', '/buscar?has_offer=true')
  })

  it('enlaza los productos y locales a sus listados completos', async () => {
    renderExplorePage()

    expect(
      await screen.findByRole('link', { name: 'Ver todos los productos' }),
    ).toHaveAttribute('href', '/buscar')
    expect(
      screen.getByRole('link', { name: 'Ver todos los locales' }),
    ).toHaveAttribute('href', '/locales')
  })

  it('enlaza cada categoría al buscador filtrado', async () => {
    renderExplorePage()

    const categoriesSection = (
      await screen.findByRole('heading', { name: 'Categorías' })
    ).closest('section')
    expect(categoriesSection).not.toBeNull()

    expect(
      within(categoriesSection as HTMLElement).getByRole('link', {
        name: /Indumentaria/,
      }),
    ).toHaveAttribute('href', '/buscar?category=1')
  })

  it('enlaza cada local a su ficha', async () => {
    renderExplorePage()

    await screen.findByText('Local Uno')
    const storesSection = screen
      .getByRole('heading', { name: 'Locales' })
      .closest('section')
    expect(storesSection).not.toBeNull()

    const storeLinks = within(storesSection as HTMLElement).getAllByRole('link')
    const localUno = storeLinks.find((link) =>
      link.textContent?.includes('Local Uno'),
    )
    expect(localUno).toHaveAttribute('href', '/locales/1')
  })

  it('muestra el estado de carga', () => {
    mockedGetExplore.mockReturnValue(new Promise<ExploreResponse>(() => {}))

    renderExplorePage()

    expect(screen.getByText('Cargando exploración…')).toBeInTheDocument()
  })

  it('muestra un error sin romper la página', async () => {
    mockedGetExplore.mockRejectedValue(
      new ApiError(500, 'No se pudo cargar la exploración.'),
    )

    renderExplorePage()

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/no se ha podido cargar la exploración/i)
    expect(
      screen.getByRole('heading', { name: 'Explora la galería' }),
    ).toBeInTheDocument()
  })

  it('maneja secciones vacías sin romper la página', async () => {
    mockedGetExplore.mockResolvedValue(
      buildExplore({ featured: [], offers: [], categories: [], stores: [] }),
    )

    renderExplorePage()

    expect(
      await screen.findByText('Todavía no hay productos destacados.'),
    ).toBeInTheDocument()
    expect(
      screen.getByText('No hay ofertas disponibles por ahora.'),
    ).toBeInTheDocument()
    expect(screen.getByText('No hay categorías disponibles.')).toBeInTheDocument()
    expect(screen.getByText('No hay locales disponibles.')).toBeInTheDocument()
  })
})

describe('Filtro de ofertas en el buscador', () => {
  it('envía has_offer y actualiza la URL al marcar "Solo ofertas"', async () => {
    renderSearchPage('/buscar?page=2')

    const checkbox = await screen.findByLabelText('Solo ofertas')
    expect(checkbox).not.toBeChecked()

    fireEvent.click(checkbox)

    await waitFor(() =>
      expect(
        mockedSearchProducts.mock.calls.some(
          ([filters]) => filters.hasOffer === true && filters.page === 1,
        ),
      ).toBe(true),
    )

    await waitFor(() =>
      expect(screen.getByTestId('location')).toHaveTextContent('has_offer=true'),
    )
    expect(screen.getByTestId('location')).not.toHaveTextContent('page=2')
  })

  it('lee has_offer de la URL y marca el checkbox', async () => {
    renderSearchPage('/buscar?has_offer=true')

    const checkbox = await screen.findByLabelText('Solo ofertas')
    expect(checkbox).toBeChecked()

    await waitFor(() =>
      expect(
        mockedSearchProducts.mock.calls.some(
          ([filters]) => filters.hasOffer === true,
        ),
      ).toBe(true),
    )
  })
})
