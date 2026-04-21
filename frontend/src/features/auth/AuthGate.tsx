import { useEffect, useState } from 'react'
import {
  activateAuthToken,
  fetchSession,
  SESSION_STORAGE_KEY,
} from '../../app/auth-client'

type Props = {
  onAuthenticated: (sessionToken: string) => void
}

export function AuthGate({ onAuthenticated }: Props) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const resolveAuth = async () => {
      const params = new URLSearchParams(window.location.search)
      const tokenInUrl = params.get('token')
      const storedSession = window.localStorage.getItem(SESSION_STORAGE_KEY)
      try {
        if (tokenInUrl) {
          const sessionToken = await activateAuthToken(tokenInUrl)
          window.localStorage.setItem(SESSION_STORAGE_KEY, sessionToken)
          onAuthenticated(sessionToken)
          return
        }
        if (storedSession) {
          await fetchSession(storedSession)
          onAuthenticated(storedSession)
          return
        }
        setError('案内メールのQRコードを読み込んでアクセスしてください。')
      } catch (authError) {
        window.localStorage.removeItem(SESSION_STORAGE_KEY)
        setError(authError instanceof Error ? authError.message : '認証に失敗しました')
      } finally {
        setLoading(false)
      }
    }
    void resolveAuth()
  }, [onAuthenticated])

  if (loading) {
    return <p>認証状態を確認中...</p>
  }
  if (error) {
    return <p className="error">{error}</p>
  }
  return <p>認証処理を完了しています...</p>
}
