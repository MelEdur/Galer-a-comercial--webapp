import type { ReactElement } from 'react'
import { Route, Routes } from 'react-router-dom'
import { LoginPage } from '../features/auth/LoginPage'
import { ProtectedRoute } from '../features/auth/ProtectedRoute'
import { MerchantsPage } from '../features/admin-merchants/MerchantsPage'
import { AdminPage } from '../pages/AdminPage'
import { HomePage } from '../pages/HomePage'
import { MerchantPage } from '../pages/MerchantPage'
import { NotFoundPage } from '../pages/NotFoundPage'
import { ProductFormPage } from '../features/merchant-catalog/ProductFormPage'
import { ProductListPage } from '../features/merchant-catalog/ProductListPage'
import { ProductDetailPage } from '../features/product-detail/ProductDetailPage'
import { ProductStatsPage } from '../features/product-stats/ProductStatsPage'
import { SearchPage } from '../features/product-search/SearchPage'
import { StoreSettingsPage } from '../features/merchant-store/StoreSettingsPage'
import { StoreDetailPage } from '../features/store-detail/StoreDetailPage'
import { ExplorePage } from '../features/explore/ExplorePage'
import { StoreListPage } from '../features/explore/StoreListPage'

export function AppRoutes(): ReactElement {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/explorar" element={<ExplorePage />} />
      <Route path="/buscar" element={<SearchPage />} />
      <Route path="/productos/:productId" element={<ProductDetailPage />} />
      <Route path="/locales" element={<StoreListPage />} />
      <Route path="/locales/:storeId" element={<StoreDetailPage />} />
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
      <Route
        path="/comerciante/local"
        element={
          <ProtectedRoute role="merchant">
            <StoreSettingsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/comerciante/productos"
        element={
          <ProtectedRoute role="merchant">
            <ProductListPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/comerciante/estadisticas"
        element={
          <ProtectedRoute role="merchant">
            <ProductStatsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/comerciante/productos/nuevo"
        element={
          <ProtectedRoute role="merchant">
            <ProductFormPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/comerciante/productos/:productId/editar"
        element={
          <ProtectedRoute role="merchant">
            <ProductFormPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
