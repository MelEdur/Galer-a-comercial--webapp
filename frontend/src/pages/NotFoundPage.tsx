import type { ReactElement } from 'react'
import { Link } from 'react-router-dom'

export function NotFoundPage(): ReactElement {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-xl flex-col justify-center gap-4 px-6 py-16 text-center">
      <p className="text-sm font-semibold tracking-wide text-indigo-600 uppercase">Error 404</p>
      <h1 className="text-3xl font-bold text-slate-900">Página no encontrada</h1>
      <p className="text-base text-slate-600">
        La página que buscas no existe o ha cambiado de ubicación.
      </p>
      <p>
        <Link
          to="/"
          className="inline-block rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
        >
          Volver a la página inicial
        </Link>
      </p>
    </main>
  )
}
