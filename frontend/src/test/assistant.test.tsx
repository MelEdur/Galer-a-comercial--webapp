import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, useLocation } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { sendAssistantMessage } from '../features/assistant/api'
import { AssistantWidget } from '../features/assistant/AssistantWidget'
import type { ChatResponse } from '../features/assistant/types'
import { ApiError } from '../lib/http'

vi.mock('../features/assistant/api')

const mockedSendAssistantMessage = vi.mocked(sendAssistantMessage)

function LocationProbe() {
  const location = useLocation()
  return <p data-testid="location">{`${location.pathname}${location.search}`}</p>
}

function renderWidget(initialEntries: string[] = ['/']) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <AssistantWidget />
      <LocationProbe />
    </MemoryRouter>,
  )
}

function openAssistant() {
  fireEvent.click(screen.getByRole('button', { name: /abrir asistente/i }))
}

function typeMessage(text: string) {
  fireEvent.change(screen.getByLabelText(/escribe tu mensaje/i), {
    target: { value: text },
  })
}

function sendMessage() {
  fireEvent.click(screen.getByRole('button', { name: /^enviar$/i }))
}

function responseWith(overrides: Partial<ChatResponse> = {}): ChatResponse {
  return {
    answer: 'Respuesta del asistente.',
    action: null,
    sources: [],
    ...overrides,
  }
}

beforeEach(() => {
  mockedSendAssistantMessage.mockReset()
})

afterEach(() => {
  vi.clearAllMocks()
})

describe('AssistantWidget', () => {
  it('abre y cierra el panel con el botón flotante', () => {
    renderWidget()

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()

    openAssistant()
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByLabelText(/escribe tu mensaje/i)).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /cerrar asistente/i }))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('cierra el panel con la tecla Escape', () => {
    renderWidget()
    openAssistant()

    fireEvent.keyDown(document, { key: 'Escape' })

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('envía un mensaje, muestra la carga y luego la respuesta', async () => {
    let resolveChat: (value: ChatResponse) => void = () => undefined
    mockedSendAssistantMessage.mockReturnValue(
      new Promise<ChatResponse>((resolve) => {
        resolveChat = resolve
      }),
    )

    renderWidget()
    openAssistant()
    typeMessage('¿Cómo encuentro un local?')
    sendMessage()

    expect(screen.getByText('¿Cómo encuentro un local?')).toBeInTheDocument()
    expect(screen.getByText('Pensando…')).toBeInTheDocument()
    expect(screen.getByLabelText(/escribe tu mensaje/i)).toBeDisabled()

    resolveChat(responseWith({ answer: 'Puedes usar el mapa.' }))

    await waitFor(() => {
      expect(screen.getByText('Puedes usar el mapa.')).toBeInTheDocument()
    })
    expect(screen.queryByText('Pensando…')).not.toBeInTheDocument()
  })

  it('envía como historial solo los últimos 10 mensajes', async () => {
    mockedSendAssistantMessage.mockImplementation(async ({ message }) =>
      responseWith({ answer: `Eco: ${message}` }),
    )

    renderWidget()
    openAssistant()

    for (let index = 0; index < 6; index += 1) {
      typeMessage(`pregunta ${index}`)
      sendMessage()

      await waitFor(() => {
        expect(screen.getByText(`Eco: pregunta ${index}`)).toBeInTheDocument()
      })
    }

    expect(mockedSendAssistantMessage).toHaveBeenCalledTimes(6)
    const lastPayload = mockedSendAssistantMessage.mock.calls[5][0]
    expect(lastPayload.history).toHaveLength(10)
    expect(lastPayload.history[0]).toEqual({
      role: 'user',
      content: 'pregunta 0',
    })
  })

  it('la acción de búsqueda navega a /buscar con el término', async () => {
    mockedSendAssistantMessage.mockResolvedValue(
      responseWith({
        answer: '¿Quieres buscar auriculares?',
        action: {
          type: 'search',
          label: 'Buscar auriculares',
          query: 'auriculares',
          href: '/buscar?search=auriculares',
        },
      }),
    )

    renderWidget()
    openAssistant()
    typeMessage('¿Dónde compro auriculares?')
    sendMessage()

    const actionButton = await screen.findByRole('button', {
      name: 'Buscar auriculares',
    })
    fireEvent.click(actionButton)

    expect(screen.getByTestId('location')).toHaveTextContent(
      '/buscar?search=auriculares',
    )
  })

  it('la acción de mapa navega a /mapa', async () => {
    mockedSendAssistantMessage.mockResolvedValue(
      responseWith({
        answer: 'Puedes consultar el mapa.',
        action: {
          type: 'map',
          label: 'Abrir mapa',
          href: '/mapa',
        },
      }),
    )

    renderWidget()
    openAssistant()
    typeMessage('¿Cómo llego al local 3?')
    sendMessage()

    const actionButton = await screen.findByRole('button', { name: 'Abrir mapa' })
    fireEvent.click(actionButton)

    expect(screen.getByTestId('location')).toHaveTextContent('/mapa')
  })

  it('muestra el error de la API sin perder la conversación', async () => {
    mockedSendAssistantMessage
      .mockResolvedValueOnce(responseWith({ answer: 'Primera respuesta.' }))
      .mockRejectedValueOnce(new ApiError(503, 'Servicio no disponible'))

    renderWidget()
    openAssistant()

    typeMessage('primer mensaje')
    sendMessage()
    await screen.findByText('Primera respuesta.')

    typeMessage('segundo mensaje')
    sendMessage()

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent(/no está disponible/i)
    expect(screen.getByText('primer mensaje')).toBeInTheDocument()
    expect(screen.getByText('Primera respuesta.')).toBeInTheDocument()
    expect(screen.getByText('segundo mensaje')).toBeInTheDocument()
  })

  it.each(['/admin', '/admin/comerciantes', '/comerciante', '/comerciante/local', '/login'])(
    'no muestra el widget en la ruta privada %s',
    (route) => {
      renderWidget([route])

      expect(
        screen.queryByRole('button', { name: /asistente/i }),
      ).not.toBeInTheDocument()
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    },
  )
})
