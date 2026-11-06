import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  getProductDetail,
  getSimilarProducts,
} from '../features/product-detail/api'
import { ProductDetailPage } from '../features/product-detail/ProductDetailPage'
import type { ProductDetail } from '../features/product-detail/types'
import type {
  PaginatedPublicProducts,
  PublicProduct,
} from '../features/product-search/types'
import {
  getStoreDetail,
  listStoreProducts,
} from '../features/store-detail/api'
import { StoreDetailPage } from '../features/store-detail/StoreDetailPage'
import type { StoreDetail } from '../features/store-detail/types'
import { ApiError } from '../lib/http'

vi.mock('../features/store-detail/api')
vi.mock('../features/product-detail/api')

const mockedGetStoreDetail = vi.mocked(getStoreDetail)
const mockedListStoreProducts = vi.mocked(listStoreProducts)
const mockedGetProductDetail = vi.mocked(getProductDetail)
const mockedGetSimilarProducts = vi.mocked(getSimilarProducts)

const FULL_STORE: StoreDetail = {
  id: 1,
  number: 2,
  name: 'Local 2',
  description: 'Ropa y accesorios',
  logo_url: 'https://images.test/local.png',
  email: 'local@galeria.local',
  phone: '1122334455',
  whatsapp: '+54 11 2233-4455',
  hours: [
    { day_of_week: 0, opens_at: '09:00:00', closes_at: '13:00:00' },
    { day_of_week: 0, opens_at: '15:00:00', closes_at: '19:00:00' },
    { day_of_week: 2, opens_at: '10:00:00', closes_at: '18:00:00' },
  ],
  links: [
    { label: 'Instagram', url: 'https://instagram.com/local', position: 1 },
    { label: 'Sitio web', url: 'https://local.test', position: 0 },
  ],
}

const MINIMAL_STORE: StoreDetail = {
  id: 3,
  number: 5,
  name: 'Local vacío',
  description: null,
  logo_url: null,
  email: null,
  phone: null,
  whatsapp: null,
  hours: [],
  links: [],
}

const CATALOG_PRODUCT: PublicProduct = {
  id: 11,
  name: 'Zapatilla',
  description: 'Cuero',
  price: '100.00',
  offer_price: null,
  effective_price: '100.00',
  categories: [{ id: 1, name: 'Calzado' }],
  primary_image: null,
  store: { id: 1, number: 2, name: 'Local 2' },
}

const EMPTY_PRODUCTS: PaginatedPublicProducts = {
  items: [],
  total: 0,
  page: 1,
  page_size: 12,
  pages: 0,
}

