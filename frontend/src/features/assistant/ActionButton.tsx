import type { ReactElement } from 'react'
import type { AssistantAction } from './types'

interface ActionButtonProps {
  action: AssistantAction
  onSelect: (action: AssistantAction) => void
}

export function ActionButton({ action, onSelect }: ActionButtonProps): ReactElement {
  return (
    <button
      type="button"
      onClick={() => onSelect(action)}
      className="mt-2 inline-flex rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
    >
      {action.label}
    </button>
  )
}
