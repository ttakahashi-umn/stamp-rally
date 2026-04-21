import type { Session } from './types'

type ActivateResponse = {
  session_token: string
  participant_id: string
}

type SessionResponse = {
  participant_id: string
  active: boolean
}

export const SESSION_STORAGE_KEY = 'stamp-rally-session-token'

export async function activateAuthToken(token: string): Promise<string> {
  const response = await fetch('/api/auth/activate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token }),
  })
  if (!response.ok) {
    throw new Error('認証トークンが無効または期限切れです')
  }
  const data = (await response.json()) as ActivateResponse
  return data.session_token
}

export async function fetchSession(sessionToken: string): Promise<Session> {
  const response = await fetch('/api/auth/session', {
    headers: { Authorization: sessionToken },
  })
  if (!response.ok) {
    throw new Error('セッションが無効です。再認証してください。')
  }
  const data = (await response.json()) as SessionResponse
  return {
    participantId: data.participant_id,
    active: data.active,
  }
}
