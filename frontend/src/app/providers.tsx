import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { AuthProvider } from '../features/auth/AuthContext'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      staleTime: 30_000,
      refetchOnWindowFocus: false,
    },
  },
})

interface AppProvidersProps {
  children: ReactNode
  client?: QueryClient
}

export function AppProviders({ children, client = queryClient }: AppProvidersProps) {
  return (
    <QueryClientProvider client={client}>
      <AuthProvider>{children}</AuthProvider>
    </QueryClientProvider>
  )
}
