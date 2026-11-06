import { useState } from 'react'
import type { ReactElement } from 'react'
import { Link } from 'react-router-dom'
import type { MapStore } from './types'

interface StoreLogoProps {
  logoUrl: string | null
  storeName: string
}

function StoreLogo({ logoUrl, storeName }: StoreLogoProps): ReactElement {
  const [hasError, setHasError] = useState(false)

  if (!logoUrl || hasError) {
    return (
      <span
        role="img"
        aria-label={`Logo no disponible de ${storeName}`}
        className="flex h-8 w-8 shrink-0 items-center justify-center rounded border border-slate-200 bg-slate-100 text-slate-400"
      >
        <svg
          aria-hidden="true"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.8}
          className="h-4 w-4"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M3 9.5 5 4h14l2 5.5M4 9.5h16V20H4V9.5ZM9 20v-6h6v6"
          />
        </svg>
      </span>
    )
  }

  return (
    <img
      src={logoUrl}
      alt={`Logo de ${storeName}`}
      onError={() => setHasError(true)}
      className="h-8 w-8 shrink-0 rounded border border-slate-200 bg-white object-contain"
    />
  )
}

interface StoreSlotProps {
  store: MapStore
}

export function StoreSlot({ store }: StoreSlotProps): ReactElement {
  return (
    <Link
      to={`/locales/${store.id}`}
      aria-label={`Local ${store.number}: ${store.name}`}
      className="flex min-h-16 w-full flex-col items-center justify-center gap-1 rounded-md border border-slate-300 bg-white px-2 py-2 text-center transition-colors hover:border-indigo-400 hover:bg-indigo-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
    >
      <StoreLogo logoUrl={store.logo_url} storeName={store.name} />

      <span className="flex w-full min-w-0 flex-col items-center">
        <span className="text-[10px] font-semibold tracking-wide text-slate-500 uppercase">
          Local {store.number}
        </span>
        <span className="w-full truncate text-center text-sm font-semibold text-slate-700">
          {store.name}
        </span>
      </span>
    </Link>
  )
}
