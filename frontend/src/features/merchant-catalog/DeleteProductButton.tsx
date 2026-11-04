import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import type { ReactElement } from 'react'
import { ApiError } from '../../lib/http'
import { deleteProduct } from './api'
import { merchantCatalogKeys } from './queryKeys'
import type { Product } from './types'

interface DeleteProductButtonProps {
  product: Product
}

function describeDeleteError(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 401:
        return 'Tu sesión ha caducado. Vuelve a iniciar sesión.'
      case 403:
        return 'No tienes permisos para dar de baja este producto.'
      case 404:
        return 'El producto no existe o ya no está disponible.'
      default:
        return error.message
    }
  }

  return 'No se ha podido dar de baja el producto. Inténtalo de nuevo.'
}

export function DeleteProductButton({ product }: DeleteProductButtonProps): ReactElement {
  const queryClient = useQueryClient()
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () => deleteProduct(product.id),
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
      setError(describeDeleteError(mutationError))
    },
  })

  function handleDelete() {
    const confirmed = window.confirm(
      product.deleted_at
        ? `«${product.name}» ya está eliminado. ¿Repetir la baja?`
        : `¿Dar de baja «${product.name}»?`,
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
        onClick={handleDelete}
        disabled={mutation.isPending}
        className="rounded-md border border-red-300 px-3 py-1.5 text-xs font-semibold text-red-700 transition-colors hover:bg-red-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-400 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {mutation.isPending ? 'Dando de baja…' : 'Dar de baja'}
      </button>
      {error ? (
        <p role="alert" className="text-right text-xs text-red-600">
          {error}
        </p>
      ) : null}
    </div>
  )
}
