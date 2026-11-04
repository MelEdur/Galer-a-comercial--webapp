import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { getCurrentUser } from '../features/auth/api'
import { AuthProvider } from '../features/auth/AuthContext'
import { ProtectedRoute } from '../features/auth/ProtectedRoute'
import type { CurrentUser } from '../features/auth/types'
import { getMyStore, updateMyStore } from '../features/merchant-store/api'
import { StoreSettingsPage } from '../features/merchant-store/StoreSettingsPage'
import type { MerchantStore } from '../features/merchant-store/types'
import { MerchantPage } from '../pages/MerchantPage'
import { ApiError } from '../lib/http'

vi.mock('../features/merchant-store/api')
vi.mock('../features/auth/api')

const mockedGetMyStore = vi.mocked(getMyStore)
const mockedUpdateMyStore = vi.mocked(updateMyStore)
const mockedGetCurrentUser = vi.mocked(getCurrentUser)

const TOKEN_KEY = 'galeria.auth.token'

const STORE: MerchantStore = {
  id: 1,
  number: 2,
  side: 'right',
  position: 1,
  name: 'Local 2',
  description: 'Ropa para toda la familia',
  logo_url: 'https://images.test/logo.png',
  email: 'local2@galeria.test',
  phone: '555-1234',
  whatsapp: '+54 9 11 5555-1234',
  hours: [
    { day_of_week: 0, opens_at: '09:00:00', closes_at: '13:00:00' },
    { day_of_week: 0, opens_at: '15:00:00', closes_at: '19:00:00' },
  ],
  links: [
    {
      label: 'Instagram',
      url: 'https://instagram.com/local2',
      position: 0,
    },
  ],
}

function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: Infinity },
      mutations: { retry: false },
    },
  })
}

function buildCurrentUser(storeName: string): CurrentUser {
  return {
    id: 2,
    email: 'local2@galeria.test',
    full_name: 'Comerciante de Prueba',
    role: 'merchant',
    is_active: true,
    store_id: STORE.id,
    store: { id: STORE.id, number: STORE.number, name: storeName },
  }
}

