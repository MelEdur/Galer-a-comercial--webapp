import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import type { ReactElement } from 'react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  createProduct,
  deleteProduct,
  getProduct,
  listCategories,
  listProducts,
  restoreProduct,
  updateProduct,
} from '../features/merchant-catalog/api'
import { ProductFormPage } from '../features/merchant-catalog/ProductFormPage'
import { ProductListPage } from '../features/merchant-catalog/ProductListPage'
import type {
  Category,
  PaginatedProducts,
  Product,
} from '../features/merchant-catalog/types'
import { ApiError } from '../lib/http'

vi.mock('../features/merchant-catalog/api')

const mockedListProducts = vi.mocked(listProducts)
const mockedGetProduct = vi.mocked(getProduct)
const mockedCreateProduct = vi.mocked(createProduct)
const mockedUpdateProduct = vi.mocked(updateProduct)
const mockedDeleteProduct = vi.mocked(deleteProduct)
const mockedRestoreProduct = vi.mocked(restoreProduct)
const mockedListCategories = vi.mocked(listCategories)

const CATEGORY: Category = { id: 1, name: 'Indumentaria' }

const PRODUCT: Product = {
  id: 7,
  name: 'Remera',
  description: null,
  price: '1500.00',
  offer_price: '1200.00',
  categories: [CATEGORY],
  images: [
    {
      id: 1,
      url: 'https://images.test/remera.jpg',
      alt_text: null,
      position: 0,
      is_primary: true,
    },
  ],
  is_active: true,
  deleted_at: null,
  created_at: '2026-01-01T00:00:00',
  updated_at: '2026-01-01T00:00:00',
}

const DELETED_PRODUCT: Product = {
  ...PRODUCT,
  id: 8,
  name: 'Pantalón',
  is_active: false,
  deleted_at: '2026-02-01T00:00:00',
}

function emptyPage(): PaginatedProducts {
  return { items: [], total: 0, page: 1, page_size: 20, pages: 1 }
}

