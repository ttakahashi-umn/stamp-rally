import { useState } from 'react'
import { scanStamp } from '../../app/stamp-client'

type Props = {
  sessionToken: string
  onStamped: () => void
}

export function StampScanAction({ sessionToken, onStamped }: Props) {
  const [qrPayload, setQrPayload] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [resultMessage, setResultMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const requestCurrentPosition = async (): Promise<GeolocationPosition> =>
    new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('位置情報APIに対応していません'))
        return
      }
      navigator.geolocation.getCurrentPosition(resolve, reject)
    })

  const handleSubmit = async () => {
    if (!qrPayload.trim()) {
      setError('QRペイロードを入力してください')
      return
    }
    setSubmitting(true)
    setError(null)
    setResultMessage(null)
    try {
      const position = await requestCurrentPosition()
      const scanResult = await scanStamp(
        sessionToken,
        qrPayload.trim(),
        position.coords.latitude,
        position.coords.longitude,
      )
      setResultMessage(scanResult.message)
      await onStamped()
    } catch (scanError) {
      setError(scanError instanceof Error ? scanError.message : '押印に失敗しました')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="scan-panel">
      <h2>スタンプ押印</h2>
      <p>会場QRの内容を入力して押印します（MVP）。</p>
      <input
        type="text"
        value={qrPayload}
        onChange={(event) => setQrPayload(event.target.value)}
        placeholder="例: IMS-TOKYO:1735689600:<signature>"
      />
      <button type="button" onClick={() => void handleSubmit()} disabled={submitting}>
        {submitting ? '押印中...' : '押印する'}
      </button>
      {resultMessage ? <p className="success">{resultMessage}</p> : null}
      {error ? <p className="error">{error}</p> : null}
    </section>
  )
}
