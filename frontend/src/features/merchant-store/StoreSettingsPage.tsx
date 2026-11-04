import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import type { FormEvent, ReactElement } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { ApiError } from '../../lib/http'
import { getMyStore, updateMyStore } from './api'
import { ContactSection } from './ContactSection'
import { GeneralSection } from './GeneralSection'
import { DAY_LABELS, HoursEditor } from './HoursEditor'
import type { HourEntry } from './HoursEditor'
import { LinksEditor } from './LinksEditor'
import type { LinkEntry } from './LinksEditor'
import { merchantStoreKeys } from './queryKeys'
import type { MerchantStore, StoreUpdateInput } from './types'

const MAX_LINKS = 10
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const HTTP_URL_PATTERN = /^https?:\/\/.+/i

interface StoreFormState {
  name: string
  description: string
  logoUrl: string
  email: string
  phone: string
  whatsapp: string
  hours: HourEntry[]
  links: LinkEntry[]
}

interface FormErrors {
  name?: string
  description?: string
  logoUrl?: string
  email?: string
  phone?: string
  whatsapp?: string
  hours?: string
  links?: string
}

function normalizeTime(value: string): string {
  return value.length >= 5 ? value.slice(0, 5) : value
}

function toFormState(store: MerchantStore): StoreFormState {
  return {
    name: store.name,
    description: store.description ?? '',
    logoUrl: store.logo_url ?? '',
    email: store.email ?? '',
    phone: store.phone ?? '',
    whatsapp: store.whatsapp ?? '',
    hours: store.hours.map((hour) => ({
      dayOfWeek: hour.day_of_week,
      opensAt: normalizeTime(hour.opens_at),
      closesAt: normalizeTime(hour.closes_at),
    })),
    links: store.links.map((link) => ({ label: link.label, url: link.url })),
  }
}

function formatSide(side: string): string {
  switch (side) {
    case 'left':
      return 'Izquierda'
    case 'right':
      return 'Derecha'
    case 'back':
      return 'Fondo'
    default:
      return side
  }
}

function describeLoadError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 401:
        return 'Tu sesión ha caducado. Vuelve a iniciar sesión.'
      case 403:
        return 'No tienes permisos para consultar este local o tu cuenta no tiene un local asignado.'
      case 404:
        return 'No se ha encontrado la información del local.'
      default:
        return 'No se ha podido cargar la información del local. Inténtalo de nuevo.'
    }
  }

  return 'No se ha podido cargar la información del local. Inténtalo de nuevo.'
}

function describeSaveError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 401:
        return 'Tu sesión ha caducado. Vuelve a iniciar sesión.'
      case 403:
        return 'No tienes permisos para modificar este local.'
      case 404:
        return 'No se ha encontrado la información del local.'
      case 422:
        return 'Revisa los datos del formulario: hay valores no válidos.'
      default:
        return 'No se han podido guardar los cambios. Inténtalo de nuevo.'
    }
  }

  return 'No se han podido guardar los cambios. Inténtalo de nuevo.'
}

function validateForm(form: StoreFormState): FormErrors {
  const errors: FormErrors = {}
  const trimmedName = form.name.trim()

  if (trimmedName.length === 0) {
    errors.name = 'El nombre es obligatorio.'
  } else if (trimmedName.length > 120) {
    errors.name = 'El nombre no puede superar los 120 caracteres.'
  }

  if (form.description.trim().length > 2000) {
    errors.description = 'La descripción no puede superar los 2000 caracteres.'
  }

  const logoUrl = form.logoUrl.trim()

  if (logoUrl.length > 0) {
    if (!HTTP_URL_PATTERN.test(logoUrl)) {
      errors.logoUrl = 'La URL del logo debe empezar por http:// o https://.'
    } else if (logoUrl.length > 500) {
      errors.logoUrl = 'La URL del logo no puede superar los 500 caracteres.'
    }
  }

  const email = form.email.trim()

  if (email.length > 0 && !EMAIL_PATTERN.test(email)) {
    errors.email = 'Introduce un correo electrónico válido.'
  }

  if (form.phone.trim().length > 30) {
    errors.phone = 'El teléfono no puede superar los 30 caracteres.'
  }

  if (form.whatsapp.trim().length > 30) {
    errors.whatsapp = 'El WhatsApp no puede superar los 30 caracteres.'
  }

  const filledHours = form.hours.filter(
    (hour) => hour.opensAt.length > 0 || hour.closesAt.length > 0,
  )

  for (const hour of filledHours) {
    const dayLabel = DAY_LABELS[hour.dayOfWeek] ?? `día ${hour.dayOfWeek + 1}`

    if (hour.opensAt.length === 0 || hour.closesAt.length === 0) {
      errors.hours = `Completa la apertura y el cierre del tramo de ${dayLabel.toLowerCase()}.`
      break
    }

    if (hour.closesAt <= hour.opensAt) {
      errors.hours = `El cierre del tramo de ${dayLabel.toLowerCase()} debe ser posterior a la apertura.`
      break
    }
  }

  const filledLinks = form.links.filter(
    (link) => link.label.trim().length > 0 || link.url.trim().length > 0,
  )

  if (filledLinks.length > MAX_LINKS) {
    errors.links = `Puedes añadir como máximo ${MAX_LINKS} enlaces.`
  } else {
    const seenUrls = new Set<string>()

    for (const link of filledLinks) {
      const label = link.label.trim()
      const url = link.url.trim()

      if (label.length === 0 || url.length === 0) {
        errors.links = 'Cada enlace debe tener etiqueta y URL.'
        break
      }

      if (label.length > 60) {
        errors.links = 'La etiqueta de cada enlace no puede superar los 60 caracteres.'
        break
      }

      if (!HTTP_URL_PATTERN.test(url) || url.length > 500) {
        errors.links = 'Cada enlace debe tener una URL válida que empiece por http:// o https://.'
        break
      }

      if (seenUrls.has(url)) {
        errors.links = 'No se pueden repetir las URLs de los enlaces.'
        break
      }

      seenUrls.add(url)
    }
  }

  return errors
}

