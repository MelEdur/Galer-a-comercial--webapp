import { useState } from 'react'
import type { FormEvent, ReactElement } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError } from '../../lib/http'
import { useAuth } from './AuthContext'

export function LoginPage(): ReactElement {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      const currentUser = await login(email.trim(), password)
      navigate(currentUser.role === 'admin' ? '/admin' : '/comerciante', {
        replace: true,
      })
    } catch (submitError) {
      if (submitError instanceof ApiError && submitError.status === 401) {
        setError('Credenciales inválidas. Revisa el correo y la contraseña.')
      } else {
        setError('No se ha podido iniciar sesión. Inténtalo de nuevo más tarde.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center gap-8 px-6 py-16">
      <header className="space-y-2 text-center">
        <p className="text-xs font-semibold tracking-wide text-indigo-600 uppercase">
          Galería Comercial
        </p>
        <h1 className="text-3xl font-bold text-slate-900">Iniciar sesión</h1>
        <p className="text-sm text-slate-600">
          Accede con tu cuenta para gestionar la galería y tu local.
        </p>
      </header>

      <form
        onSubmit={handleSubmit}
        className="space-y-5 rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
        noValidate
      >
        {error ? (
          <p
            role="alert"
            className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"
          >
            {error}
          </p>
        ) : null}

        <div className="space-y-1">
          <label htmlFor="login-email" className="block text-sm font-medium text-slate-700">
            Correo electrónico
          </label>
          <input
            id="login-email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          />
        </div>

        <div className="space-y-1">
          <label htmlFor="login-password" className="block text-sm font-medium text-slate-700">
            Contraseña
          </label>
          <input
            id="login-password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200"
          />
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:cursor-not-allowed disabled:bg-indigo-300"
        >
          {isSubmitting ? 'Iniciando sesión…' : 'Iniciar sesión'}
        </button>
      </form>
    </main>
  )
}
