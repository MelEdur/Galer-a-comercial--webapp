import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  createMerchant,
  deactivateMerchant,
  listAdminStores,
  listMerchants,
} from '../features/admin-merchants/api'
import { MerchantsPage } from '../features/admin-merchants/MerchantsPage'
import type { Merchant, StoreAdmin } from '../features/admin-merchants/types'
import { AuthProvider } from '../features/auth/AuthContext'
import { ApiError } from '../lib/http'

vi.mock('../features/admin-merchants/api')

const mockedListMerchants = vi.mocked(listMerchants)
const mockedListAdminStores = vi.mocked(listAdminStores)
const mockedCreateMerchant = vi.mocked(createMerchant)
const mockedDeactivateMerchant = vi.mocked(deactivateMerchant)

const OCCUPIED_STORE: StoreAdmin = {
  id: 1,
  number: 1,
  name: 'Local Uno',
  side: 'left',
  position: 1,
  is_active: true,
  merchant: { id: 10, full_name: 'Ana Pérez', email: 'ana@galeria.test' },
}

const FREE_STORE: StoreAdmin = {
  id: 2,
  number: 2,
  name: 'Local Dos',
  side: 'right',
  position: 2,
  is_active: true,
  merchant: null,
}

const MERCHANT: Merchant = {
  id: 10,
  email: 'ana@galeria.test',
  full_name: 'Ana Pérez',
  is_active: true,
  created_at: '2026-01-01T00:00:00',
  store: { id: 1, number: 1, name: 'Local Uno' },
}

function renderMerchantsPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: Infinity,
      },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AuthProvider>
          <MerchantsPage />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function fillMerchantForm({
  email = 'nuevo@galeria.test',
  fullName = 'Nuevo Comerciante',
  password = 'contrasena123',
  storeId = '2',
} = {}) {
  fireEvent.change(screen.getByLabelText(/correo electrónico/i), {
    target: { value: email },
  })
  fireEvent.change(screen.getByLabelText(/nombre completo/i), {
    target: { value: fullName },
  })
  fireEvent.change(screen.getByLabelText(/^contraseña$/i), {
    target: { value: password },
  })
  fireEvent.change(screen.getByLabelText(/^local$/i), {
    target: { value: storeId },
  })
  fireEvent.click(screen.getByRole('button', { name: /crear comerciante/i }))
}

beforeEach(() => {
  sessionStorage.clear()
  vi.clearAllMocks()
})

afterEach(() => {
  vi.clearAllMocks()
})

describe('MerchantsPage', () => {
  it('muestra el listado de comerciantes con su local y estado', async () => {
    mockedListMerchants.mockResolvedValue([MERCHANT])
    mockedListAdminStores.mockResolvedValue([OCCUPIED_STORE, FREE_STORE])

    renderMerchantsPage()

    expect(await screen.findByText('ana@galeria.test')).toBeInTheDocument()
    expect(screen.getByText('Ana Pérez')).toBeInTheDocument()
    expect(screen.getByText('Local 1 · Local Uno')).toBeInTheDocument()
    expect(screen.getByText('Activo')).toBeInTheDocument()
  })

  it('muestra un estado vacío cuando no hay comerciantes', async () => {
    mockedListMerchants.mockResolvedValue([])
    mockedListAdminStores.mockResolvedValue([FREE_STORE])

    renderMerchantsPage()

    expect(
      await screen.findByText(/todavía no hay comerciantes registrados/i),
    ).toBeInTheDocument()
  })

  it('crea un comerciante con el payload correcto y refresca el listado', async () => {
    const created: Merchant = {
      id: 11,
      email: 'nuevo@galeria.test',
      full_name: 'Nuevo Comerciante',
      is_active: true,
      created_at: '2026-02-01T00:00:00',
      store: { id: 2, number: 2, name: 'Local Dos' },
    }

    mockedListMerchants.mockResolvedValue([])
    mockedListAdminStores.mockResolvedValue([FREE_STORE])
    mockedCreateMerchant.mockResolvedValue(created)

    renderMerchantsPage()

    expect(await screen.findByLabelText(/correo electrónico/i)).toBeInTheDocument()
    fillMerchantForm()

    await waitFor(() => expect(mockedCreateMerchant).toHaveBeenCalledTimes(1))
    expect(mockedCreateMerchant.mock.calls[0][0]).toEqual({
      email: 'nuevo@galeria.test',
      full_name: 'Nuevo Comerciante',
      password: 'contrasena123',
      store_id: 2,
    })

    await waitFor(() => expect(mockedListMerchants.mock.calls.length).toBeGreaterThanOrEqual(2))
    await waitFor(() => expect(mockedListAdminStores.mock.calls.length).toBeGreaterThanOrEqual(2))
  })

  it('muestra el error 409 y conserva los datos del formulario', async () => {
    mockedListMerchants.mockResolvedValue([])
    mockedListAdminStores.mockResolvedValue([FREE_STORE])
    mockedCreateMerchant.mockRejectedValue(new ApiError(409, 'Local ocupado.'))

    renderMerchantsPage()

    expect(await screen.findByLabelText(/correo electrónico/i)).toBeInTheDocument()
    fillMerchantForm()

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/local ya está ocupado|ya existe un comerciante/i)
    expect(screen.getByLabelText(/correo electrónico/i)).toHaveValue('nuevo@galeria.test')
    expect(screen.getByLabelText(/nombre completo/i)).toHaveValue('Nuevo Comerciante')
    expect(mockedCreateMerchant).toHaveBeenCalledTimes(1)
  })

  it('pide confirmación, da de baja y refresca el listado', async () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)
    mockedListMerchants.mockResolvedValue([MERCHANT])
    mockedListAdminStores.mockResolvedValue([OCCUPIED_STORE, FREE_STORE])
    mockedDeactivateMerchant.mockResolvedValue(undefined)

    renderMerchantsPage()

    const deactivateButton = await screen.findByRole('button', { name: 'Dar de baja' })
    fireEvent.click(deactivateButton)

    expect(confirmSpy).toHaveBeenCalledTimes(1)
    await waitFor(() => expect(mockedDeactivateMerchant).toHaveBeenCalledTimes(1))
    expect(mockedDeactivateMerchant.mock.calls[0][0]).toBe(10)
    await waitFor(() => expect(mockedListMerchants.mock.calls.length).toBeGreaterThanOrEqual(2))
    await waitFor(() => expect(mockedListAdminStores.mock.calls.length).toBeGreaterThanOrEqual(2))

    confirmSpy.mockRestore()
  })
})
