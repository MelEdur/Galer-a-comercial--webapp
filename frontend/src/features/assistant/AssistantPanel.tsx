import { useEffect, useRef } from 'react'
import type { FormEvent, ReactElement } from 'react'
import { MessageList } from './MessageList'
import type { AssistantAction, ChatMessage } from './types'

interface AssistantPanelProps {
  messages: ChatMessage[]
  input: string
  isLoading: boolean
  error: string | null
  onInputChange: (value: string) => void
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
  onClose: () => void
  onAction: (action: AssistantAction) => void
}

export function AssistantPanel({
  messages,
  input,
  isLoading,
  error,
  onInputChange,
  onSubmit,
  onClose,
  onAction,
}: AssistantPanelProps): ReactElement {
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        onClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="assistant-title"
      className="fixed right-4 bottom-24 z-50 flex max-h-[70vh] w-[22rem] max-w-[calc(100vw-2rem)] flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xl"
    >
      <header className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h2 id="assistant-title" className="text-sm font-semibold text-slate-900">
          Asistente de la galería
        </h2>
        <button
          type="button"
          onClick={onClose}
          aria-label="Cerrar panel del asistente"
          className="rounded-md p-1 text-slate-500 transition-colors hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-400"
        >
          <span aria-hidden="true">✕</span>
        </button>
      </header>

      <MessageList messages={messages} isLoading={isLoading} onAction={onAction} />

      {error ? (
        <p
          role="alert"
          className="mx-4 mb-2 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          {error}
        </p>
      ) : null}

      <form
        onSubmit={onSubmit}
        className="flex items-center gap-2 border-t border-slate-200 px-4 py-3"
      >
        <label htmlFor="assistant-input" className="sr-only">
          Escribe tu mensaje
        </label>
        <input
          id="assistant-input"
          ref={inputRef}
          type="text"
          value={input}
          maxLength={1000}
          disabled={isLoading}
          onChange={(event) => onInputChange(event.target.value)}
          placeholder="Escribe tu mensaje…"
          className="min-w-0 flex-1 rounded-md border border-slate-300 px-3 py-1.5 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200 disabled:bg-slate-100"
        />
        <button
          type="submit"
          disabled={isLoading || input.trim().length === 0}
          className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:cursor-not-allowed disabled:bg-indigo-300"
        >
          Enviar
        </button>
      </form>
    </div>
  )
}
