import { useState } from 'react'
import type { ReactElement } from 'react'
import { Link } from 'react-router-dom'
import type { ExploreStore } from './types'

interface StoreCardProps {
  store: ExploreStore
}

interface StoreLogoProps {
  logoUrl: string | null
  storeName: string
}

function StoreLogo({ logoUrl, storeName }: StoreLogoProps): ReactElement {
  const [hasError, setHasError] = useState(false)

  if (!logoUrl || hasError) {
    return (
      <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-md border border-slate-200 bg-slate-100">
        <span className="text-xs text-slate-400">Sin logo</span>
      </div>
    )
  }

  return (
    <img
      src={logoUrl}
      alt={`Logo de ${storeName}`}
      onError={() => setHasError(true)}
      className="h-16 w-16 shrink-0 rounded-md border border-slate-200 object-contain"
    />
  )
}

export function StoreCard({ store }: StoreCardProps): ReactElement {
  return (
    <Link
      to={`/locales/${store.id}`}
      className="group block h-full rounded-lg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
    >
      <article className="flex h-full items-start gap-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition-shadow group-hover:shadow-md">
        <StoreLogo
          key={store.logo_url ?? 'no-logo'}
          logoUrl={store.logo_url}
          storeName={store.name}
        />

        <div className="space-y-1">
          <p className="text-sm font-semibold text-indigo-600">
            Local {store.number}
          </p>
          <h3 className="text-base font-semibold text-slate-900">{store.name}</h3>
          {store.description ? (
            <p className="text-sm text-slate-600">{store.description}</p>
          ) : null}
        </div>
      </article>
    </Link>
  )
}
