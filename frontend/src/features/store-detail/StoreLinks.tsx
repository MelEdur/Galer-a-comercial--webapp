import type { ReactElement } from 'react'
import type { StoreLink } from './types'

interface StoreLinksProps {
  links: StoreLink[]
}

export function StoreLinks({ links }: StoreLinksProps): ReactElement | null {
  if (links.length === 0) {
    return null
  }

  const sortedLinks = [...links].sort((a, b) => a.position - b.position)

  return (
    <section
      aria-labelledby="store-links-title"
      className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
    >
      <h2
        id="store-links-title"
        className="text-lg font-semibold text-slate-900"
      >
        Enlaces
      </h2>

      <ul className="mt-4 flex flex-col gap-2 text-sm">
        {sortedLinks.map((link) => (
          <li key={`${link.url}-${link.position}`}>
            <a
              href={link.url}
              target="_blank"
              rel="noreferrer"
              className="font-medium text-indigo-600 hover:text-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            >
              {link.label}
            </a>
          </li>
        ))}
      </ul>
    </section>
  )
}
