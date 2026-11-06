import type { ReactElement } from 'react'
import { Link } from 'react-router-dom'
import { AccountActions } from './AccountActions'
import { HeaderSearch } from './HeaderSearch'

export function SiteHeader(): ReactElement {
  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white">
      <div className="mx-auto w-full max-w-6xl px-4 py-3 sm:px-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link
            to="/"
            className="text-lg font-bold text-slate-900 transition-colors hover:text-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            Galería Comercial
          </Link>
          <AccountActions />
        </div>

        <div className="mt-3">
          <HeaderSearch />
        </div>
      </div>
    </header>
  )
}
