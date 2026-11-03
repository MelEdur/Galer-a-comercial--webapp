import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import type { FormEvent, ReactElement } from 'react'
import { ApiError } from '../../lib/http'
import { createMerchant } from './api'
import type { StoreAdmin } from './types'

interface MerchantFormProps {
  stores: StoreAdmin[]
}

interface FieldErrors {
  email?: string
  fullName?: string
  password?: string
  store?: string
}

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function describeError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 409:
        return 'Ya existe un comerciante con ese correo o el local ya está ocupado.'
      case 403:
        return 'No tienes permisos para crear comerciantes.'
      case 401:
        return 'Tu sesión ha caducado. Vuelve a iniciar sesión.'
      case 404:
        return 'El local seleccionado no existe.'
      case 422:
        return 'Revisa los datos del formulario.'
      default:
        return error.message
    }
  }

  return 'No se ha podido crear el comerciante. Inténtalo de nuevo.'
}

export function MerchantForm({ stores }: MerchantFormProps): ReactElement {
  const queryClient = useQueryClient()

  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')
  const [storeId, setStoreId] = useState('')
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})
  const [formError, setFormError] = useState<string | null>(null)

  const availableStores = stores.filter((store) => store.merchant === null)

  const mutation = useMutation({
    mutationFn: createMerchant,
    onSuccess: () => {
      setEmail('')
      setFullName('')
      setPassword('')
      setStoreId('')
      setFieldErrors({})
      setFormError(null)
      void queryClient.invalidateQueries({ queryKey: ['admin', 'merchants'] })
      void queryClient.invalidateQueries({ queryKey: ['admin', 'stores'] })
    },
    onError: (error) => {
      setFormError(describeError(error))
    },
  })

  function validate(): FieldErrors {
    const errors: FieldErrors = {}
    const trimmedEmail = email.trim()
    const trimmedName = fullName.trim()

    if (!trimmedEmail) {
      errors.email = 'El correo es obligatorio.'
    } else if (!EMAIL_PATTERN.test(trimmedEmail)) {
      errors.email = 'Introduce un correo válido.'
    }

    if (!trimmedName) {
      errors.fullName = 'El nombre completo es obligatorio.'
    }

    if (password.length < 8 || password.length > 72) {
      errors.password = 'La contraseña debe tener entre 8 y 72 caracteres.'
    }

    if (!storeId) {
      errors.store = 'Selecciona un local disponible.'
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

    mutation.mutate({
      email: email.trim().toLowerCase(),
      full_name: fullName.trim(),
      password,
      store_id: Number(storeId),
    })
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">Alta de comerciante</h2>
      <p className="mt-1 text-sm text-slate-600">
        Crea la cuenta y asígnala a uno de los locales disponibles.
      </p>

      <form onSubmit={handleSubmit} className="mt-4 space-y-4" noValidate>
        {formError ? (
          <p
            role="alert"
            className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
          >
            {formError}
          </p>
        ) : null}

        <div className="space-y-1">
          <label
            htmlFor="merchant-email"
            className="block text-sm font-medium text-slate-700"
          >
            Correo electrónico
          </label>
          <input
            id="merchant-email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          />
          {fieldErrors.email ? (
            <p className="text-xs text-red-600">{fieldErrors.email}</p>
          ) : null}
        </div>

        <div className="space-y-1">
          <label
            htmlFor="merchant-full-name"
            className="block text-sm font-medium text-slate-700"
          >
            Nombre completo
          </label>
          <input
            id="merchant-full-name"
            type="text"
            autoComplete="name"
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          />
          {fieldErrors.fullName ? (
            <p className="text-xs text-red-600">{fieldErrors.fullName}</p>
          ) : null}
        </div>

        <div className="space-y-1">
          <label
            htmlFor="merchant-password"
            className="block text-sm font-medium text-slate-700"
          >
            Contraseña
          </label>
          <input
            id="merchant-password"
            type="password"
            autoComplete="new-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          />
          {fieldErrors.password ? (
            <p className="text-xs text-red-600">{fieldErrors.password}</p>
          ) : null}
        </div>

        <div className="space-y-1">
          <label htmlFor="merchant-store" className="block text-sm font-medium text-slate-700">
            Local
          </label>
          <select
            id="merchant-store"
            value={storeId}
            onChange={(event) => setStoreId(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          >
            <option value="">Selecciona un local</option>
            {availableStores.map((store) => (
              <option key={store.id} value={store.id}>
                Local {store.number} · {store.name}
              </option>
            ))}
          </select>
          {availableStores.length === 0 ? (
            <p className="text-xs text-slate-500">
              No hay locales disponibles en este momento.
            </p>
          ) : null}
          {fieldErrors.store ? (
            <p className="text-xs text-red-600">{fieldErrors.store}</p>
          ) : null}
        </div>

        <button
          type="submit"
          disabled={mutation.isPending || availableStores.length === 0}
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:cursor-not-allowed disabled:bg-indigo-300"
        >
          {mutation.isPending ? 'Creando…' : 'Crear comerciante'}
        </button>
      </form>
    </section>
  )
}
