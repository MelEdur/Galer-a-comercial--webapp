import type { ReactElement } from 'react'
import { Route, Routes } from 'react-router-dom'
import { LoginPage } from '../features/auth/LoginPage'
import { ProtectedRoute } from '../features/auth/ProtectedRoute'
import { MerchantsPage } from '../features/admin-merchants/MerchantsPage'
import { AdminPage } from '../pages/AdminPage'
import { HomePage } from '../pages/HomePage'
import { MerchantPage } from '../pages/MerchantPage'
import { NotFoundPage } from '../pages/NotFoundPage'

export function AppRoutes(): ReactElement {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/admin"
        element={
          <ProtectedRoute>
            <AdminPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/comerciantes"
        element={
          <ProtectedRoute>
            <MerchantsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/comerciante"
        element={
          <ProtectedRoute role="merchant">
            <MerchantPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