function buildPayload(form: StoreFormState): StoreUpdateInput {
  const optionalValue = (value: string): string | null => {
    const trimmed = value.trim()
    return trimmed.length > 0 ? trimmed : null
  }

  return {
    name: form.name.trim(),
    description: optionalValue(form.description),
    logo_url: optionalValue(form.logoUrl),
    email: optionalValue(form.email),
    phone: optionalValue(form.phone),
    whatsapp: optionalValue(form.whatsapp),
    hours: form.hours
      .filter((hour) => hour.opensAt.length > 0 && hour.closesAt.length > 0)
      .map((hour) => ({
        day_of_week: hour.dayOfWeek,
        opens_at: normalizeTime(hour.opensAt),
        closes_at: normalizeTime(hour.closesAt),
      })),
    links: form.links
      .filter((link) => link.label.trim().length > 0 && link.url.trim().length > 0)
      .map((link) => ({
        label: link.label.trim(),
        url: link.url.trim(),
      })),
  }
}

export function StoreSettingsPage(): ReactElement {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const { refreshUser } = useAuth()
  const [form, setForm] = useState<StoreFormState | null>(null)
  const [fieldErrors, setFieldErrors] = useState<FormErrors>({})
  const [formError, setFormError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)

  const storeQuery = useQuery({
    queryKey: merchantStoreKeys.store,
    queryFn: getMyStore,
  })

  const store = storeQuery.data

  useEffect(() => {
    if (store && form === null) {
      setForm(toFormState(store))
    }
  }, [store, form])

  const mutation = useMutation({
    mutationFn: updateMyStore,
    onSuccess: async (updatedStore) => {
      queryClient.setQueryData(merchantStoreKeys.store, updatedStore)
      setForm(toFormState(updatedStore))
      setFieldErrors({})
      setFormError(null)
      setSaved(true)
      await queryClient.invalidateQueries({ queryKey: merchantStoreKeys.store })

      try {
        await refreshUser()
      } catch {
        // The saved data is already persisted; keep the current session if the
        // identity refresh fails and still return to the panel.
      }
      navigate('/comerciante', { replace: true })
    },
    onError: (error) => {
      setSaved(false)
      setFormError(describeSaveError(error))
    },
  })

  function updateForm<K extends keyof StoreFormState>(
    field: K,
    value: StoreFormState[K],
  ) {
    setForm((previous) => (previous ? { ...previous, [field]: value } : previous))
    setSaved(false)
  }

  function addHour(dayOfWeek: number) {
    setForm((previous) =>
      previous
        ? {
            ...previous,
            hours: [
              ...previous.hours,
              { dayOfWeek, opensAt: '09:00', closesAt: '18:00' },
            ],
          }
        : previous,
    )
    setSaved(false)
  }

  function changeHour(
    index: number,
    field: 'opensAt' | 'closesAt',
    value: string,
  ) {
    setForm((previous) =>
      previous
        ? {
            ...previous,
            hours: previous.hours.map((hour, position) =>
              position === index ? { ...hour, [field]: value } : hour,
            ),
          }
        : previous,
    )
    setSaved(false)
  }

  function removeHour(index: number) {
    setForm((previous) =>
      previous
        ? {
            ...previous,
            hours: previous.hours.filter((_, position) => position !== index),
          }
        : previous,
    )
    setSaved(false)
  }

  function addLink() {
    setForm((previous) =>
      previous
        ? { ...previous, links: [...previous.links, { label: '', url: '' }] }
        : previous,
    )
    setSaved(false)
  }

  function changeLink(index: number, field: 'label' | 'url', value: string) {
    setForm((previous) =>
      previous
        ? {
            ...previous,
            links: previous.links.map((link, position) =>
              position === index ? { ...link, [field]: value } : link,
            ),
          }
        : previous,
    )
    setSaved(false)
  }

  function removeLink(index: number) {
    setForm((previous) =>
      previous
        ? {
            ...previous,
            links: previous.links.filter((_, position) => position !== index),
          }
        : previous,
    )
    setSaved(false)
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!form) {
      return
    }

    setSaved(false)
    setFormError(null)

    const errors = validateForm(form)
    setFieldErrors(errors)

    if (Object.keys(errors).length > 0) {
      return
    }

    mutation.mutate(buildPayload(form))
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col gap-8 px-6 py-16">
      <header className="space-y-2">
        <p className="text-xs font-semibold tracking-wide text-indigo-600 uppercase">
          Mi local
        </p>
        <h1 className="text-3xl font-bold text-slate-900">Información del local</h1>
        <p className="text-sm text-slate-600">
          Consulta y actualiza los datos públicos de tu local.
        </p>
        <p>
          <Link
            to="/comerciante"
            className="text-sm font-medium text-indigo-600 hover:text-indigo-700"
          >
            ← Volver al panel
          </Link>
        </p>
      </header>

      {storeQuery.isPending ? (
        <p aria-live="polite" className="text-sm text-slate-600">
          Cargando información del local…
        </p>
      ) : null}

      {storeQuery.isError ? (
        <p
          role="alert"
          className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
        >
          {describeLoadError(storeQuery.error)}
        </p>
      ) : null}

      {store && form ? (
        <>
          <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Ubicación</h2>
            <dl className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div>
                <dt className="text-xs font-semibold tracking-wide text-slate-500 uppercase">
                  Número
                </dt>
                <dd className="mt-1 text-sm text-slate-900">{store.number}</dd>
              </div>
              <div>
                <dt className="text-xs font-semibold tracking-wide text-slate-500 uppercase">
                  Lado
                </dt>
                <dd className="mt-1 text-sm text-slate-900">
                  {formatSide(store.side)}
                </dd>
              </div>
              <div>
                <dt className="text-xs font-semibold tracking-wide text-slate-500 uppercase">
                  Posición
                </dt>
                <dd className="mt-1 text-sm text-slate-900">{store.position}</dd>
              </div>
            </dl>
            <p className="mt-3 text-xs text-slate-500">
              El número, el lado y la posición los asigna la administración de la galería.
            </p>
          </section>

          <form
            onSubmit={handleSubmit}
            className="space-y-8 rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
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

            {saved ? (
              <p
                role="status"
                className="rounded-md border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-800"
              >
                Los cambios se han guardado correctamente.
              </p>
            ) : null}

            <GeneralSection
              name={form.name}
              description={form.description}
              logoUrl={form.logoUrl}
              errors={fieldErrors}
              onNameChange={(value) => updateForm('name', value)}
              onDescriptionChange={(value) => updateForm('description', value)}
              onLogoUrlChange={(value) => updateForm('logoUrl', value)}
            />

            <ContactSection
              email={form.email}
              phone={form.phone}
              whatsapp={form.whatsapp}
              errors={fieldErrors}
              onEmailChange={(value) => updateForm('email', value)}
              onPhoneChange={(value) => updateForm('phone', value)}
              onWhatsappChange={(value) => updateForm('whatsapp', value)}
            />

            <HoursEditor
              hours={form.hours}
              error={fieldErrors.hours}
              onAdd={addHour}
              onChange={changeHour}
              onRemove={removeHour}
            />

            <LinksEditor
              links={form.links}
              maxLinks={MAX_LINKS}
              error={fieldErrors.links}
              onAdd={addLink}
              onChange={changeLink}
              onRemove={removeLink}
            />

            <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
              <Link
                to="/comerciante"
                className="rounded-md border border-slate-300 px-4 py-2 text-center text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100"
              >
                Cancelar
              </Link>
              <button
                type="submit"
                disabled={mutation.isPending}
                className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:cursor-not-allowed disabled:bg-indigo-300"
              >
                {mutation.isPending ? 'Guardando…' : 'Guardar cambios'}
              </button>
            </div>
          </form>
        </>
      ) : null}
    </main>
  )
}
