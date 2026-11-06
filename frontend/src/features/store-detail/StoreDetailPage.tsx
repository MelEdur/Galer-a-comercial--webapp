import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import type { ReactElement } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ApiError } from '../../lib/http'
import { useGoBack } from '../../lib/useGoBack'
import { getStoreDetail } from './api'
import { storeDetailKeys } from './queryKeys'
import { StoreCatalog } from './StoreCatalog'
import { StoreHours } from './StoreHours'
import { StoreLinks } from './StoreLinks'

interface StoreLogoProps {
  logoUrl: string | null
  storeName: string
}

function StoreLogo({ logoUrl, storeName }: StoreLogoProps): ReactElement {
  const [hasError, setHasError] = useState(false)

  if (!logoUrl || hasError) {
    return (
      <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-md border border-slate-200 bg-slate-100">
        <span className="text-xs text-slate-400">Sin logo</span>
      </div>
    )
  }

  return (
    <img
      src={logoUrl}
      alt={`Logo de ${storeName}`}
      onError={() => setHasError(true)}
      className="h-20 w-20 shrink-0 rounded-md border border-slate-200 object-contain"
    />
  )
}

export function StoreDetailPage(): ReactElement {
  const { storeId = '' } = useParams()
  const goBack = useGoBack()

  const detailQuery = useQuery({
    queryKey: storeDetailKeys.detail(storeId),
    queryFn: () => getStoreDetail(storeId),
    enabled: storeId.trim().length > 0,
  })

  const isNotFound =
    detailQuery.error instanceof ApiError && detailQuery.error.status === 404
  const store = detailQuery.data
  const whatsappDigits = store?.whatsapp ? store.whatsapp.replace(/\D/g, '') : ''
  const hasContact = Boolean(store?.email || store?.phone || whatsappDigits)

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-4xl flex-col gap-6 px-6 py-16">
      <button
        type="button"
        onClick={goBack}
        aria-label="Volver"
        className="w-fit text-sm font-semibold text-indigo-600 hover:text-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
      >
        ← Volver
      </button>

      {detailQuery.isPending ? (
        <p aria-live="polite" className="text-sm text-slate-600">
          Cargando local…
        </p>
      ) : null}

      {isNotFound ? (
        <section className="rounded-lg border border-slate-200 bg-white px-6 py-10 text-center shadow-sm">
          <h1 className="text-2xl font-bold text-slate-900">
            Local no encontrado
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            El local que buscas no está disponible o ya no existe.
          </p>
          <Link
            to="/buscar"
            className="mt-6 inline-flex rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            Volver al buscador
          </Link>
        </section>
      ) : null}

      {detailQuery.isError && !isNotFound ? (
        <p
          role="alert"
          className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          No se ha podido cargar el local. Inténtalo de nuevo más tarde.
        </p>
      ) : null}

      {store ? (
        <>
          <header className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-start gap-4">
              <StoreLogo
                key={store.logo_url ?? 'no-logo'}
                logoUrl={store.logo_url}
                storeName={store.name}
              />

              <div className="space-y-1">
                <p className="text-sm font-semibold text-indigo-600">
                  Local {store.number}
                </p>
                <h1 className="text-3xl font-bold text-slate-900">
                  {store.name}
                </h1>
                {store.description ? (
                  <p className="text-sm text-slate-600">{store.description}</p>
                ) : null}
              </div>
            </div>
          </header>

          <StoreHours hours={store.hours} />

          {hasContact ? (
            <section
              aria-labelledby="store-contact-title"
              className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
            >
              <h2
                id="store-contact-title"
                className="text-lg font-semibold text-slate-900"
              >
                Contacto
              </h2>

              <ul className="mt-4 space-y-1 text-sm">
                {store.email ? (
                  <li>
                    <a
                      href={`mailto:${store.email}`}
                      className="text-indigo-600 hover:text-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                    >
                      {store.email}
                    </a>
                  </li>
                ) : null}

                {store.phone ? (
                  <li>
                    <a
                      href={`tel:${store.phone}`}
                      className="text-indigo-600 hover:text-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                    >
                      {store.phone}
                    </a>
                  </li>
                ) : null}

                {whatsappDigits.length > 0 ? (
                  <li>
                    <a
                      href={`https://wa.me/${whatsappDigits}`}
                      target="_blank"
                      rel="noreferrer"
                      className="text-indigo-600 hover:text-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                    >
                      WhatsApp: {store.whatsapp}
                    </a>
                  </li>
                ) : null}
              </ul>
            </section>
          ) : null}

          <StoreLinks links={store.links} />

          <StoreCatalog key={store.id} storeId={String(store.id)} />
        </>
      ) : null}
    </main>
  )
}
