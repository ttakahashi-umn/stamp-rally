import type { Progress, ScanResult } from './types'

type ProgressApi = {
  total: number
  completed: number
  items: Array<{
    venue_id: string
    code: string
    name: string
    location: string
    completed: boolean
  }>
}

type ScanApi = {
  status: 'stamped' | 'already_stamped'
  stamp_id: string | null
  message: string
}

export async function fetchProgress(sessionToken: string): Promise<Progress> {
  const response = await fetch('/api/stamps/progress', {
    headers: { Authorization: sessionToken },
  })
  if (!response.ok) {
    throw new Error('進捗情報の取得に失敗しました')
  }
  const data = (await response.json()) as ProgressApi
  return {
    total: data.total,
    completed: data.completed,
    items: data.items.map((item) => ({
      venueId: item.venue_id,
      code: item.code,
      name: item.name,
      location: item.location,
      completed: item.completed,
    })),
  }
}

export async function scanStamp(
  sessionToken: string,
  qrPayload: string,
  latitude: number,
  longitude: number,
): Promise<ScanResult> {
  const response = await fetch('/api/stamps/scan', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: sessionToken,
    },
    body: JSON.stringify({
      qr_payload: qrPayload,
      latitude,
      longitude,
    }),
  })
  if (!response.ok) {
    const errorBody = (await response.json()) as { detail?: string }
    throw new Error(errorBody.detail ?? '押印に失敗しました')
  }
  const data = (await response.json()) as ScanApi
  return {
    status: data.status,
    stampId: data.stamp_id,
    message: data.message,
  }
}
