import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import type { ReactElement } from 'react'
import { ApiError } from '../../lib/http'
import { restoreProduct } from './api'
import { merchantCatalogKeys } from './queryKeys'
import type { Product } from './types'

interface RestoreProductButtonProps {
  product: Product
}

function describeRestoreError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 401:
        return 'Tu sesión ha caducado. Vuelve a iniciar sesión.'
      case 403:
        return 'No tienes permisos para restaurar este producto.'
      case 404:
        return 'El producto no existe o ya no está disponible.'
      default:
        return error.message
    }
  }

  return 'No se ha podido restaurar el producto. Inténtalo de nuevo.'
}

export function RestoreProductButton({ product }: RestoreProductButtonProps): ReactElement {
  const queryClient = useQueryClient()
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () => restoreProduct(product.id),
    onMutate: () => {
      setError(null)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: merchantCatalogKeys.products })
      void queryClient.invalidateQueries({
        queryKey: merchantCatalogKeys.product(product.id),
      })
    },
    onError: (mutationError) => {
      setError(describeRestoreError(mutationError))
    },
  })

  function handleRestore() {
    const confirmed = window.confirm(
      `¿Restaurar «${product.name}»? Volverá a aparecer entre los productos vigentes.`,
    )

    if (!confirmed) {
      return
    }

    mutation.mutate()
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <button
        type="button"
        onClick={handleRestore}
        disabled={mutation.isPending}
        className="rounded-md border border-emerald-300 px-3 py-1.5 text-xs font-semibold text-emerald-700 transition-colors hover:bg-emerald-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {mutation.isPending ? 'Restaurando…' : 'Restaurar'}
      </button>
      {error ? (
        <p role="alert" className="text-right text-xs text-red-600">
          {error}
        </p>
      ) : null}
    </div>
  )
}
