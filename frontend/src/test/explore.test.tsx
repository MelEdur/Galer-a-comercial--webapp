import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { getExplore } from '../features/explore/api'
import { ExploreContent } from '../features/explore/ExploreContent'
import type { ExploreResponse } from '../features/explore/types'
import { HomePage } from '../pages/HomePage'
import type { PublicCategory, PublicProduct } from '../features/product-search/types'
import { ApiError } from '../lib/http'

vi.mock('../features/explore/api')
vi.mock('../features/product-search/api')

const mockedGetExplore = vi.mocked(getExplore)
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

function renderExploreContent() {
  return render(
    <QueryClientProvider client={createQueryClient()}>
      <MemoryRouter initialEntries={['/']}>
        <ExploreContent />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function renderHomePage() {
  return render(
    <QueryClientProvider client={createQueryClient()}>
      <MemoryRouter initialEntries={['/']}>
        <HomePage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  mockedGetExplore.mockResolvedValue(buildExplore())
})

afterEach(() => {
  vi.clearAllMocks()
})

describe('Contenido de exploración', () => {
  it('muestra destacados, ofertas, categorías y locales', async () => {
    renderExploreContent()

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
    renderExploreContent()

    const featured = await screen.findByText('Campera destacada')
    expect(featured.closest('a')).toHaveAttribute('href', '/productos/10')

    const offer = screen.getByText('Remera en oferta')
    expect(offer.closest('a')).toHaveAttribute('href', '/productos/20')
  })

  it('enlaza a todas las ofertas con has_offer=true', async () => {
    renderExploreContent()

    expect(
      await screen.findByRole('link', { name: 'Ver todas las ofertas' }),
    ).toHaveAttribute('href', '/buscar?has_offer=true')
  })

  it('enlaza los productos y locales a sus listados completos', async () => {
    renderExploreContent()

    expect(
      await screen.findByRole('link', { name: 'Ver todos los productos' }),
    ).toHaveAttribute('href', '/buscar')
    expect(
      screen.getByRole('link', { name: 'Ver todos los locales' }),
    ).toHaveAttribute('href', '/locales')
  })

  it('enlaza cada categoría al buscador filtrado', async () => {
    renderExploreContent()

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
    renderExploreContent()

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

    renderExploreContent()

    expect(screen.getByText('Cargando exploración…')).toBeInTheDocument()
  })

  it('muestra un error sin romper la página', async () => {
    mockedGetExplore.mockRejectedValue(
      new ApiError(500, 'No se pudo cargar la exploración.'),
    )

    renderExploreContent()

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/no se ha podido cargar la exploración/i)
    expect(
      screen.queryByRole('heading', { name: 'Destacados' }),
    ).not.toBeInTheDocument()
  })

  it('maneja secciones vacías sin romper la página', async () => {
    mockedGetExplore.mockResolvedValue(
      buildExplore({ featured: [], offers: [], categories: [], stores: [] }),
    )

    renderExploreContent()

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

describe('Página principal', () => {
  it('muestra el acceso destacado al mapa', async () => {
    renderHomePage()

    expect(
      screen.getByRole('link', { name: 'Ver mapa de la galería' }),
    ).toHaveAttribute('href', '/mapa')

    await screen.findByText('Campera destacada')
  })

  it('muestra las secciones de exploración en la home', async () => {
    renderHomePage()

    expect(await screen.findByText('Campera destacada')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Destacados' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Ofertas' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Categorías' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Locales' })).toBeInTheDocument()
  })

  it('no muestra el estado técnico del backend', async () => {
    renderHomePage()

    await screen.findByText('Campera destacada')

    expect(screen.queryByText(/comprobando el estado del backend/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/backend operativo/i)).not.toBeInTheDocument()
  })
})
