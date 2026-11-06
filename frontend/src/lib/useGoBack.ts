import { useLocation, useNavigate } from 'react-router-dom'

export function useGoBack(): () => void {
  const navigate = useNavigate()
  const location = useLocation()

  return () => {
    if (location.key !== 'default') {
      navigate(-1)
      return
    }

    navigate('/')
  }
}
