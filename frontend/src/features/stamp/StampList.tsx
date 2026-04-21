import type { Progress } from '../../app/types'
import { useMemo, useState } from 'react'

const DUMMY_FACILITY_DESCRIPTION =
  'この施設は地域の交流拠点として多くの来場者に親しまれています。イベント期間中は記念展示や体験企画を実施しています。'

type Props = {
  progress: Progress
  loading: boolean
  error: string | null
}

export function StampList({ progress, loading, error }: Props) {
  const sortedItems = useMemo(
    () =>
      [...progress.items].sort((a, b) => {
        if (a.completed === b.completed) {
          return 0
        }
        return a.completed ? -1 : 1
      }),
    [progress.items],
  )
  const collectedItems = useMemo(
    () => progress.items.filter((item) => item.completed),
    [progress.items],
  )
  const [selectedCollectedVenueId, setSelectedCollectedVenueId] = useState<string | null>(
    null,
  )

  const selectedCollected = collectedItems.find(
    (item) => item.venueId === selectedCollectedVenueId,
  )

  return (
    <section>
      {loading ? <p>会場情報を読み込み中...</p> : null}
      {error ? <p className="error">{error}</p> : null}
      <ul className="stamp-grid">
        {sortedItems.map((item) => (
          <li key={item.venueId}>
            {item.completed ? (
              <button
                type="button"
                className="stamp-chip-button"
                onClick={() => setSelectedCollectedVenueId(item.venueId)}
              >
                <div className="stamp-chip done">
                  <img
                    src={item.imageUrl}
                    alt={`${item.name}のスタンプ`}
                    className="stamp-image"
                    loading="lazy"
                  />
                  <span className="stamp-name">{item.name}</span>
                  <small>押印済み</small>
                </div>
              </button>
            ) : (
              <div className="stamp-chip">
                <div className="stamp-image-placeholder" aria-hidden="true" />
                <span className="stamp-name">{item.name}</span>
                <small>未押印</small>
              </div>
            )}
          </li>
        ))}
      </ul>

      {collectedItems.length === 0 ? (
        <p>まだ押印済みスタンプがありません。</p>
      ) : null}
      {selectedCollected ? (
        <>
          <button
            type="button"
            className="sheet-backdrop"
            aria-label="詳細を閉じる"
            onClick={() => setSelectedCollectedVenueId(null)}
          />
          <article className="venue-sheet">
            <button
              type="button"
              className="sheet-close"
              aria-label="閉じる"
              onClick={() => setSelectedCollectedVenueId(null)}
            >
              ×
            </button>
            <h4>{selectedCollected.name}</h4>
            <img
              src={`https://picsum.photos/seed/${selectedCollected.venueId}-facility/960/540`}
              alt={`${selectedCollected.name}の施設写真`}
              className="venue-photo"
              loading="lazy"
            />
            <p className="sheet-label">紹介</p>
            <p className="sheet-sub-label">住所</p>
            <p className="detail-location">{selectedCollected.location}</p>
            <p className="sheet-sub-label">説明</p>
            <p>{DUMMY_FACILITY_DESCRIPTION}</p>
            <p className="sheet-label">特産品</p>
            <p className="sheet-sub-label">名前</p>
            <p>{selectedCollected.description || '特産品情報は未設定です。'}</p>
            <p className="sheet-sub-label">画像</p>
            <img
              src={selectedCollected.imageUrl}
              alt={`${selectedCollected.description || selectedCollected.name}の画像`}
              className="specialty-photo"
              loading="lazy"
            />
          </article>
        </>
      ) : null}
    </section>
  )
}
