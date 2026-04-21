export type Session = {
  participantId: string
  active: boolean
}

export type ProgressItem = {
  venueId: string
  code: string
  name: string
  location: string
  completed: boolean
}

export type Progress = {
  total: number
  completed: number
  items: ProgressItem[]
}

export type ScanResult = {
  status: 'stamped' | 'already_stamped'
  stampId: string | null
  message: string
}
