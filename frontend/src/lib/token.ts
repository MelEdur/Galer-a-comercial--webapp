const TOKEN_STORAGE_KEY = 'galeria.auth.token'

export function getStoredToken(): string | null {
  try {
    return sessionStorage.getItem(TOKEN_STORAGE_KEY)
  } catch {
    return null
  }
}

export function setStoredToken(token: string): void {
  try {
    sessionStorage.setItem(TOKEN_STORAGE_KEY, token)
  } catch {
    // Si el almacenamiento no está disponible la sesión será solo en memoria.
  }
}

export function clearStoredToken(): void {
  try {
    sessionStorage.removeItem(TOKEN_STORAGE_KEY)
  } catch {
    // Sin almacenamiento no hay nada que limpiar.
  }
}
