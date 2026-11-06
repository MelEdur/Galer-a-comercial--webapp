import { BrowserRouter } from 'react-router-dom'
import { AppProviders } from './app/providers'
import { AppRoutes } from './app/router'
import { AssistantWidget } from './features/assistant/AssistantWidget'

export default function App() {
  return (
    <AppProviders>
      <BrowserRouter>
        <AppRoutes />
        <AssistantWidget />
      </BrowserRouter>
    </AppProviders>
  )
}
