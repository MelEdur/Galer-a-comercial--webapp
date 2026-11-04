import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  getProductDetail,
  getSimilarProducts,
} from '../features/product-detail/api'
import { ProductDetailPage } from '../features/product-detail/ProductDetailPage'
import type { ProductDetail, StoreDetail } from '../features/product-detail/types'
import { ProductCard } from '../features/product-search/ProductCard'
import type {
  PublicCategory,
  PublicProduct,
} from '../features/product-search/types'
import { ApiError } from '../lib/http'

vi.mock('../features/product-detail/api')

const mockedGetProductDetail = vi.mocked(getProductDetail)
const mockedGetSimilarProducts = vi.mocked(getSimilarProducts)

const CATEGORY: PublicCategory = { id: 1, name: 'Indumentaria' }

const STORE: StoreDetail = {
  id: 1,
  number: 2,
  name: 'Boutique Centro',
  logo_url: 'https://images.test/logo.png',
  email: 'local@galeria.local',
  phone: '1122334455',
  whatsapp: '+54 11 2233-4455',
}

const DETAIL: ProductDetail = {
  id: 7,
  name: 'Remera',
  description: 'Algodón',
  price: '1500.00',
  offer_price: '1200.00',
  effective_price: '1200.00',
  categories: [CATEGORY],
  images: [
    {
      id: 1,
      url: 'https://images.test/frente.jpg',
      alt_text: 'Frente',
      position: 0,
      is_primary: true,
    },
    {
      id: 2,
      url: 'https://images.test/dorso.jpg',
      alt_text: 'Dorso',
      position: 1,
      is_primary: false,
    },
  ],
  store: STORE,
}

const SIMILAR_PRODUCT: PublicProduct = {
  id: 8,
  name: 'Pantalón',
  description: null,
  price: '2000.00',
  offer_price: null,
  effective_price: '2000.00',
  categories: [],
  primary_image: null,
  store: { id: 1, number: 2, name: 'Boutique Centro' },
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

function renderDetailPage(productId = '7') {
  return render(
    <QueryClientProvider client={createQueryClient()}>
      <MemoryRouter initialEntries={[`/productos/${productId}`]}>
        <Routes>
          <Route path="/productos/:productId" element={<ProductDetailPage />} />
          <Route path="/buscar" element={<h1>Buscador</h1>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function renderProductCard(product: PublicProduct) {
  return render(
    <MemoryRouter>
      <ProductCard product={product} />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  mockedGetProductDetail.mockResolvedValue(DETAIL)
  mockedGetSimilarProducts.mockResolvedValue({ items: [] })
})

afterEach(() => {
  vi.clearAllMocks()
})

describe('Detalle público del producto', () => {
  it('muestra imágenes, oferta, categorías, local y contacto', async () => {
    renderDetailPage()

    expect(
      await screen.findByRole('heading', { name: 'Remera' }),
    ).toBeInTheDocument()
    expect(screen.getByText('Algodón')).toBeInTheDocument()
    expect(screen.getByText(/1\.500,00/)).toBeInTheDocument()
    expect(screen.getByText(/1\.200,00/)).toBeInTheDocument()
    expect(screen.getByText('Oferta')).toBeInTheDocument()
    expect(screen.getByText('Indumentaria')).toBeInTheDocument()

    expect(screen.getByAltText('Frente')).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Ver imagen 2 de Remera' }),
    ).toBeInTheDocument()

    expect(screen.getByText('Local 2')).toBeInTheDocument()
    expect(screen.getByText('Boutique Centro')).toBeInTheDocument()
    expect(screen.getByAltText('Logo de Boutique Centro')).toBeInTheDocument()

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
  })

  it('muestra "Sin imagen" cuando el producto no tiene imágenes', async () => {
    mockedGetProductDetail.mockResolvedValue({ ...DETAIL, images: [] })

    renderDetailPage()

    expect(await screen.findByText('Sin imagen')).toBeInTheDocument()
    expect(screen.getByText('Algodón')).toBeInTheDocument()
  })

  it('renderiza los similares y enlaza cada uno a su detalle', async () => {
    mockedGetSimilarProducts.mockResolvedValue({ items: [SIMILAR_PRODUCT] })

    renderDetailPage()

    expect(
      await screen.findByRole('heading', { name: 'Productos similares' }),
    ).toBeInTheDocument()

    const similarName = await screen.findByText('Pantalón')
    expect(similarName.closest('a')).toHaveAttribute('href', '/productos/8')
  })

  it('no renderiza la sección de similares cuando la lista está vacía', async () => {
    mockedGetSimilarProducts.mockResolvedValue({ items: [] })

    renderDetailPage()

    await screen.findByRole('heading', { name: 'Remera' })
    expect(
      screen.queryByRole('heading', { name: 'Productos similares' }),
    ).not.toBeInTheDocument()
  })

  it('muestra el estado de carga', () => {
    mockedGetProductDetail.mockReturnValue(new Promise<ProductDetail>(() => {}))

    renderDetailPage()

    expect(screen.getByText('Cargando producto…')).toBeInTheDocument()
  })

  it('muestra un error genérico cuando la consulta falla', async () => {
    mockedGetProductDetail.mockRejectedValue(
      new ApiError(500, 'No se pudo cargar el producto.'),
    )

    renderDetailPage()

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/no se ha podido cargar el producto/i)
    expect(mockedGetSimilarProducts).not.toHaveBeenCalled()
  })

  it('muestra producto no encontrado con enlace al buscador en un 404', async () => {
    mockedGetProductDetail.mockRejectedValue(
      new ApiError(404, 'Producto no encontrado.'),
    )

    renderDetailPage()

    expect(
      await screen.findByRole('heading', { name: 'Producto no encontrado' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Volver al buscador' }),
    ).toHaveAttribute('href', '/buscar')
    expect(mockedGetSimilarProducts).not.toHaveBeenCalled()
  })
})

describe('Tarjeta de búsqueda', () => {
  it('enlaza toda la tarjeta a /productos/{id}', () => {
    renderProductCard(SIMILAR_PRODUCT)

    const link = screen.getByRole('link', { name: /Pantalón/ })
    expect(link).toHaveAttribute('href', '/productos/8')
    expect(
      screen.getByRole('heading', { name: 'Pantalón' }),
    ).toBeInTheDocument()
  })
})
