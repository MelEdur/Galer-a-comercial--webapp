import type { ReactElement } from 'react'

interface ContactSectionProps {
  email: string
  phone: string
  whatsapp: string
  errors: {
    email?: string
    phone?: string
    whatsapp?: string
  }
  onEmailChange: (value: string) => void
  onPhoneChange: (value: string) => void
  onWhatsappChange: (value: string) => void
}

const inputClass =
  'w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200'

export function ContactSection({
  email,
  phone,
  whatsapp,
  errors,
  onEmailChange,
  onPhoneChange,
  onWhatsappChange,
}: ContactSectionProps): ReactElement {
  return (
    <section className="space-y-4">
      <h2 className="text-lg font-semibold text-slate-900">Contacto</h2>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="space-y-1 sm:col-span-2">
          <label
            htmlFor="store-email"
            className="block text-sm font-medium text-slate-700"
          >
            Correo electrónico
          </label>
          <input
            id="store-email"
            type="email"
            value={email}
            maxLength={320}
            onChange={(event) => onEmailChange(event.target.value)}
            className={inputClass}
          />
          {errors.email ? <p className="text-xs text-red-600">{errors.email}</p> : null}
        </div>

        <div className="space-y-1">
          <label
            htmlFor="store-phone"
            className="block text-sm font-medium text-slate-700"
          >
            Teléfono
          </label>
          <input
            id="store-phone"
            type="tel"
            value={phone}
            maxLength={30}
            onChange={(event) => onPhoneChange(event.target.value)}
            className={inputClass}
          />
          {errors.phone ? <p className="text-xs text-red-600">{errors.phone}</p> : null}
        </div>

        <div className="space-y-1">
          <label
            htmlFor="store-whatsapp"
            className="block text-sm font-medium text-slate-700"
          >
            WhatsApp
          </label>
          <input
            id="store-whatsapp"
            type="tel"
            value={whatsapp}
            maxLength={30}
            onChange={(event) => onWhatsappChange(event.target.value)}
            className={inputClass}
          />
          {errors.whatsapp ? (
            <p className="text-xs text-red-600">{errors.whatsapp}</p>
          ) : null}
        </div>
      </div>
    </section>
  )
}