function pageOf(items: Product[]): PaginatedProducts {
  return {
    items,
    total: items.length,
    page: 1,
    page_size: 20,
    pages: items.length > 0 ? 1 : 1,
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

function renderWithProviders(
  ui: ReactElement,
  initialEntries: string[] = ['/'],
) {
  return render(
    <QueryClientProvider client={createQueryClient()}>
      <MemoryRouter initialEntries={initialEntries}>{ui}</MemoryRouter>
    </QueryClientProvider>,
  )
}

function renderFormFlow(initialEntry: string) {
  return renderWithProviders(
    <Routes>
      <Route path="/comerciante/productos" element={<h1>Listado de productos</h1>} />
      <Route path="/comerciante/productos/nuevo" element={<ProductFormPage />} />
      <Route
        path="/comerciante/productos/:productId/editar"
        element={<ProductFormPage />}
      />
    </Routes>,
    [initialEntry],
  )
}

async function fillBaseFields({
  name = 'Remera nueva',
  price = '1500.00',
  offer = '',
}: { name?: string; price?: string; offer?: string } = {}) {
  fireEvent.change(await screen.findByLabelText('Nombre'), {
    target: { value: name },
  })
  fireEvent.change(screen.getByLabelText('Precio'), { target: { value: price } })

  if (offer.length > 0) {
    fireEvent.change(screen.getByLabelText('Precio de oferta'), {
      target: { value: offer },
    })
  }
}

beforeEach(() => {
  vi.clearAllMocks()
  mockedListCategories.mockResolvedValue([CATEGORY])
  mockedListProducts.mockResolvedValue(emptyPage())
})

afterEach(() => {
  vi.clearAllMocks()
})

describe('Listado del catálogo', () => {
  it('muestra los productos con sus datos y acciones', async () => {
    mockedListProducts.mockResolvedValue(pageOf([PRODUCT]))

    renderWithProviders(<ProductListPage />)

    expect(await screen.findByText('Remera')).toBeInTheDocument()
    expect(screen.getByText('Vigente')).toBeInTheDocument()
    expect(screen.getAllByText('Indumentaria').length).toBeGreaterThan(0)
    expect(screen.getByRole('link', { name: 'Editar' })).toHaveAttribute(
      'href',
      '/comerciante/productos/7/editar',
    )
    expect(screen.getByRole('button', { name: 'Dar de baja' })).toBeInTheDocument()
    expect(mockedListProducts).toHaveBeenCalledWith(
      expect.objectContaining({ status: 'active', page: 1 }),
    )
  })

  it('muestra un estado vacío cuando no hay productos', async () => {
    mockedListProducts.mockResolvedValue(emptyPage())

    renderWithProviders(<ProductListPage />)

    expect(
      await screen.findByText(/no hay productos que coincidan con los filtros/i),
    ).toBeInTheDocument()
  })

  it('actualiza la petición al buscar y filtrar por estado y categoría', async () => {
    renderWithProviders(<ProductListPage />)

    const searchInput = await screen.findByLabelText('Buscar productos')
    fireEvent.change(searchInput, { target: { value: 'reme' } })

    await waitFor(
      () =>
        expect(
          mockedListProducts.mock.calls.some(
            ([filters]) => filters.search === 'reme',
          ),
        ).toBe(true),
      { timeout: 2000 },
    )

    const statusSelect = screen.getByLabelText('Estado')
    fireEvent.change(statusSelect, { target: { value: 'deleted' } })

    await waitFor(
      () =>
        expect(
          mockedListProducts.mock.calls.some(
            ([filters]) => filters.status === 'deleted',
          ),
        ).toBe(true),
      { timeout: 2000 },
    )

    const categorySelect = await screen.findByLabelText('Categoría')
    await screen.findByRole('option', { name: 'Indumentaria' })
    fireEvent.change(categorySelect, { target: { value: '1' } })

    await waitFor(
      () =>
        expect(
          mockedListProducts.mock.calls.some(
            ([filters]) => filters.categoryId === 1,
          ),
        ).toBe(true),
      { timeout: 2000 },
    )
  })
})

describe('Alta de producto', () => {
  it('envía el payload correcto y vuelve al listado', async () => {
    mockedCreateProduct.mockResolvedValue(PRODUCT)

    renderFormFlow('/comerciante/productos/nuevo')

    await fillBaseFields()
    fireEvent.click(await screen.findByLabelText('Indumentaria'))
    fireEvent.click(screen.getByRole('button', { name: 'Crear producto' }))

    await waitFor(() => expect(mockedCreateProduct).toHaveBeenCalledTimes(1))
    expect(mockedCreateProduct.mock.calls[0][0]).toEqual({
      name: 'Remera nueva',
      price: '1500.00',
      category_ids: [1],
      images: [],
    })
    expect(
      await screen.findByRole('heading', { name: 'Listado de productos' }),
    ).toBeInTheDocument()
  })
})

describe('Edición de producto', () => {
  it('carga el producto, guarda los cambios y vuelve al listado', async () => {
    mockedGetProduct.mockResolvedValue(PRODUCT)
    mockedUpdateProduct.mockResolvedValue({ ...PRODUCT, price: '1600.00' })

    renderFormFlow('/comerciante/productos/7/editar')

    await waitFor(() =>
      expect(screen.getByLabelText('Nombre')).toHaveValue('Remera'),
    )
    expect(screen.getByLabelText('Precio')).toHaveValue('1500.00')
    expect(screen.getByLabelText('Precio de oferta')).toHaveValue('1200.00')

    fireEvent.change(screen.getByLabelText('Precio'), {
      target: { value: '1600.00' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Guardar cambios' }))

    await waitFor(() => expect(mockedUpdateProduct).toHaveBeenCalledTimes(1))
    expect(mockedUpdateProduct.mock.calls[0][0]).toBe(7)
    expect(mockedUpdateProduct.mock.calls[0][1]).toMatchObject({
      name: 'Remera',
      price: '1600.00',
      category_ids: [1],
    })
    expect(
      await screen.findByRole('heading', { name: 'Listado de productos' }),
    ).toBeInTheDocument()
  })

  it('muestra el error 409 al intentar editar un producto eliminado', async () => {
    mockedGetProduct.mockResolvedValue(DELETED_PRODUCT)
    mockedUpdateProduct.mockRejectedValue(
      new ApiError(409, 'El producto está eliminado.'),
    )

    renderFormFlow('/comerciante/productos/8/editar')

    await waitFor(() =>
      expect(screen.getByLabelText('Nombre')).toHaveValue('Pantalón'),
    )
    fireEvent.click(screen.getByRole('button', { name: 'Guardar cambios' }))

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/no se puede editar un producto eliminado/i)
    expect(screen.queryByRole('heading', { name: 'Listado de productos' })).not.toBeInTheDocument()
  })
})

describe('Baja de producto', () => {
  it('pide confirmación, da de baja e invalida el listado', async () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)
    mockedListProducts.mockResolvedValue(pageOf([PRODUCT]))
    mockedDeleteProduct.mockResolvedValue(undefined)

    renderWithProviders(<ProductListPage />)

    const deleteButton = await screen.findByRole('button', { name: 'Dar de baja' })
    fireEvent.click(deleteButton)

    expect(confirmSpy).toHaveBeenCalledTimes(1)
    await waitFor(() => expect(mockedDeleteProduct).toHaveBeenCalledWith(7))
    await waitFor(() =>
      expect(mockedListProducts.mock.calls.length).toBeGreaterThanOrEqual(2),
    )

    confirmSpy.mockRestore()
  })

  it('no da de baja si el comerciante cancela la confirmación', async () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false)
    mockedListProducts.mockResolvedValue(pageOf([PRODUCT]))

    renderWithProviders(<ProductListPage />)

    fireEvent.click(await screen.findByRole('button', { name: 'Dar de baja' }))

    expect(mockedDeleteProduct).not.toHaveBeenCalled()
    confirmSpy.mockRestore()
  })
})

