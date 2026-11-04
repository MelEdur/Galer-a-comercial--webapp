import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import type { FormEvent, ReactElement } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ApiError } from '../../lib/http'
import {
  createProduct,
  getProduct,
  listCategories,
  updateProduct,
} from './api'
import { merchantCatalogKeys } from './queryKeys'
import type { ProductInput } from './types'

interface ImageField {
  url: string
  altText: string
}

interface FormErrors {
  name?: string
  price?: string
  offerPrice?: string
  categories?: string
  images?: string
}

const MAX_IMAGES = 5
const PRICE_PATTERN = /^-?\d+([.,]\d{1,2})?$/

function normalizePrice(value: string): string {
  return value.trim().replace(',', '.')
}

function describeFormError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 401:
        return 'Tu sesión ha caducado. Vuelve a iniciar sesión.'
      case 403:
        return 'No tienes permisos para administrar este catálogo.'
      case 404:
        return 'El producto no existe, no pertenece a tu local o ya no está disponible.'
      case 409:
        return 'No se puede editar un producto eliminado.'
      case 422:
        return 'Revisa los datos del formulario: hay valores no válidos.'
      default:
        return error.message
    }
  }

  return 'No se ha podido guardar el producto. Inténtalo de nuevo.'
}

export function ProductFormPage(): ReactElement {
  const { productId } = useParams<{ productId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const productIdNumber = Number(productId)
  const isEdit = Boolean(productId) && Number.isInteger(productIdNumber)

  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [price, setPrice] = useState('')
  const [offerPrice, setOfferPrice] = useState('')
  const [categoryIds, setCategoryIds] = useState<number[]>([])
  const [images, setImages] = useState<ImageField[]>([])
  const [fieldErrors, setFieldErrors] = useState<FormErrors>({})
  const [formError, setFormError] = useState<string | null>(null)

  const categoriesQuery = useQuery({
    queryKey: merchantCatalogKeys.categories,
    queryFn: listCategories,
  })

  const productQuery = useQuery({
    queryKey: merchantCatalogKeys.product(productIdNumber),
    queryFn: () => getProduct(productIdNumber),
    enabled: isEdit,
  })

  useEffect(() => {
    const product = productQuery.data

    if (!product) {
      return
    }

    setName(product.name)
    setDescription(product.description ?? '')
    setPrice(product.price)
    setOfferPrice(product.offer_price ?? '')
    setCategoryIds(product.categories.map((category) => category.id))
    setImages(
      product.images.map((image) => ({
        url: image.url,
        altText: image.alt_text ?? '',
      })),
    )
  }, [productQuery.data])

  const mutation = useMutation({
    mutationFn: (input: ProductInput) =>
      isEdit
        ? updateProduct(productIdNumber, input)
        : createProduct(input),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: merchantCatalogKeys.products })
      if (isEdit) {
        void queryClient.invalidateQueries({
          queryKey: merchantCatalogKeys.product(productIdNumber),
        })
      }
      navigate('/comerciante/productos')
    },
    onError: (error) => {
      setFormError(describeFormError(error))
    },
  })

  function toggleCategory(id: number) {
    setCategoryIds((previous) =>
      previous.includes(id)
        ? previous.filter((categoryId) => categoryId !== id)
        : [...previous, id],
    )
  }

  function addImage() {
    setImages((previous) => [...previous, { url: '', altText: '' }])
  }

  function updateImage(index: number, field: keyof ImageField, value: string) {
    setImages((previous) =>
      previous.map((image, position) =>
        position === index ? { ...image, [field]: value } : image,
      ),
    )
  }

  function removeImage(index: number) {
    setImages((previous) => previous.filter((_, position) => position !== index))
  }

  function validate(): FormErrors {
    const errors: FormErrors = {}

    if (name.trim().length === 0) {
      errors.name = 'El nombre es obligatorio.'
    }

    const normalizedPrice = normalizePrice(price)

    if (normalizedPrice.length === 0) {
      errors.price = 'El precio es obligatorio.'
    } else if (!PRICE_PATTERN.test(price.trim())) {
      errors.price = 'Introduce un precio válido con hasta 2 decimales.'
    } else if (Number(normalizedPrice) < 0) {
      errors.price = 'El precio no puede ser negativo.'
    }

    const normalizedOffer = normalizePrice(offerPrice)

    if (normalizedOffer.length > 0) {
      if (!PRICE_PATTERN.test(offerPrice.trim())) {
        errors.offerPrice = 'Introduce un precio de oferta válido con hasta 2 decimales.'
      } else if (Number(normalizedOffer) < 0) {
        errors.offerPrice = 'El precio de oferta no puede ser negativo.'
      } else if (!errors.price && Number(normalizedOffer) >= Number(normalizedPrice)) {
        errors.offerPrice = 'El precio de oferta debe ser menor que el precio.'
      }
    }

    if (categoryIds.length === 0) {
      errors.categories = 'Selecciona al menos una categoría.'
    }

    const filledImages = images.filter(
      (image) => image.url.trim().length > 0 || image.altText.trim().length > 0,
    )

    if (filledImages.length > MAX_IMAGES) {
      errors.images = 'Puedes añadir como máximo 5 imágenes.'
    } else if (
      filledImages.some(
        (image) =>
          image.url.trim().length === 0 ||
          !/^https?:\/\/.+/i.test(image.url.trim()),
      )
    ) {
      errors.images =
        'Cada imagen debe tener una URL válida que empiece por http:// o https://.'
    }

    return errors
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)

    const errors = validate()
    setFieldErrors(errors)

    if (Object.keys(errors).length > 0) {
      return
    }

    const trimmedDescription = description.trim()
    const preparedImages = images
      .map((image) => ({
        url: image.url.trim(),
        altText: image.altText.trim(),
      }))
      .filter((image) => image.url.length > 0)
      .map((image) =>
        image.altText.length > 0
          ? { url: image.url, alt_text: image.altText }
          : { url: image.url },
      )

    const payload: ProductInput = {
      name: name.trim(),
      price: normalizePrice(price),
      category_ids: categoryIds,
      images: preparedImages,
    }

    if (trimmedDescription.length > 0) {
      payload.description = trimmedDescription
    } else if (isEdit) {
      payload.description = null
    }

    const normalizedOffer = normalizePrice(offerPrice)

    if (normalizedOffer.length > 0) {
      payload.offer_price = normalizedOffer
    } else if (isEdit) {
      payload.offer_price = null
    }

    mutation.mutate(payload)
  }

  const isLoading = categoriesQuery.isPending || (isEdit && productQuery.isPending)

  if (isEdit && productQuery.isError) {
    return (
      <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col gap-6 px-6 py-16">
        <h1 className="text-3xl font-bold text-slate-900">Editar producto</h1>
        <p
          role="alert"
          className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          No se ha podido cargar el producto. Puede que no exista o no pertenezca a
          tu local.
        </p>
        <Link
          to="/comerciante/productos"
          className="text-sm font-medium text-indigo-600 hover:text-indigo-700"
        >
          ← Volver al listado
        </Link>
      </main>
    )
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col gap-8 px-6 py-16">
      <header className="space-y-2">
        <p className="text-xs font-semibold tracking-wide text-indigo-600 uppercase">
          Mi local
        </p>
        <h1 className="text-3xl font-bold text-slate-900">
          {isEdit ? 'Editar producto' : 'Nuevo producto'}
        </h1>
        <p className="text-sm text-slate-600">
          {isEdit
            ? 'Modifica los datos del producto y guarda los cambios.'
            : 'Completa los datos para añadir un producto a tu catálogo.'}
        </p>
        <p>
          <Link
            to="/comerciante/productos"
            className="text-sm font-medium text-indigo-600 hover:text-indigo-700"
          >
            ← Volver al listado
          </Link>
        </p>
      </header>

      {isLoading ? (
        <p aria-live="polite" className="text-sm text-slate-600">
          Cargando producto y categorías…
        </p>
      ) : (
        <form
          onSubmit={handleSubmit}
          className="space-y-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
          noValidate
        >
          {formError ? (
            <p
              role="alert"
              className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
            >
              {formError}
            </p>
          ) : null}

          <div className="space-y-1">
            <label htmlFor="product-name" className="block text-sm font-medium text-slate-700">
              Nombre
            </label>
            <input
              id="product-name"
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            />
            {fieldErrors.name ? (
              <p className="text-xs text-red-600">{fieldErrors.name}</p>
            ) : null}
          </div>

          <div className="space-y-1">
            <label
              htmlFor="product-description"
              className="block text-sm font-medium text-slate-700"
            >
              Descripción
            </label>
            <textarea
              id="product-description"
              rows={3}
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
            />
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="space-y-1">
              <label
                htmlFor="product-price"
                className="block text-sm font-medium text-slate-700"
              >
                Precio
              </label>
              <input
                id="product-price"
                type="text"
                inputMode="decimal"
                value={price}
                onChange={(event) => setPrice(event.target.value)}
                placeholder="1500.00"
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              />
              {fieldErrors.price ? (
                <p className="text-xs text-red-600">{fieldErrors.price}</p>
              ) : null}
            </div>

            <div className="space-y-1">
              <label
                htmlFor="product-offer-price"
                className="block text-sm font-medium text-slate-700"
              >
                Precio de oferta
              </label>
              <input
                id="product-offer-price"
                type="text"
                inputMode="decimal"
                value={offerPrice}
                onChange={(event) => setOfferPrice(event.target.value)}
                placeholder="Opcional"
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
              />
              {fieldErrors.offerPrice ? (
                <p className="text-xs text-red-600">{fieldErrors.offerPrice}</p>
              ) : null}
            </div>
          </div>

          <fieldset className="space-y-2">
            <legend className="text-sm font-medium text-slate-700">Categorías</legend>
            {categoriesQuery.isError ? (
              <p role="alert" className="text-xs text-red-600">
                No se han podido cargar las categorías.
              </p>
            ) : null}
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {categoriesQuery.data?.map((category) => (
                <label
                  key={category.id}
                  className="flex items-center gap-2 text-sm text-slate-700"
                >
                  <input
                    type="checkbox"
                    checked={categoryIds.includes(category.id)}
                    onChange={() => toggleCategory(category.id)}
                    className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-200"
                  />
                  {category.name}
                </label>
              ))}
            </div>
            {fieldErrors.categories ? (
              <p className="text-xs text-red-600">{fieldErrors.categories}</p>
            ) : null}
          </fieldset>

          <fieldset className="space-y-2">
            <legend className="text-sm font-medium text-slate-700">
              Imágenes (máximo 5)
            </legend>
            <p className="text-xs text-slate-500">
              Añade imágenes mediante URL. La primera será la imagen principal.
            </p>

            {images.map((image, index) => (
              <div
                key={index}
                className="grid grid-cols-1 gap-2 rounded-md border border-slate-200 p-3 sm:grid-cols-[2fr_1fr_auto]"
              >
                <input
                  type="url"
                  aria-label={`URL de la imagen ${index + 1}`}
                  value={image.url}
                  onChange={(event) => updateImage(index, 'url', event.target.value)}
                  placeholder="https://ejemplo.com/imagen.jpg"
                  className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                />
                <input
                  type="text"
                  aria-label={`Texto alternativo ${index + 1}`}
                  value={image.altText}
                  onChange={(event) => updateImage(index, 'altText', event.target.value)}
                  placeholder="Texto alternativo"
                  className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
                />
                <button
                  type="button"
                  onClick={() => removeImage(index)}
                  className="self-start rounded-md border border-slate-300 px-3 py-2 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100"
                >
                  Quitar
                </button>
              </div>
            ))}

            <button
              type="button"
              onClick={addImage}
              className="rounded-md border border-slate-300 px-3 py-2 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100"
            >
              Agregar imagen
            </button>

            {fieldErrors.images ? (
              <p className="text-xs text-red-600">{fieldErrors.images}</p>
            ) : null}
          </fieldset>

          <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
            <Link
              to="/comerciante/productos"
              className="rounded-md border border-slate-300 px-4 py-2 text-center text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100"
            >
              Cancelar
            </Link>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:cursor-not-allowed disabled:bg-indigo-300"
            >
              {mutation.isPending
                ? 'Guardando…'
                : isEdit
                  ? 'Guardar cambios'
                  : 'Crear producto'}
            </button>
          </div>
        </form>
      )}
    </main>
  )
}
