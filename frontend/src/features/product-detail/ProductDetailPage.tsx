import { useQuery } from '@tanstack/react-query'
import type { ReactElement } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ApiError } from '../../lib/http'
import { formatPrice } from '../product-search/format'
import { getProductDetail, getSimilarProducts } from './api'
import { ProductGallery } from './ProductGallery'
import { productDetailKeys } from './queryKeys'
import { SimilarProducts } from './SimilarProducts'

export function ProductDetailPage(): ReactElement {
  const { productId = '' } = useParams()

  const detailQuery = useQuery({
    queryKey: productDetailKeys.detail(productId),
    queryFn: () => getProductDetail(productId),
    enabled: productId.trim().length > 0,
  })

  const similarQuery = useQuery({
    queryKey: productDetailKeys.similar(productId),
    queryFn: () => getSimilarProducts(productId),
    enabled: detailQuery.isSuccess,
  })

  const isNotFound =
    detailQuery.error instanceof ApiError && detailQuery.error.status === 404
  const product = detailQuery.data
  const hasOffer = product ? product.offer_price !== null : false
  const whatsappDigits = product?.store.whatsapp
    ? product.store.whatsapp.replace(/\D/g, '')
    : ''

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-6 py-16">
      <Link
        to="/buscar"
        className="w-fit text-sm font-semibold text-indigo-600 hover:text-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
      >
        ← Volver a la búsqueda
      </Link>

      {detailQuery.isPending ? (
        <p aria-live="polite" className="text-sm text-slate-600">
          Cargando producto…
        </p>
      ) : null}

      {isNotFound ? (
        <section className="rounded-lg border border-slate-200 bg-white px-6 py-10 text-center shadow-sm">
          <h1 className="text-2xl font-bold text-slate-900">Producto no encontrado</h1>
          <p className="mt-2 text-sm text-slate-600">
            El producto que buscas no está disponible o ya no existe.
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
          No se ha podido cargar el producto. Inténtalo de nuevo más tarde.
        </p>
      ) : null}

      {product ? (
        <>
          <article className="grid gap-8 lg:grid-cols-2">
            <ProductGallery images={product.images} productName={product.name} />

            <div className="space-y-6">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold text-slate-900">{product.name}</h1>
                {product.description ? (
                  <p className="text-sm text-slate-600">{product.description}</p>
                ) : null}
              </div>

              <div className="space-y-1">
                {hasOffer ? (
                  <p className="flex flex-wrap items-baseline gap-2">
                    <span className="text-base text-slate-400 line-through">
                      {formatPrice(product.price)}
                    </span>
                    <span className="text-2xl font-bold text-emerald-700">
                      {formatPrice(product.effective_price)}
                    </span>
                    <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-semibold text-emerald-700">
                      Oferta
                    </span>
                  </p>
                ) : (
                  <p className="text-2xl font-bold text-slate-900">
                    {formatPrice(product.price)}
                  </p>
                )}
              </div>

              {product.categories.length > 0 ? (
                <ul className="flex flex-wrap gap-1.5">
                  {product.categories.map((category) => (
                    <li
                      key={category.id}
                      className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600"
                    >
                      {category.name}
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>
          </article>

          <section
            aria-labelledby="store-title"
            className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
          >
            <h2 id="store-title" className="text-lg font-semibold text-slate-900">
              Local
            </h2>

            <div className="mt-4 flex items-start gap-4">
              {product.store.logo_url ? (
                <img
                  src={product.store.logo_url}
                  alt={`Logo de ${product.store.name}`}
                  className="h-16 w-16 rounded-md border border-slate-200 object-contain"
                />
              ) : null}

              <div className="space-y-2">
                <div>
                  <p className="text-sm font-semibold text-slate-900">
                    Local {product.store.number}
                  </p>
                  <p className="text-sm text-slate-700">{product.store.name}</p>
                </div>

                <ul className="space-y-1 text-sm">
                  {product.store.email ? (
                    <li>
                      <a
                        href={`mailto:${product.store.email}`}
                        className="text-indigo-600 hover:text-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                      >
                        {product.store.email}
                      </a>
                    </li>
                  ) : null}

                  {product.store.phone ? (
                    <li>
                      <a
                        href={`tel:${product.store.phone}`}
                        className="text-indigo-600 hover:text-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                      >
                        {product.store.phone}
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
                        WhatsApp: {product.store.whatsapp}
                      </a>
                    </li>
                  ) : null}
                </ul>
              </div>
            </div>
          </section>

          <SimilarProducts products={similarQuery.data?.items ?? []} />
        </>
      ) : null}
    </main>
  )
}
