import type { Progress } from '../../app/types'

type Props = {
  progress: Progress
  loading: boolean
  error: string | null
  onReload: () => void
}

export function StampList({ progress, loading, error, onReload }: Props) {
  return (
    <section>
      <div className="section-head">
        <h2>進捗</h2>
        <button type="button" onClick={onReload}>
          再読み込み
        </button>
      </div>
      {loading ? <p>進捗を読み込み中...</p> : null}
      {error ? <p className="error">{error}</p> : null}
      <p className="progress">
        達成状況: {progress.completed} / {progress.total}
      </p>
      <ul className="stamp-list">
        {progress.items.map((item) => (
          <li key={item.venueId}>
            <div className={item.completed ? 'done card' : 'card'}>
              <span>{item.name}</span>
              <small>{item.location}</small>
              <small>{item.code}</small>
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}
