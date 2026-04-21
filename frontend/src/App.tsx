import { useCallback, useState } from 'react'
import { fetchProgress } from './app/stamp-client'
import type { Progress } from './app/types'
import { AuthGate } from './features/auth/AuthGate'
import { StampList } from './features/stamp/StampList'
import { StampScanAction } from './features/stamp/StampScanAction'
import './App.css'

const EMPTY_PROGRESS: Progress = {
  total: 0,
  completed: 0,
  items: [],
}

function App() {
  const [sessionToken, setSessionToken] = useState<string | null>(null)
  const [progress, setProgress] = useState<Progress>(EMPTY_PROGRESS)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadProgress = useCallback(async () => {
    if (!sessionToken) {
      return
    }
    setLoading(true)
    setError(null)
    try {
      const nextProgress = await fetchProgress(sessionToken)
      setProgress(nextProgress)
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : '読み込みに失敗しました')
    } finally {
      setLoading(false)
    }
  }, [sessionToken])

  const handleAuthenticated = useCallback((token: string) => {
    setSessionToken(token)
    setLoading(true)
    setError(null)
    void (async () => {
      try {
        const nextProgress = await fetchProgress(token)
        setProgress(nextProgress)
      } catch (loadError) {
        setError(
          loadError instanceof Error ? loadError.message : '読み込みに失敗しました',
        )
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  const handleStamped = useCallback(async () => {
    await loadProgress()
  }, [loadProgress])

  return (
    <main className="container">
      <div className="app-branding">
        <img src="/branding/logo.png" alt="IMSグループ" className="app-logo" />
        <img
          src="/branding/logo_70_120.png"
          alt="IMSグループ70周年ロゴ"
          className="app-logo-anniversary"
        />
      </div>

      {!sessionToken ? (
        <AuthGate onAuthenticated={handleAuthenticated} />
      ) : (
        <>
          <StampScanAction sessionToken={sessionToken} onStamped={handleStamped} />
          <StampList progress={progress} loading={loading} error={error} />
        </>
      )}
    </main>
  )
}

export default App
