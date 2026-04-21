import { BrowserQRCodeReader } from '@zxing/browser'
import { useEffect, useRef, useState } from 'react'
import { scanStamp } from '../../app/stamp-client'

type Props = {
  sessionToken: string
  onStamped: () => void
}

export function StampScanAction({ sessionToken, onStamped }: Props) {
  const [submitting, setSubmitting] = useState(false)
  const [cameraActive, setCameraActive] = useState(false)
  const [resultMessage, setResultMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [cameraError, setCameraError] = useState<string | null>(null)
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const scannerRef = useRef<BrowserQRCodeReader | null>(null)
  const controlRef = useRef<{ stop: () => void } | null>(null)
  const scanInFlightRef = useRef(false)
  const timeoutRef = useRef<number | null>(null)

  const stopCamera = () => {
    controlRef.current?.stop()
    controlRef.current = null
    scannerRef.current = null
    if (timeoutRef.current !== null) {
      window.clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }
    setCameraActive(false)
  }

  useEffect(() => () => stopCamera(), [])

  const requestCurrentPosition = async (): Promise<GeolocationPosition> =>
    new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('位置情報APIに対応していません'))
        return
      }
      navigator.geolocation.getCurrentPosition(resolve, reject)
    })

  const submitWithPayload = async (payload: string) => {
    setSubmitting(true)
    setError(null)
    try {
      const position = await requestCurrentPosition()
      const scanResult = await scanStamp(
        sessionToken,
        payload.trim(),
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

  const startCamera = async () => {
    if (!videoRef.current) {
      return
    }
    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraError('このブラウザはカメラアクセスに対応していません')
      return
    }
    setCameraError(null)
    setError(null)
    const reader = new BrowserQRCodeReader()
    scannerRef.current = reader
    try {
      const controls = await reader.decodeFromVideoDevice(
        undefined,
        videoRef.current,
        (result) => {
          if (!result || scanInFlightRef.current) {
            return
          }
          scanInFlightRef.current = true
          const payload = result.getText()
          setResultMessage('QRを読み取りました。押印を実行します...')
          void submitWithPayload(payload).finally(() => {
            scanInFlightRef.current = false
          })
        },
      )
      controlRef.current = controls
      setCameraActive(true)
      timeoutRef.current = window.setTimeout(() => {
        stopCamera()
        setResultMessage('カメラを停止しました（60秒タイムアウト）')
      }, 60_000)
    } catch {
      setCameraError(
        'カメラを起動できませんでした。権限を許可して再試行してください。',
      )
      stopCamera()
    }
  }

  return (
    <section className="scan-panel">
      <p className="scan-description">会場QRをカメラで読み取って押印します。</p>
      <div className="camera-actions">
        <button
          type="button"
          onClick={() => void startCamera()}
          disabled={submitting}
        >
          {cameraActive ? 'カメラ起動中...' : 'カメラ起動'}
        </button>
      </div>
      <video
        ref={videoRef}
        className={cameraActive ? 'camera-preview active' : 'camera-preview'}
        muted
        playsInline
      />
      {cameraError ? <p className="error">{cameraError}</p> : null}
      {resultMessage ? <p className="success">{resultMessage}</p> : null}
      {error ? <p className="error">{error}</p> : null}
    </section>
  )
}
