import { useState } from 'react'
import type { ReactElement } from 'react'

interface GeneralSectionProps {
  name: string
  description: string
  logoUrl: string
  errors: {
    name?: string
    description?: string
    logoUrl?: string
  }
  onNameChange: (value: string) => void
  onDescriptionChange: (value: string) => void
  onLogoUrlChange: (value: string) => void
}

const inputClass =
  'w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200'

function isHttpUrl(value: string): boolean {
  return /^https?:\/\/.+/i.test(value.trim())
}

export function GeneralSection({
  name,
  description,
  logoUrl,
  errors,
  onNameChange,
  onDescriptionChange,
  onLogoUrlChange,
}: GeneralSectionProps): ReactElement {
  const [failedPreviewUrl, setFailedPreviewUrl] = useState<string | null>(null)
  const trimmedLogoUrl = logoUrl.trim()
  const showPreview = isHttpUrl(trimmedLogoUrl) && failedPreviewUrl !== trimmedLogoUrl

  return (
    <section className="space-y-4">
      <h2 className="text-lg font-semibold text-slate-900">Datos generales</h2>

      <div className="space-y-1">
        <label htmlFor="store-name" className="block text-sm font-medium text-slate-700">
          Nombre
        </label>
        <input
          id="store-name"
          type="text"
          value={name}
          maxLength={120}
          onChange={(event) => onNameChange(event.target.value)}
          className={inputClass}
        />
        {errors.name ? <p className="text-xs text-red-600">{errors.name}</p> : null}
      </div>

      <div className="space-y-1">
        <label
          htmlFor="store-description"
          className="block text-sm font-medium text-slate-700"
        >
          Descripción
        </label>
        <textarea
          id="store-description"
          rows={4}
          value={description}
          maxLength={2000}
          onChange={(event) => onDescriptionChange(event.target.value)}
          className={inputClass}
        />
        {errors.description ? (
          <p className="text-xs text-red-600">{errors.description}</p>
        ) : null}
      </div>

      <div className="space-y-2">
        <label
          htmlFor="store-logo-url"
          className="block text-sm font-medium text-slate-700"
        >
          URL del logo
        </label>
        <input
          id="store-logo-url"
          type="url"
          value={logoUrl}
          maxLength={500}
          placeholder="https://ejemplo.com/logo.png"
          onChange={(event) => onLogoUrlChange(event.target.value)}
          className={inputClass}
        />
        {errors.logoUrl ? (
          <p className="text-xs text-red-600">{errors.logoUrl}</p>
        ) : null}
        {showPreview ? (
          <div className="flex items-center gap-3 rounded-md border border-slate-200 bg-slate-50 p-3">
            <img
              src={trimmedLogoUrl}
              alt="Vista previa del logo"
              className="h-16 w-16 rounded-md border border-slate-200 bg-white object-contain"
              onError={() => setFailedPreviewUrl(trimmedLogoUrl)}
            />
            <p className="text-xs text-slate-500">Vista previa del logo</p>
          </div>
        ) : null}
      </div>
    </section>
  )
}
