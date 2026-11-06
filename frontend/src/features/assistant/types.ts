export type ChatRole = 'user' | 'assistant'

export interface AssistantSource {
  title: string
  type: string
}

export type AssistantAction =
  | {
      type: 'search'
      label: string
      query: string
      href: string
    }
  | {
      type: 'map'
      label: string
      href: string
    }

export interface ChatMessage {
  id: string
  role: ChatRole
  content: string
  action?: AssistantAction | null
  sources?: AssistantSource[]
}

export interface AssistantChatRequest {
  message: string
  history: Array<{ role: ChatRole; content: string }>
}

export interface ChatResponse {
  answer: string
  action: AssistantAction | null
  sources: AssistantSource[]
}
