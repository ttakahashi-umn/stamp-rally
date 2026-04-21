import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { StampList } from './StampList'

describe('StampList', () => {
  it('進捗と押印済みスタンプを表示できる', () => {
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
              imageUrl: 'https://example.com/tokyo.jpg',
              description: '東京会場の紹介',
              completed: true,
            },
            {
              venueId: 'v2',
              code: 'IMS-OSAKA',
              name: '大阪城会場',
              location: '大阪府大阪市',
              imageUrl: 'https://example.com/osaka.jpg',
              description: '大阪会場の紹介',
              completed: false,
            },
          ],
        }}
        loading={false}
        error={null}
      />,
    )
    expect(screen.queryByText('会場スタンプ')).not.toBeInTheDocument()
    expect(screen.queryByText('押印済みスタンプ')).not.toBeInTheDocument()
    const stampGrid = document.querySelector('.stamp-grid')
    expect(stampGrid?.firstElementChild?.textContent).toContain('東京タワー会場')
    const stampedImage = screen.getByAltText('東京タワー会場のスタンプ')
    expect(stampedImage).toHaveAttribute('src', 'https://example.com/tokyo.jpg')
    fireEvent.click(screen.getByRole('button', { name: /東京タワー会場/ }))
    expect(screen.getByText('紹介')).toBeInTheDocument()
    expect(screen.getByText('住所')).toBeInTheDocument()
    expect(screen.getByText('説明')).toBeInTheDocument()
    expect(screen.getByText('特産品')).toBeInTheDocument()
    expect(screen.getByText('名前')).toBeInTheDocument()
    expect(screen.getByText('画像')).toBeInTheDocument()
    expect(screen.getByText('東京会場の紹介')).toBeInTheDocument()
  })
})
