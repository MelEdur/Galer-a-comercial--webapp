import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { getHealth } from '../features/health/api'
import { HealthStatus } from '../features/health/HealthStatus'

vi.mock('../features/health/api')

const mockedGetHealth = vi.mocked(getHealth)

function renderHealthStatus() {
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
      <HealthStatus />
    </QueryClientProvider>,
  )
}

afterEach(() => {
  vi.clearAllMocks()
})

describe('HealthStatus', () => {
  it('muestra el estado de carga mientras la consulta está pendiente', () => {
    mockedGetHealth.mockReturnValue(new Promise(() => {}))

    renderHealthStatus()

    expect(screen.getByText(/comprobando el estado del backend/i)).toBeInTheDocument()
  })

  it('muestra el backend operativo cuando la consulta responde correctamente', async () => {
    mockedGetHealth.mockResolvedValue({ status: 'ok', database: 'ok' })

    renderHealthStatus()

    expect(await screen.findByText(/backend operativo/i)).toBeInTheDocument()
    expect(screen.getByText('Base de datos disponible')).toBeInTheDocument()
  })

  it('muestra la base de datos no disponible cuando el backend está degradado', async () => {
    mockedGetHealth.mockResolvedValue({ status: 'degraded', database: 'unavailable' })

    renderHealthStatus()

    expect(await screen.findByText(/backend operativo/i)).toBeInTheDocument()
    expect(screen.getByText('Base de datos no disponible')).toBeInTheDocument()
  })

  it('muestra el estado de error cuando la consulta falla sin bloquear la página', async () => {
    mockedGetHealth.mockRejectedValue(new Error('No se ha podido contactar con la API.'))

    renderHealthStatus()

    expect(await screen.findByText(/backend no disponible/i)).toBeInTheDocument()
    expect(screen.getByRole('alert')).toBeInTheDocument()
  })
})