function renderPage(): ReturnType<typeof render> {
  return render(
    <QueryClientProvider client={createQueryClient()}>
      <AuthProvider>
        <MemoryRouter initialEntries={['/comerciante/local']}>
          <Routes>
            <Route path="/comerciante/local" element={<StoreSettingsPage />} />
            <Route
              path="/comerciante"
              element={
                <ProtectedRoute role="merchant">
                  <MerchantPage />
                </ProtectedRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    </QueryClientProvider>,
  )
}

async function renderLoadedPage(): Promise<ReturnType<typeof render>> {
  const view = renderPage()
  await screen.findByDisplayValue('Local 2')
  return view
}

function fillField(label: string, value: string) {
  fireEvent.change(screen.getByLabelText(label), { target: { value } })
}

beforeEach(() => {
  vi.clearAllMocks()
  sessionStorage.clear()
  sessionStorage.setItem(TOKEN_KEY, 'token-merchant')
  mockedGetMyStore.mockResolvedValue(STORE)
  mockedUpdateMyStore.mockResolvedValue(STORE)
  mockedGetCurrentUser.mockResolvedValue(buildCurrentUser(STORE.name))
})

afterEach(() => {
  vi.clearAllMocks()
  sessionStorage.clear()
})

describe('Información del local', () => {
  it('carga y muestra los datos actuales, horarios y enlaces', async () => {
    await renderLoadedPage()

    expect(screen.getByLabelText('Nombre')).toHaveValue('Local 2')
    expect(screen.getByLabelText('Descripción')).toHaveValue(
      'Ropa para toda la familia',
    )
    expect(screen.getByLabelText('URL del logo')).toHaveValue(
      'https://images.test/logo.png',
    )
    expect(screen.getByLabelText('Correo electrónico')).toHaveValue(
      'local2@galeria.test',
    )
    expect(screen.getByLabelText('Teléfono')).toHaveValue('555-1234')
    expect(screen.getByLabelText('WhatsApp')).toHaveValue('+54 9 11 5555-1234')

    expect(screen.getByLabelText('Apertura Lunes 1')).toHaveValue('09:00')
    expect(screen.getByLabelText('Cierre Lunes 1')).toHaveValue('13:00')
    expect(screen.getByLabelText('Apertura Lunes 2')).toHaveValue('15:00')
    expect(screen.getByLabelText('Cierre Lunes 2')).toHaveValue('19:00')

    expect(screen.getByLabelText('Etiqueta del enlace 1')).toHaveValue('Instagram')
    expect(screen.getByLabelText('URL del enlace 1')).toHaveValue(
      'https://instagram.com/local2',
    )
  })

  it('edita nombre y contacto y envía el payload correcto', async () => {
    await renderLoadedPage()

    fillField('Nombre', 'Local Dos Renovado')
    fillField('Correo electrónico', 'nuevo@galeria.test')
    fillField('Teléfono', '555-9999')

    fireEvent.click(screen.getByRole('button', { name: 'Guardar cambios' }))

    await waitFor(() => expect(mockedUpdateMyStore).toHaveBeenCalledTimes(1))

    expect(mockedUpdateMyStore).toHaveBeenCalledWith(
      {
        name: 'Local Dos Renovado',
        description: 'Ropa para toda la familia',
        logo_url: 'https://images.test/logo.png',
        email: 'nuevo@galeria.test',
        phone: '555-9999',
        whatsapp: '+54 9 11 5555-1234',
        hours: [
          { day_of_week: 0, opens_at: '09:00', closes_at: '13:00' },
          { day_of_week: 0, opens_at: '15:00', closes_at: '19:00' },
        ],
        links: [
          { label: 'Instagram', url: 'https://instagram.com/local2' },
        ],
      },
      expect.anything(),
    )

    expect(
      await screen.findByRole('heading', { name: 'Panel del comerciante' }),
    ).toBeInTheDocument()
  })

  it('vuelve al panel y refresca la sesión con el local actualizado', async () => {
    const updatedStore: MerchantStore = { ...STORE, name: 'Local Dos Renovado' }
    mockedUpdateMyStore.mockResolvedValue(updatedStore)
    mockedGetCurrentUser
      .mockResolvedValueOnce(buildCurrentUser(STORE.name))
      .mockResolvedValueOnce(buildCurrentUser(updatedStore.name))

    await renderLoadedPage()

    fillField('Nombre', 'Local Dos Renovado')
    fireEvent.click(screen.getByRole('button', { name: 'Guardar cambios' }))

    expect(
      await screen.findByRole('heading', { name: 'Panel del comerciante' }),
    ).toBeInTheDocument()
    expect(await screen.findByText('Local Dos Renovado')).toBeInTheDocument()
    expect(mockedGetCurrentUser).toHaveBeenCalledTimes(2)
  })

  it('agrega y quita tramos horarios', async () => {
    await renderLoadedPage()

    fireEvent.click(screen.getByRole('button', { name: 'Agregar tramo Martes' }))

    expect(screen.getByLabelText('Apertura Martes 1')).toHaveValue('09:00')
    expect(screen.getByLabelText('Cierre Martes 1')).toHaveValue('18:00')

    fireEvent.change(screen.getByLabelText('Apertura Martes 1'), {
      target: { value: '10:30' },
    })
    fireEvent.change(screen.getByLabelText('Cierre Martes 1'), {
      target: { value: '14:00' },
    })

    expect(screen.getByLabelText('Apertura Martes 1')).toHaveValue('10:30')
    expect(screen.getByLabelText('Cierre Martes 1')).toHaveValue('14:00')

    fireEvent.click(
      screen.getByRole('button', { name: 'Quitar tramo Martes 1' }),
    )

    expect(screen.queryByLabelText('Apertura Martes 1')).not.toBeInTheDocument()
    expect(screen.getAllByText('Cerrado')).toHaveLength(6)
  })

  it('agrega y quita enlaces', async () => {
    await renderLoadedPage()

    fireEvent.click(screen.getByRole('button', { name: 'Agregar enlace' }))

    expect(screen.getByLabelText('Etiqueta del enlace 2')).toHaveValue('')
    expect(screen.getByLabelText('URL del enlace 2')).toHaveValue('')

    fireEvent.change(screen.getByLabelText('Etiqueta del enlace 2'), {
      target: { value: 'Sitio web' },
    })
    fireEvent.change(screen.getByLabelText('URL del enlace 2'), {
      target: { value: 'https://local2.test' },
    })

    expect(screen.getByLabelText('Etiqueta del enlace 2')).toHaveValue('Sitio web')
    expect(screen.getByLabelText('URL del enlace 2')).toHaveValue(
      'https://local2.test',
    )

    fireEvent.click(screen.getByRole('button', { name: 'Quitar enlace 2' }))

    expect(screen.queryByLabelText('Etiqueta del enlace 2')).not.toBeInTheDocument()
    expect(screen.getByLabelText('Etiqueta del enlace 1')).toHaveValue('Instagram')
  })

  it('muestra el error 422 sin perder los datos ingresados', async () => {
    mockedUpdateMyStore.mockRejectedValue(new ApiError(422, 'Datos no válidos.'))
    await renderLoadedPage()

    fillField('Nombre', 'Nombre conservado')
    fillField('Correo electrónico', 'conservado@galeria.test')

    fireEvent.click(screen.getByRole('button', { name: 'Guardar cambios' }))

    expect(
      await screen.findByText(/revisa los datos del formulario/i),
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Nombre')).toHaveValue('Nombre conservado')
    expect(screen.getByLabelText('Correo electrónico')).toHaveValue(
      'conservado@galeria.test',
    )
  })

  it('muestra número, lado y posición como solo lectura', async () => {
    await renderLoadedPage()

    expect(screen.getByText('Número')).toBeInTheDocument()
    expect(screen.getByText('Lado')).toBeInTheDocument()
    expect(screen.getByText('Posición')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('Derecha')).toBeInTheDocument()
    expect(screen.getByText('1')).toBeInTheDocument()

    expect(screen.queryByLabelText('Número')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Lado')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Posición')).not.toBeInTheDocument()
  })
})
