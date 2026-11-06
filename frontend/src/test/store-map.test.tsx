import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, within } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { getStoreMap } from '../features/store-map/api'
import { StoreMapPage } from '../features/store-map/StoreMapPage'
import type { MapResponse, MapStore } from '../features/store-map/types'
import { ApiError } from '../lib/http'

vi.mock('../features/store-map/api')

const mockedGetStoreMap = vi.mocked(getStoreMap)

const STORES: MapStore[] = [
  {
    id: 3,
    number: 7,
    name: 'Librería del Pasillo',
    logo_url: null,
    side: 'right',
    position: 2,
  },
  {
    id: 4,
    number: 9,
    name: 'Fondo Café',
    logo_url: null,
    side: 'back',
    position: 1,
  },
  {
    id: 2,
    number: 5,
    name: 'Boutique Norte',
    logo_url: null,
    side: 'left',
    position: 3,
  },
  {
    id: 1,
    number: 2,
    name: 'Café Central',
    logo_url: 'https://images.test/cafe.png',
    side: 'left',
    position: 1,
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

function renderMapPage() {
  return render(
    <QueryClientProvider client={createQueryClient()}>
      <MemoryRouter initialEntries={['/mapa']}>
        <Routes>
          <Route path="/mapa" element={<StoreMapPage />} />
          <Route path="/locales/:storeId" element={<h1>Ficha del local</h1>} />
          <Route path="/" element={<h1>Inicio</h1>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function slotLinks(region: HTMLElement): HTMLElement[] {
  return within(region).getAllByRole('link')
}

beforeEach(() => {
  vi.clearAllMocks()
  mockedGetStoreMap.mockResolvedValue({ stores: STORES })
})

afterEach(() => {
  vi.clearAllMocks()
})

describe('Mapa público de la galería', () => {
  it('renderiza los locales agrupados por lado y ordenados por posición', async () => {
    renderMapPage()

    expect(
      await screen.findByRole('heading', { name: 'Mapa de la galería' }),
    ).toBeInTheDocument()

    const leftRegion = await screen.findByRole('region', {
      name: 'Lado izquierdo',
    })
    expect(
      slotLinks(leftRegion).map((link) => link.getAttribute('aria-label')),
    ).toEqual(['Local 2: Café Central', 'Local 5: Boutique Norte'])

    const rightRegion = screen.getByRole('region', { name: 'Lado derecho' })
    expect(
      slotLinks(rightRegion).map((link) => link.getAttribute('aria-label')),
    ).toEqual(['Local 7: Librería del Pasillo'])

    const backRegion = screen.getByRole('region', { name: 'Local del fondo' })
    expect(
      slotLinks(backRegion).map((link) => link.getAttribute('aria-label')),
    ).toEqual(['Local 9: Fondo Café'])
  })

  it('muestra número, nombre y logo en cada slot', async () => {
    renderMapPage()

    const leftRegion = await screen.findByRole('region', {
      name: 'Lado izquierdo',
    })

    const cafeSlot = within(leftRegion).getByRole('link', {
      name: 'Local 2: Café Central',
    })
    expect(cafeSlot).toHaveTextContent('Local 2')
    expect(cafeSlot).toHaveTextContent('Café Central')
    expect(
      within(cafeSlot).getByAltText('Logo de Café Central'),
    ).toHaveAttribute('src', 'https://images.test/cafe.png')

    const boutiqueSlot = within(leftRegion).getByRole('link', {
      name: 'Local 5: Boutique Norte',
    })
    expect(boutiqueSlot).toHaveTextContent('Local 5')
    expect(boutiqueSlot).toHaveTextContent('Boutique Norte')
    expect(
      within(boutiqueSlot).getByRole('img', {
        name: 'Logo no disponible de Boutique Norte',
      }),
    ).toBeInTheDocument()
  })

  it('usa un marcador cuando el logo falla al cargarse', async () => {
    renderMapPage()

    const leftRegion = await screen.findByRole('region', {
      name: 'Lado izquierdo',
    })
    const logo = within(leftRegion).getByAltText('Logo de Café Central')

    fireEvent.error(logo)

    expect(
      within(leftRegion).getByRole('img', {
        name: 'Logo no disponible de Café Central',
      }),
    ).toBeInTheDocument()
  })

  it('cada slot es un enlace a la ficha del local', async () => {
    renderMapPage()

    const leftRegion = await screen.findByRole('region', {
      name: 'Lado izquierdo',
    })

    expect(
      within(leftRegion).getByRole('link', { name: 'Local 2: Café Central' }),
    ).toHaveAttribute('href', '/locales/1')
    expect(
      within(leftRegion).getByRole('link', { name: 'Local 5: Boutique Norte' }),
    ).toHaveAttribute('href', '/locales/2')

    const rightRegion = screen.getByRole('region', { name: 'Lado derecho' })
    expect(
      within(rightRegion).getByRole('link', {
        name: 'Local 7: Librería del Pasillo',
      }),
    ).toHaveAttribute('href', '/locales/3')

    const backRegion = screen.getByRole('region', { name: 'Local del fondo' })
    expect(
      within(backRegion).getByRole('link', { name: 'Local 9: Fondo Café' }),
    ).toHaveAttribute('href', '/locales/4')
  })

  it('navega a la ficha del local al hacer clic en un slot', async () => {
    renderMapPage()

    fireEvent.click(
      await screen.findByRole('link', { name: 'Local 2: Café Central' }),
    )

    expect(
      await screen.findByRole('heading', { name: 'Ficha del local' }),
    ).toBeInTheDocument()
  })

  it('ya no muestra un panel de selección', async () => {
    renderMapPage()

    await screen.findByRole('region', { name: 'Lado izquierdo' })

    expect(
      screen.queryByRole('region', { name: 'Detalle del local' }),
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText(
        'Selecciona un local del mapa para ver su información.',
      ),
    ).not.toBeInTheDocument()
  })

  it('muestra el estado de carga', () => {
    mockedGetStoreMap.mockReturnValue(new Promise<MapResponse>(() => {}))

    renderMapPage()

    expect(screen.getByText('Cargando mapa…')).toBeInTheDocument()
  })

  it('muestra un error sin romper la página', async () => {
    mockedGetStoreMap.mockRejectedValue(
      new ApiError(500, 'No se pudo cargar el mapa.'),
    )

    renderMapPage()

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/no se ha podido cargar el mapa/i)
    expect(
      screen.getByRole('heading', { name: 'Mapa de la galería' }),
    ).toBeInTheDocument()
  })

  it('muestra el estado vacío cuando no hay locales activos', async () => {
    mockedGetStoreMap.mockResolvedValue({ stores: [] })

    renderMapPage()

    expect(
      await screen.findByText(
        'Todavía no hay locales disponibles en el mapa.',
      ),
    ).toBeInTheDocument()
  })
})
