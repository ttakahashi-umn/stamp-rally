# Research & Design Decisions

## Summary
- **Feature**: `stamp-rally-mvp`
- **Discovery Scope**: Extension
- **Key Findings**:
  - 既存実装は「グローバルなスタンプ状態」を扱う最小サンプルであり、参加者別の認証・押印履歴モデルが未実装。
  - 要件の中心は「起動の速さ」「認証の簡便さ」「押印の簡便さ」であり、運営向けの高度機能はMVP外にする必要がある。
  - 不正抑止は位置情報判定のみでは不十分なため、短TTLの署名付きQR検証を合わせる前提が必要。

## Research Log

### 既存コードとの整合
- **Context**: 既存アプリを拡張してMVPを成立させる必要がある。
- **Sources Consulted**:
  - `frontend/src/App.tsx`
  - `backend/app/main.py`
  - `backend/app/db.py`
- **Findings**:
  - フロントは `/api/stamps` の一覧取得とトグル更新のみを提供している。
  - バックエンドは `stamps` テーブルのみで、利用者単位の状態を保持していない。
  - 認証、端末記憶、会場マスタ、押印履歴、位置情報判定APIが欠落している。
- **Implications**:
  - 既存の `stamps.completed` を参加者別状態へ移行する設計が必要。
  - APIとDBの境界を明確化しないと、後続タスクが衝突しやすい。

### 不正抑止要件の成立性
- **Context**: 会場QR + 位置情報チェックのMVP実現性を確認。
- **Sources Consulted**:
  - 先行ディスカバリーでの技術妥当性チェック結果
  - `docker-compose.yml`, `Makefile`
- **Findings**:
  - 位置情報判定単体では位置偽装や拒否ケースに弱い。
  - 静的QRのみでは横流し・再利用リスクが高い。
  - 短TTL署名トークン検証を合わせるとMVPでも最低限の抑止効果が得られる。
- **Implications**:
  - 押印APIは「認証」「署名検証」「位置判定」「重複判定」を同一トランザクション境界で扱う必要がある。

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| 既存API拡張（単一FastAPI） | 既存 `main.py` を責務分割しつつ拡張 | 既存構成を活かし実装速度が高い | 責務未分離のままだと保守性低下 | MVPに最適 |
| サービス分割（認証/押印分離） | 複数サービスへ分割 | 将来拡張に強い | MVPには過剰、運用コスト増 | 今回は不採用 |
| 外部ID基盤連携 | 企業SSOへ統合 | 本人性が強い | 導入調整コストが高い | MVP外 |

## Design Decisions

### Decision: 認証方式はメール起点トークン + 端末記憶
- **Context**: 参加導線を最短化しつつ、再訪時の手間を減らす必要がある。
- **Alternatives Considered**:
  1. 社員番号/パスワード入力
  2. メール配布リンク/QR起点のトークン認証
- **Selected Approach**: メールトークンで初回認証し、端末側にセッション識別子を保持して再訪を簡易化する。
- **Rationale**: ユーザーの入力負荷を最小化し、要求の「簡単に認証」を満たす。
- **Trade-offs**: 端末紛失・共有端末時の再認証導線が必須。
- **Follow-up**: セッション失効条件と再認証UXをテスト計画に含める。

### Decision: 押印判定は署名QR検証 + ジオフェンスの二段構え
- **Context**: 不正押印抑止をMVP範囲で成立させる必要がある。
- **Alternatives Considered**:
  1. 位置情報判定のみ
  2. QR検証のみ
  3. QR検証 + 位置情報判定
- **Selected Approach**: 署名付き短TTL QRの検証後に会場ジオフェンスを判定し、両方成立時のみ押印する。
- **Rationale**: 横流しリスクと遠隔押印リスクを同時に下げられる。
- **Trade-offs**: 位置情報拒否時は押印不可となり、UX低下が起こり得る。
- **Follow-up**: 失敗理由を明確表示し、再試行導線を設計へ反映する。

### Decision: データ責務を会場/参加者/押印履歴に分離
- **Context**: グローバルフラグ型の既存構造では要件を満たせない。
- **Alternatives Considered**:
  1. `stamps` テーブルを拡張して使い続ける
  2. 参加者・会場・押印履歴を分離する
- **Selected Approach**: 会場マスタ、参加者、端末セッション、押印履歴の4責務へ分離。
- **Rationale**: 参加者別の進捗表示と重複防止、監査可能性を担保できる。
- **Trade-offs**: 初期実装のテーブル追加が必要。
- **Follow-up**: SQLite同時書き込みの負荷試験を行う。

## Synthesis Outcomes
- **Generalization**: 押印判定を単一ユースケースではなく「検証パイプライン（認証→QR→位置→重複）」として定義し、将来の別イベントでも再利用可能な契約に一般化した。
- **Build vs Adopt**: QR読み取りUIはブラウザ標準API（`BarcodeDetector` 非対応時は入力代替）を優先し、MVPでは重い外部SDK導入を回避する。
- **Simplification**: 管理者機能、景品連携、高度不正検知を除外し、参加者向けフローと運営の事前データ投入前提に限定した。

## Risks & Mitigations
- 位置情報拒否で押印できない参加者が出る — 失敗理由と再試行導線を明示し、運営の救済オペレーションを別途準備。
- SQLite同時書き込み競合 — WAL設定とイベントピーク想定の負荷試験を必須化。
- 端末記憶トークンの漏えい — 有効期限短縮、失効API、サーバ側照合でリスク低減。

## References
- `frontend/src/App.tsx` — 既存UI構成とAPI呼び出し方式
- `backend/app/main.py` — 既存APIとレスポンスモデル
- `backend/app/db.py` — 既存SQLiteスキーマ
- `README.md` — 既存セットアップとAPI公開範囲
