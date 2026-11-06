import { useRef, useState } from 'react'
import type { FormEvent, ReactElement } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { ApiError } from '../../lib/http'
import { sendAssistantMessage } from './api'
import { AssistantPanel } from './AssistantPanel'
import type { AssistantAction, ChatMessage } from './types'

const MAX_HISTORY_MESSAGES = 10

function isHiddenRoute(pathname: string): boolean {
  return (
    pathname === '/login' ||
    pathname === '/admin' ||
    pathname.startsWith('/admin/') ||
    pathname === '/comerciante' ||
    pathname.startsWith('/comerciante/')
  )
}

function errorMessageFor(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 422) {
      return 'El mensaje no es válido. Acórtalo e inténtalo de nuevo.'
    }
    if (error.status === 429) {
      return 'Has hecho demasiadas consultas. Espera un momento e inténtalo de nuevo.'
    }
    if (error.status === 503) {
      return 'El asistente no está disponible en este momento. Inténtalo más tarde.'
    }
  }

  return 'No se ha podido contactar con el asistente. Inténtalo de nuevo.'
}

export function AssistantWidget(): ReactElement | null {
  const location = useLocation()
  const navigate = useNavigate()

  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const nextId = useRef(0)

  if (isHiddenRoute(location.pathname)) {
    return null
  }

  function makeId(): string {
    nextId.current += 1
    return `assistant-message-${nextId.current}`
  }

  async function handleSend(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const text = input.trim()
    if (text.length === 0 || isLoading) {
      return
    }

    const history = messages
      .slice(-MAX_HISTORY_MESSAGES)
      .map(({ role, content }) => ({ role, content }))

    setMessages((previous) => [
      ...previous,
      { id: makeId(), role: 'user', content: text },
    ])
    setInput('')
    setError(null)
    setIsLoading(true)

    try {
      const response = await sendAssistantMessage({ message: text, history })
      setMessages((previous) => [
        ...previous,
        {
          id: makeId(),
          role: 'assistant',
          content: response.answer,
          action: response.action,
          sources: response.sources,
        },
      ])
    } catch (sendError) {
      setError(errorMessageFor(sendError))
    } finally {
      setIsLoading(false)
    }
  }

  function handleAction(action: AssistantAction) {
    navigate(action.href)
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen((previous) => !previous)}
        aria-label={isOpen ? 'Cerrar asistente' : 'Abrir asistente'}
        aria-expanded={isOpen}
        className="fixed right-4 bottom-4 z-50 inline-flex items-center gap-2 rounded-full bg-indigo-600 px-4 py-3 text-sm font-semibold text-white shadow-lg transition-colors hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
      >
        <span aria-hidden="true">💬</span>
        Asistente
      </button>

      {isOpen ? (
        <AssistantPanel
          messages={messages}
          input={input}
          isLoading={isLoading}
          error={error}
          onInputChange={setInput}
          onSubmit={handleSend}
          onClose={() => setIsOpen(false)}
          onAction={handleAction}
        />
      ) : null}
    </>
  )
}