describe('Restauración de producto', () => {
  it('muestra "Restaurar" y no "Editar" en un producto eliminado', async () => {
    mockedListProducts.mockResolvedValue(pageOf([DELETED_PRODUCT]))

    renderWithProviders(<ProductListPage />)

    expect(await screen.findByText('Pantalón')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Restaurar' })).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Editar' })).not.toBeInTheDocument()
  })

  it('pide confirmación, restaura e invalida el listado', async () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)
    mockedListProducts.mockResolvedValue(pageOf([DELETED_PRODUCT]))
    mockedRestoreProduct.mockResolvedValue({
      ...DELETED_PRODUCT,
      is_active: true,
      deleted_at: null,
    })

    renderWithProviders(<ProductListPage />)

    fireEvent.click(await screen.findByRole('button', { name: 'Restaurar' }))

    expect(confirmSpy).toHaveBeenCalledTimes(1)
    await waitFor(() => expect(mockedRestoreProduct).toHaveBeenCalledWith(8))
    await waitFor(() =>
      expect(mockedListProducts.mock.calls.length).toBeGreaterThanOrEqual(2),
    )

    confirmSpy.mockRestore()
  })

  it('no restaura si el comerciante cancela la confirmación', async () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false)
    mockedListProducts.mockResolvedValue(pageOf([DELETED_PRODUCT]))

    renderWithProviders(<ProductListPage />)

    fireEvent.click(await screen.findByRole('button', { name: 'Restaurar' }))

    expect(mockedRestoreProduct).not.toHaveBeenCalled()
    confirmSpy.mockRestore()
  })
})

describe('Validación local del formulario', () => {
  it('exige al menos una categoría', async () => {
    renderFormFlow('/comerciante/productos/nuevo')

    await fillBaseFields()
    fireEvent.click(screen.getByRole('button', { name: 'Crear producto' }))

    expect(
      await screen.findByText(/selecciona al menos una categoría/i),
    ).toBeInTheDocument()
    expect(mockedCreateProduct).not.toHaveBeenCalled()
  })

  it('rechaza una oferta mayor o igual que el precio', async () => {
    renderFormFlow('/comerciante/productos/nuevo')

    await fillBaseFields({ price: '100.00', offer: '150.00' })
    fireEvent.click(await screen.findByLabelText('Indumentaria'))
    fireEvent.click(screen.getByRole('button', { name: 'Crear producto' }))

    expect(
      await screen.findByText(/precio de oferta debe ser menor que el precio/i),
    ).toBeInTheDocument()
    expect(mockedCreateProduct).not.toHaveBeenCalled()
  })

  it('rechaza más de cinco imágenes', async () => {
    renderFormFlow('/comerciante/productos/nuevo')

    await fillBaseFields()
    fireEvent.click(await screen.findByLabelText('Indumentaria'))

    const addButton = screen.getByRole('button', { name: 'Agregar imagen' })
    for (let index = 0; index < 6; index += 1) {
      fireEvent.click(addButton)
    }

    for (let index = 1; index <= 6; index += 1) {
      fireEvent.change(screen.getByLabelText(`URL de la imagen ${index}`), {
        target: { value: `https://images.test/${index}.jpg` },
      })
    }

    fireEvent.click(screen.getByRole('button', { name: 'Crear producto' }))

    expect(
      await screen.findByText(/como máximo 5 imágenes/i),
    ).toBeInTheDocument()
    expect(mockedCreateProduct).not.toHaveBeenCalled()
  })
})
