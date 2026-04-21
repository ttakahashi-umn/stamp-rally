import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { StampList } from './StampList'

describe('StampList', () => {
  it('進捗と一覧を表示し、再読み込みを呼べる', () => {
    const onReload = vi.fn()
    render(
      <StampList
        progress={{
          total: 2,
          completed: 1,
          items: [
            {
              venueId: 'v1',
              code: 'IMS-TOKYO',
              name: '東京タワー会場',
              location: '東京都港区',
              completed: true,
            },
            {
              venueId: 'v2',
              code: 'IMS-OSAKA',
              name: '大阪城会場',
              location: '大阪府大阪市',
              completed: false,
            },
          ],
        }}
        loading={false}
        error={null}
        onReload={onReload}
      />,
    )
    expect(screen.getByText('達成状況: 1 / 2')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: '再読み込み' }))
    expect(onReload).toHaveBeenCalledTimes(1)
  })
})
