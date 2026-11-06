import type { ReactElement } from 'react'
import { ActionButton } from './ActionButton'
import type { AssistantAction, ChatMessage } from './types'

interface MessageListProps {
  messages: ChatMessage[]
  isLoading: boolean
  onAction: (action: AssistantAction) => void
}

export function MessageList({
  messages,
  isLoading,
  onAction,
}: MessageListProps): ReactElement {
  return (
    <div
      aria-live="polite"
      className="flex flex-1 flex-col gap-3 overflow-y-auto px-4 py-4"
    >
      {messages.length === 0 && !isLoading ? (
        <p className="rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-600">
          Hola, soy el asistente de la galería. Puedo ayudarte a conocer los locales,
          las categorías y cómo usar la aplicación.
        </p>
      ) : null}

      {messages.map((message) => (
        <div
          key={message.id}
          className={
            message.role === 'user'
              ? 'self-end rounded-lg bg-indigo-600 px-3 py-2 text-sm text-white'
              : 'self-start rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-800'
          }
        >
          <p className="whitespace-pre-line">{message.content}</p>
          {message.action ? (
            <ActionButton action={message.action} onSelect={onAction} />
          ) : null}
        </div>
      ))}

      {isLoading ? (
        <p className="self-start rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-600">
          Pensando…
        </p>
      ) : null}
    </div>
  )
}
