import type { ReactElement } from 'react'
import { StoreSlot } from './StoreSlot'
import type { MapSide, MapStore } from './types'

const SIDE_LABELS: Record<MapSide, string> = {
  left: 'Izquierda',
  right: 'Derecha',
  back: 'Fondo',
}

const SIDE_REGION_LABELS: Record<MapSide, string> = {
  left: 'Lado izquierdo',
  right: 'Lado derecho',
  back: 'Local del fondo',
}

function byPosition(stores: MapStore[]): MapStore[] {
  return [...stores].sort((a, b) => a.position - b.position)
}

interface MapSideColumnProps {
  side: MapSide
  stores: MapStore[]
}

function MapSideColumn({ side, stores }: MapSideColumnProps): ReactElement {
  return (
    <section aria-label={SIDE_REGION_LABELS[side]} className="space-y-2">
      <h2 className="text-xs font-semibold tracking-wide text-slate-500 uppercase">
        {SIDE_LABELS[side]}
      </h2>
      <div className="space-y-2">
        {stores.map((store) => (
          <StoreSlot key={store.id} store={store} />
        ))}
      </div>
    </section>
  )
}

interface MapLayoutProps {
  stores: MapStore[]
}

export function MapLayout({ stores }: MapLayoutProps): ReactElement {
  const backStores = byPosition(stores.filter((store) => store.side === 'back'))
  const leftStores = byPosition(stores.filter((store) => store.side === 'left'))
  const rightStores = byPosition(stores.filter((store) => store.side === 'right'))

  return (
    <div className="overflow-x-auto">
      <div className="mx-auto min-w-[30rem] max-w-3xl space-y-4">
        {backStores.length > 0 ? (
          <section
            aria-label="Local del fondo"
            className="rounded-lg border border-slate-200 bg-slate-50 p-4"
          >
            <h2 className="text-xs font-semibold tracking-wide text-slate-500 uppercase">
              Fondo
            </h2>
            <div className="mt-2 space-y-2">
              {backStores.map((store) => (
                <StoreSlot key={store.id} store={store} />
              ))}
            </div>
          </section>
        ) : null}

        <div className="grid grid-cols-[minmax(5.5rem,1fr)_2.5rem_minmax(5.5rem,1fr)] items-start gap-3 sm:grid-cols-[1fr_4rem_1fr]">
          <MapSideColumn side="left" stores={leftStores} />

          <div
            aria-hidden="true"
            className="flex min-h-full items-center justify-center rounded-md bg-slate-100"
          >
            <span className="text-[10px] font-semibold tracking-widest text-slate-400 uppercase [writing-mode:vertical-rl]">
              Pasillo
            </span>
          </div>

          <MapSideColumn side="right" stores={rightStores} />
        </div>
      </div>
    </div>
  )
}
