import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes, useNavigate } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
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

vi.mock('../features/product-search/api')

const mockedSearchProducts = vi.mocked(searchProducts)
const mockedListPublicCategories = vi.mocked(listPublicCategories)

const CATEGORY: PublicCategory = { id: 1, name: 'Indumentaria' }

const OFFER_PRODUCT: PublicProduct = {
  id: 7,
  name: 'Remera',
  description: 'Algodón',
  price: '1500.00',
  offer_price: '1200.00',
  effective_price: '1200.00',
  categories: [CATEGORY],
  primary_image: {
    url: 'https://images.test/remera.jpg',
    alt_text: null,
  },
  store: { id: 1, number: 2, name: 'Boutique Centro' },
}

const PLAIN_PRODUCT: PublicProduct = {
  id: 8,
  name: 'Pantalón',
  description: null,
  price: '2000.00',
  offer_price: null,
  effective_price: '2000.00',
  categories: [],
  primary_image: null,
  store: { id: 2, number: 5, name: 'Local de ropa' },
}

function emptyPage(): PaginatedPublicProducts {
  return { items: [], total: 0, page: 1, page_size: 20, pages: 1 }
}

function pageOf(
  items: PublicProduct[],
  overrides: Partial<PaginatedPublicProducts> = {},
): PaginatedPublicProducts {
  return {
    items,
    total: items.length,
    page: 1,
    page_size: 20,
    pages: 1,
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

function renderSearchPage(initialEntry = '/buscar') {
  return render(
    <QueryClientProvider client={createQueryClient()}>
      <MemoryRouter initialEntries={[initialEntry]}>
        <Routes>
          <Route path="/buscar" element={<SearchPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  mockedListPublicCategories.mockResolvedValue([CATEGORY])
  mockedSearchProducts.mockResolvedValue(emptyPage())
})

afterEach(() => {
  vi.clearAllMocks()
})

describe('Búsqueda pública de productos', () => {
  it('muestra resultados con nombre, precio y local', async () => {
    mockedSearchProducts.mockResolvedValue(pageOf([PLAIN_PRODUCT]))

    renderSearchPage()

    expect(await screen.findByText('Pantalón')).toBeInTheDocument()
    expect(screen.getByText(/2\.000,00/)).toBeInTheDocument()
    expect(screen.getByText(/Local 5 · Local de ropa/)).toBeInTheDocument()
  })

  it('muestra la oferta y el precio efectivo', async () => {
    mockedSearchProducts.mockResolvedValue(pageOf([OFFER_PRODUCT]))

    renderSearchPage()

    expect(await screen.findByText('Remera')).toBeInTheDocument()
    expect(screen.getByText(/1\.500,00/)).toBeInTheDocument()
    expect(screen.getByText(/1\.200,00/)).toBeInTheDocument()
    expect(screen.getByText('Oferta')).toBeInTheDocument()
  })

  it('actualiza la petición al buscar por nombre con debounce', async () => {
    renderSearchPage()

    fireEvent.change(await screen.findByLabelText('Buscar productos'), {
      target: { value: 'reme' },
    })

    await waitFor(
      () =>
        expect(
          mockedSearchProducts.mock.calls.some(([filters]) => filters.search === 'reme'),
        ).toBe(true),
      { timeout: 2000 },
    )
  })

  it('filtra por categoría y por precio actualizando la petición', async () => {
    renderSearchPage()

    const categorySelect = await screen.findByLabelText('Categoría')
    await screen.findByRole('option', { name: 'Indumentaria' })

    fireEvent.change(categorySelect, { target: { value: '1' } })

    await waitFor(
      () =>
        expect(
          mockedSearchProducts.mock.calls.some(
            ([filters]) => filters.categoryId === 1,
          ),
        ).toBe(true),
      { timeout: 2000 },
    )

    fireEvent.change(screen.getByLabelText('Precio mínimo'), {
      target: { value: '100' },
    })
    fireEvent.change(screen.getByLabelText('Precio máximo'), {
      target: { value: '500' },
    })

    await waitFor(
      () =>
        expect(
          mockedSearchProducts.mock.calls.some(
            ([filters]) => filters.minPrice === '100' && filters.maxPrice === '500',
          ),
        ).toBe(true),
      { timeout: 2000 },
    )
  })

  it('muestra el estado vacío cuando el catálogo no tiene productos', async () => {
    mockedSearchProducts.mockResolvedValue(emptyPage())

    renderSearchPage()

    expect(
      await screen.findByText(/todavía no hay productos/i),
    ).toBeInTheDocument()
  })

  it('distingue el vacío por filtros del catálogo vacío', async () => {
    mockedSearchProducts.mockResolvedValue(emptyPage())

    renderSearchPage('/buscar?search=inexistente')

    expect(
      await screen.findByText(/no hay productos que coincidan con tu búsqueda/i),
    ).toBeInTheDocument()
  })

  it('muestra el estado de error cuando la consulta falla', async () => {
    mockedSearchProducts.mockRejectedValue(
      new ApiError(500, 'No se pudo completar la búsqueda.'),
    )

    renderSearchPage()

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/no se han podido cargar los productos/i)
  })

  it('solicita la página siguiente al paginar', async () => {
    mockedSearchProducts.mockResolvedValue(
      pageOf([PLAIN_PRODUCT], { total: 45, page: 1, pages: 3 }),
    )

    renderSearchPage()

    const nextButton = await screen.findByRole('button', { name: 'Siguiente' })
    fireEvent.click(nextButton)

    await waitFor(() =>
      expect(
        mockedSearchProducts.mock.calls.some(([filters]) => filters.page === 2),
      ).toBe(true),
    )
  })

  it('sincroniza el término cuando la URL cambia externamente', async () => {
    function GoAudio() {
      const navigate = useNavigate()
      return (
        <button type="button" onClick={() => navigate('/buscar?search=audio')}>
          Ir a audio
        </button>
      )
    }

    render(
      <QueryClientProvider client={createQueryClient()}>
        <MemoryRouter initialEntries={['/buscar?search=zapatillas']}>
          <GoAudio />
          <Routes>
            <Route path="/buscar" element={<SearchPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    )

    const input = await screen.findByLabelText('Buscar productos')
    expect(input).toHaveValue('zapatillas')

    fireEvent.click(screen.getByRole('button', { name: 'Ir a audio' }))

    await waitFor(() => expect(input).toHaveValue('audio'))
    await waitFor(
      () =>
        expect(
          mockedSearchProducts.mock.calls.some(([filters]) => filters.search === 'audio'),
        ).toBe(true),
      { timeout: 2000 },
    )

    await new Promise((resolve) => setTimeout(resolve, 400))
    expect(input).toHaveValue('audio')
    const lastSearch = mockedSearchProducts.mock.calls.at(-1)?.[0].search
    expect(lastSearch).toBe('audio')
  })

  it('sin filtros muestra el catálogo completo de la primera página', async () => {
    mockedSearchProducts.mockResolvedValue(pageOf([PLAIN_PRODUCT]))

    renderSearchPage()

    expect(await screen.findByText('Pantalón')).toBeInTheDocument()
    expect(mockedSearchProducts).toHaveBeenCalledWith(
      expect.objectContaining({
        search: '',
        categoryId: null,
        minPrice: '',
        maxPrice: '',
        sort: 'name',
        page: 1,
      }),
    )
  })
})
