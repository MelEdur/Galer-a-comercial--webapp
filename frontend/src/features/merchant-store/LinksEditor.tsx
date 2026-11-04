import type { ReactElement } from 'react'

export interface LinkEntry {
  label: string
  url: string
}

interface LinksEditorProps {
  links: LinkEntry[]
  maxLinks: number
  error?: string
  onAdd: () => void
  onChange: (index: number, field: 'label' | 'url', value: string) => void
  onRemove: (index: number) => void
}

const inputClass =
  'w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200'

export function LinksEditor({
  links,
  maxLinks,
  error,
  onAdd,
  onChange,
  onRemove,
}: LinksEditorProps): ReactElement {
  const limitReached = links.length >= maxLinks

  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Enlaces</h2>
        <p className="mt-1 text-xs text-slate-500">
          Redes sociales, sitio web u otros enlaces externos. Máximo {maxLinks}.
        </p>
      </div>

      {links.length === 0 ? (
        <p className="text-sm text-slate-500">No hay enlaces añadidos.</p>
      ) : (
        <div className="space-y-2">
          {links.map((link, index) => (
            <div
              key={index}
              className="grid grid-cols-1 gap-2 rounded-md border border-slate-200 p-3 sm:grid-cols-[1fr_2fr_auto]"
            >
              <input
                type="text"
                aria-label={`Etiqueta del enlace ${index + 1}`}
                value={link.label}
                maxLength={60}
                placeholder="Etiqueta"
                onChange={(event) => onChange(index, 'label', event.target.value)}
                className={inputClass}
              />
              <input
                type="url"
                aria-label={`URL del enlace ${index + 1}`}
                value={link.url}
                maxLength={500}
                placeholder="https://ejemplo.com"
                onChange={(event) => onChange(index, 'url', event.target.value)}
                className={inputClass}
              />
              <button
                type="button"
                onClick={() => onRemove(index)}
                aria-label={`Quitar enlace ${index + 1}`}
                className="self-start rounded-md border border-slate-300 px-3 py-2 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100"
              >
                Quitar
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="space-y-2">
        <button
          type="button"
          onClick={onAdd}
          disabled={limitReached}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100 disabled:cursor-not-allowed disabled:border-slate-200 disabled:text-slate-400"
        >
          Agregar enlace
        </button>
        {limitReached ? (
          <p className="text-xs text-slate-500">
            Has alcanzado el máximo de {maxLinks} enlaces.
          </p>
        ) : null}
      </div>

      {error ? (
        <p role="alert" className="text-xs text-red-600">
          {error}
        </p>
      ) : null}
    </section>
  )
}