const PRODUCT_DETAIL: ProductDetail = {
  id: 7,
  name: 'Remera',
  description: null,
  price: '1500.00',
  offer_price: null,
  effective_price: '1500.00',
  categories: [],
  images: [],
  store: {
    id: 1,
    number: 2,
    name: 'Boutique Centro',
    logo_url: null,
    email: null,
    phone: null,
    whatsapp: null,
  },
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

function renderStorePage(storeId = '1') {
  return render(
    <QueryClientProvider client={createQueryClient()}>
      <MemoryRouter initialEntries={[`/locales/${storeId}`]}>
        <Routes>
          <Route path="/" element={<h1>Inicio</h1>} />
          <Route path="/locales/:storeId" element={<StoreDetailPage />} />
          <Route path="/buscar" element={<h1>Buscador</h1>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function renderStorePageHistory(initialEntries: string[], initialIndex = 0) {
  return render(
    <QueryClientProvider client={createQueryClient()}>
      <MemoryRouter initialEntries={initialEntries} initialIndex={initialIndex}>
        <Routes>
          <Route path="/" element={<h1>Inicio</h1>} />
          <Route path="/locales/:storeId" element={<StoreDetailPage />} />
          <Route path="/buscar" element={<h1>Buscador</h1>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function renderProductDetailPage(productId = '7') {
  return render(
    <QueryClientProvider client={createQueryClient()}>
      <MemoryRouter initialEntries={[`/productos/${productId}`]}>
        <Routes>
          <Route path="/" element={<h1>Inicio</h1>} />
          <Route path="/productos/:productId" element={<ProductDetailPage />} />
          <Route path="/locales/:storeId" element={<h1>Ficha del local</h1>} />
          <Route path="/buscar" element={<h1>Buscador</h1>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function renderProductDetailPageHistory(
  initialEntries: string[],
  initialIndex = 0,
) {
  return render(
    <QueryClientProvider client={createQueryClient()}>
      <MemoryRouter initialEntries={initialEntries} initialIndex={initialIndex}>
        <Routes>
          <Route path="/" element={<h1>Inicio</h1>} />
          <Route path="/productos/:productId" element={<ProductDetailPage />} />
          <Route path="/locales/:storeId" element={<h1>Ficha del local</h1>} />
          <Route path="/buscar" element={<h1>Buscador</h1>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  mockedGetStoreDetail.mockResolvedValue(FULL_STORE)
  mockedListStoreProducts.mockResolvedValue(EMPTY_PRODUCTS)
  mockedGetProductDetail.mockResolvedValue(PRODUCT_DETAIL)
  mockedGetSimilarProducts.mockResolvedValue({ items: [] })
})

afterEach(() => {
  vi.clearAllMocks()
})

describe('Ficha pública del local', () => {
  it('muestra logo, datos generales, horarios, contacto y enlaces', async () => {
    renderStorePage()

    expect(
      await screen.findByRole('heading', { name: 'Local 2' }),
    ).toBeInTheDocument()
    expect(screen.getByText('Ropa y accesorios')).toBeInTheDocument()
    expect(screen.getByAltText('Logo de Local 2')).toHaveAttribute(
      'src',
      'https://images.test/local.png',
    )

    expect(
      screen.getByRole('heading', { name: 'Horarios' }),
    ).toBeInTheDocument()
    expect(
      screen.getByText('09:00 - 13:00 · 15:00 - 19:00'),
    ).toBeInTheDocument()
    expect(screen.getByText('10:00 - 18:00')).toBeInTheDocument()

    expect(
      screen.getByRole('heading', { name: 'Contacto' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'local@galeria.local' }),
    ).toHaveAttribute('href', 'mailto:local@galeria.local')
    expect(screen.getByRole('link', { name: '1122334455' })).toHaveAttribute(
      'href',
      'tel:1122334455',
    )
    expect(
      screen.getByRole('link', { name: 'WhatsApp: +54 11 2233-4455' }),
    ).toHaveAttribute('href', 'https://wa.me/541122334455')

    const linksSection = screen
      .getByRole('heading', { name: 'Enlaces' })
      .closest('section')
    expect(linksSection).not.toBeNull()

    const externalLinks = within(linksSection as HTMLElement).getAllByRole(
      'link',
    )
    expect(externalLinks.map((link) => link.textContent)).toEqual([
      'Sitio web',
      'Instagram',
    ])
    expect(externalLinks[0]).toHaveAttribute('target', '_blank')
    expect(externalLinks[0]).toHaveAttribute('rel', 'noreferrer')
  })

  it('muestra "Cerrado" en los días sin tramos horarios', async () => {
    renderStorePage()

    await screen.findByRole('heading', { name: 'Local 2' })

    expect(screen.getAllByText('Cerrado')).toHaveLength(5)
    expect(screen.getByText('09:00 - 13:00 · 15:00 - 19:00')).toBeInTheDocument()
  })

  it('oculta las secciones sin datos y muestra el marcador sin logo', async () => {
    mockedGetStoreDetail.mockResolvedValue(MINIMAL_STORE)

    renderStorePage('3')

    expect(
      await screen.findByRole('heading', { name: 'Local vacío' }),
    ).toBeInTheDocument()
    expect(screen.getByText('Sin logo')).toBeInTheDocument()
    expect(
      screen.queryByRole('heading', { name: 'Horarios' }),
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('heading', { name: 'Contacto' }),
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('heading', { name: 'Enlaces' }),
    ).not.toBeInTheDocument()
  })

  it('cae al marcador cuando el logo no se puede cargar', async () => {
    renderStorePage()

    const logo = await screen.findByAltText('Logo de Local 2')
    fireEvent.error(logo)

    expect(screen.getByText('Sin logo')).toBeInTheDocument()
    expect(screen.queryByAltText('Logo de Local 2')).not.toBeInTheDocument()
  })

  it('muestra el estado de carga', () => {
    mockedGetStoreDetail.mockReturnValue(new Promise<StoreDetail>(() => {}))

    renderStorePage()

    expect(screen.getByText('Cargando local…')).toBeInTheDocument()
  })

  it('muestra un error genérico cuando la consulta falla', async () => {
    mockedGetStoreDetail.mockRejectedValue(
      new ApiError(500, 'No se pudo cargar el local.'),
    )

    renderStorePage()

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/no se ha podido cargar el local/i)
  })

  it('muestra local no encontrado con enlace al buscador en un 404', async () => {
    mockedGetStoreDetail.mockRejectedValue(
      new ApiError(404, 'Local no encontrado.'),
    )

    renderStorePage()

    expect(
      await screen.findByRole('heading', { name: 'Local no encontrado' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Volver al buscador' }),
    ).toHaveAttribute('href', '/buscar')
  })
})

describe('Integración con el detalle de producto', () => {
  it('enlaza el local a su ficha pública', async () => {
    renderProductDetailPage()

    await screen.findByRole('heading', { name: 'Remera' })

    const storeLink = screen.getByRole('link', { name: 'Boutique Centro' })
    expect(storeLink).toHaveAttribute('href', '/locales/1')
  })
})

describe('Catálogo del local', () => {
  it('muestra el catálogo debajo de los enlaces con sus productos', async () => {
    mockedListStoreProducts.mockResolvedValue({
      items: [CATALOG_PRODUCT],
      total: 1,
      page: 1,
      page_size: 12,
      pages: 1,
    })

    renderStorePage()

    await screen.findByRole('heading', { name: 'Local 2' })

    const catalogHeading = await screen.findByRole('heading', {
      name: 'Catálogo',
    })
    const catalogSection = catalogHeading.closest('section') as HTMLElement
    const linksSection = screen
      .getByRole('heading', { name: 'Enlaces' })
      .closest('section') as HTMLElement

    expect(
      linksSection.compareDocumentPosition(catalogSection) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy()

    expect(within(catalogSection).getByText('Zapatilla')).toBeInTheDocument()
    expect(within(catalogSection).getByText('Calzado')).toBeInTheDocument()

    const productLink = within(catalogSection).getByRole('link', {
      name: /Zapatilla/,
    })
    expect(productLink).toHaveAttribute('href', '/productos/11')

    expect(mockedListStoreProducts).toHaveBeenCalledWith('1', 1)
  })

  it('no repite el local en las tarjetas del catálogo', async () => {
    mockedListStoreProducts.mockResolvedValue({
      items: [CATALOG_PRODUCT],
      total: 1,
      page: 1,
      page_size: 12,
      pages: 1,
    })

    renderStorePage()

    const catalogHeading = await screen.findByRole('heading', {
      name: 'Catálogo',
    })
    const catalogSection = catalogHeading.closest('section') as HTMLElement

    expect(within(catalogSection).queryByText(/Local /)).not.toBeInTheDocument()
  })

  it('muestra el estado vacío cuando el local no tiene productos', async () => {
    renderStorePage()

    expect(
      await screen.findByText(
        'Este local todavía no tiene productos disponibles',
      ),
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Siguiente' }),
    ).not.toBeInTheDocument()
  })

  it('pagina el catálogo consultando la página siguiente', async () => {
    mockedListStoreProducts.mockImplementation((_storeId, page) =>
      Promise.resolve({
        items: [CATALOG_PRODUCT],
        total: 20,
        page,
        page_size: 12,
        pages: 2,
      }),
    )

    renderStorePage()

    await screen.findByText('Zapatilla')
    expect(await screen.findByText(/Página 1 de 2/)).toBeInTheDocument()

    const nextButton = screen.getByRole('button', { name: 'Siguiente' })
    expect(nextButton).toBeEnabled()
    fireEvent.click(nextButton)

    await waitFor(() =>
      expect(mockedListStoreProducts).toHaveBeenCalledWith('1', 2),
    )
    expect(await screen.findByText(/Página 2 de 2/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Anterior' })).toBeEnabled()
  })

  it('oculta la paginación cuando solo hay una página', async () => {
    mockedListStoreProducts.mockResolvedValue({
      items: [CATALOG_PRODUCT],
      total: 1,
      page: 1,
      page_size: 12,
      pages: 1,
    })

    renderStorePage()

    await screen.findByText('Zapatilla')
    expect(
      screen.queryByRole('button', { name: 'Siguiente' }),
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Anterior' }),
    ).not.toBeInTheDocument()
  })

  it('muestra un error cuando el catálogo falla', async () => {
    mockedListStoreProducts.mockRejectedValue(
      new ApiError(500, 'Catálogo no disponible.'),
    )

    renderStorePage()

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/no se ha podido cargar el catálogo/i)
  })
})

describe('Volver en la ficha del local', () => {
  it('regresa a la página de origen cuando hay historial interno', async () => {
    renderStorePageHistory(['/buscar', '/locales/1'], 1)

    await screen.findByRole('heading', { name: 'Local 2' })

    fireEvent.click(screen.getByRole('button', { name: 'Volver' }))

    expect(
      await screen.findByRole('heading', { name: 'Buscador' }),
    ).toBeInTheDocument()
  })

  it('navega a la portada cuando la entrada es directa', async () => {
    renderStorePage()

    await screen.findByRole('heading', { name: 'Local 2' })

    fireEvent.click(screen.getByRole('button', { name: 'Volver' }))

    expect(
      await screen.findByRole('heading', { name: 'Inicio' }),
    ).toBeInTheDocument()
  })

  it('expone un botón Volver accesible', async () => {
    renderStorePage()

    await screen.findByRole('heading', { name: 'Local 2' })

    const backButton = screen.getByRole('button', { name: 'Volver' })
    expect(backButton).toHaveTextContent('← Volver')
    expect(backButton).toHaveAttribute('type', 'button')
  })
})

describe('Volver en el detalle de producto', () => {
  it('regresa a la página de origen cuando hay historial interno', async () => {
    renderProductDetailPageHistory(['/buscar', '/productos/7'], 1)

    await screen.findByRole('heading', { name: 'Remera' })

    fireEvent.click(screen.getByRole('button', { name: 'Volver' }))

    expect(
      await screen.findByRole('heading', { name: 'Buscador' }),
    ).toBeInTheDocument()
  })

  it('navega a la portada cuando la entrada es directa', async () => {
    renderProductDetailPage()

    await screen.findByRole('heading', { name: 'Remera' })

    fireEvent.click(screen.getByRole('button', { name: 'Volver' }))

    expect(
      await screen.findByRole('heading', { name: 'Inicio' }),
    ).toBeInTheDocument()
  })

  it('mantiene el CTA al buscador en el estado no encontrado', async () => {
    mockedGetProductDetail.mockRejectedValue(
      new ApiError(404, 'Producto no encontrado.'),
    )

    renderProductDetailPageHistory(['/productos/7'])

    expect(
      await screen.findByRole('heading', { name: 'Producto no encontrado' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Volver al buscador' }),
    ).toHaveAttribute('href', '/buscar')
    expect(screen.getByRole('button', { name: 'Volver' })).toBeInTheDocument()
  })
})
