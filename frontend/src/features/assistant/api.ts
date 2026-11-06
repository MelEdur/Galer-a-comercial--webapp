import { apiFetch } from '../../lib/http'
import type { AssistantChatRequest, ChatResponse } from './types'

export function sendAssistantMessage(
  payload: AssistantChatRequest,
): Promise<ChatResponse> {
  return apiFetch<ChatResponse>('/public/assistant/chat', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
