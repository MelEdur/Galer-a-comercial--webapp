import type { ReactElement } from 'react'
import { Outlet } from 'react-router-dom'
import { SiteHeader } from './SiteHeader'

export function AppLayout(): ReactElement {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      <SiteHeader />
      <div className="flex-1">
        <Outlet />
      </div>
    </div>
  )
}
