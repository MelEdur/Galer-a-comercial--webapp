import { useState } from 'react'
import type { ReactElement } from 'react'
import type { ProductImageDetail } from './types'

interface ProductGalleryProps {
  images: ProductImageDetail[]
  productName: string
}

export function ProductGallery({
  images,
  productName,
}: ProductGalleryProps): ReactElement {
  const [selectedIndex, setSelectedIndex] = useState(0)

  if (images.length === 0) {
    return (
      <div className="flex aspect-square w-full items-center justify-center rounded-lg border border-slate-200 bg-slate-100">
        <span className="text-sm text-slate-400">Sin imagen</span>
      </div>
    )
  }

  const activeIndex = selectedIndex < images.length ? selectedIndex : 0
  const activeImage = images[activeIndex]

  return (
    <div className="space-y-3">
      <div className="overflow-hidden rounded-lg border border-slate-200 bg-slate-100">
        <img
          src={activeImage.url}
          alt={activeImage.alt_text ?? productName}
          className="aspect-square w-full object-cover"
        />
      </div>

      {images.length > 1 ? (
        <ul className="flex gap-2 overflow-x-auto pb-1">
          {images.map((image, index) => {
            const isSelected = index === activeIndex

            return (
              <li key={image.id} className="shrink-0">
                <button
                  type="button"
                  onClick={() => setSelectedIndex(index)}
                  aria-label={`Ver imagen ${index + 1} de ${productName}`}
                  aria-pressed={isSelected}
                  className={`overflow-hidden rounded-md border transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 ${
                    isSelected
                      ? 'border-indigo-600'
                      : 'border-slate-200 hover:border-slate-400'
                  }`}
                >
                  <img
                    src={image.url}
                    alt=""
                    className="h-16 w-16 object-cover"
                  />
                  {image.is_primary ? (
                    <span className="sr-only">Imagen principal</span>
                  ) : null}
                </button>
              </li>
            )
          })}
        </ul>
      ) : null}
    </div>
  )
}
