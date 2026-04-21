# Requirements Document

## Introduction
本仕様は、IMSグループ職員向け70周年イベントの回遊体験を向上させるスタンプラリーMVPの要求を定義する。  
対象機能は、メール起点の参加導線、簡易認証、会場QR押印、会場一覧/詳細表示、ならびに位置情報を利用した不正抑止である。

## Boundary Context (Optional)
- **In scope**: メール配布リンク/QRでの初回参加、端末記憶による再訪、会場QR押印、位置情報判定、押印可否の明確なフィードバック、参加状況表示。
- **Out of scope**: 企業SSO連携、ネイティブアプリ、景品抽選機能、高度な不正検知、イベント企画全体の改善支援。
- **Adjacent expectations**: 運営側がイベント期間と会場情報（会場名、QR、緯度経度）を事前に整備し、参加者へ案内メールを配信済みであることを前提とする。

## Project Description (Input)
- 誰の課題か: IMSグループの職員（約25,000人）にとって、70周年記念イベントの催しが十分に魅力的でなく、参加体験が弱い。  
- 現状: スタンプラリーを実施するためのデジタル導線（メール配布リンク/QRからの即時参加、簡易認証、会場QR押印、進捗表示）が未整備である。  
- 変えたい状態: メール経由で素早く起動・認証でき、会場QRで簡単にスタンプを押せる体験を提供する。加えて、端末記憶と会場緯度経度に基づく不正抑止を備え、イベント満足度向上につながるMVPを実現する。

## Requirements

### Requirement 1: 参加導線と初回認証
**Objective:** As a イベント参加者, I want 案内メールからすぐ参加開始できること, so that 手間なくスタンプラリーを始められる

#### Acceptance Criteria
1. When 参加者が案内メール内リンクを開いたとき, the Stamp Rally Service shall 初回認証画面または認証済み画面へ遷移させる.
2. If 参加者が無効または期限切れの認証情報でアクセスしたとき, then the Stamp Rally Service shall 再認証が必要であることを表示し押印機能を利用不可にする.
3. The Stamp Rally Service shall 認証完了後に参加者がスタンプ一覧画面へ到達できるようにする.

### Requirement 2: 端末記憶による再訪体験
**Objective:** As a イベント参加者, I want 同じ端末で再訪時に再入力を減らしたい, so that 簡単に継続参加できる

#### Acceptance Criteria
1. When 認証済み参加者が同一端末で再訪したとき, the Stamp Rally Service shall 認証済み状態としてスタンプ一覧へ遷移させる.
2. If 端末記憶情報が無効化または失効しているとき, then the Stamp Rally Service shall 再認証フローへ誘導する.
3. While 参加者が未認証状態である間, the Stamp Rally Service shall 押印機能を実行させない.

### Requirement 3: 会場QRによるスタンプ押印（カメラ専用）
**Objective:** As a イベント参加者, I want 会場でQRを読み取ってすぐ押印したい, so that 回遊体験を中断せずに進められる

#### Acceptance Criteria
1. When 認証済み参加者が有効な会場QRを読み取ったとき, the Stamp Rally Service shall 対象会場のスタンプを付与し成功メッセージを表示する.
2. If 同一参加者が同一会場のQRを再読み取りしたとき, then the Stamp Rally Service shall 二重押印せず既に取得済みであることを表示する.
3. The Stamp Rally Service shall カメラ起動でのみプレビューを表示し、起動後60秒で自動停止する.
4. The Stamp Rally Service shall 手入力を提供せず、カメラ読み取りのみで押印を実行する.

### Requirement 4: 位置情報による現地判定
**Objective:** As a イベント運営者, I want 現地参加を前提に押印させたい, so that 不正押印を抑止できる

#### Acceptance Criteria
1. When 参加者が押印を実行するとき, the Stamp Rally Service shall 当該会場の許可範囲内かを判定する.
2. If 参加者の位置情報取得が拒否または失敗したとき, then the Stamp Rally Service shall 位置情報が必要であることを表示し押印を完了させない.
3. If 参加者の位置が会場の許可範囲外であるとき, then the Stamp Rally Service shall 押印を拒否し会場付近で再試行する案内を表示する.

### Requirement 5: 不正・異常系の押印拒否
**Objective:** As a イベント運営者, I want 不正または無効な押印を拒否したい, so that イベント結果の信頼性を保てる

#### Acceptance Criteria
1. If 期限切れまたは無効な会場QRが利用されたとき, then the Stamp Rally Service shall 押印を拒否し再読込または最新QR利用を案内する.
2. When 押印処理中に通信エラーが発生したとき, the Stamp Rally Service shall 成功未確定であることを表示し参加者が再試行できる状態にする.
3. The Stamp Rally Service shall 押印成功と押印失敗を参加者に識別可能なメッセージで表示する.

### Requirement 6: 会場一覧と押印済み詳細表示
**Objective:** As a イベント参加者, I want 会場一覧と押印済み会場の詳細を分かりやすく見たい, so that 次に回る会場と取得済み情報を直感的に把握できる

#### Acceptance Criteria
1. When 参加者がスタンプ一覧画面を表示したとき, the Stamp Rally Service shall 会場を3列グリッドで表示し、押印済み会場を先頭に並べる.
2. The Stamp Rally Service shall 進捗件数ラベル（X/Y）や手動再読み込みボタンを表示しない.
3. When 参加者が押印済み会場をタップしたとき, the Stamp Rally Service shall 画面下から詳細シートを表示し、以下の順で情報を表示する: 施設名 / 施設写真（ダミー） / 紹介（住所・説明） / 特産品（名前・画像）.
4. The Stamp Rally Service shall 押印済み会場のグリッドカードに `frontend/public/stamps` のスタンプ画像を表示する.
5. If 一覧データの取得に失敗したとき, then the Stamp Rally Service shall 失敗理由を表示する.

### Requirement 7: 会場データ・画像リソース運用
**Objective:** As a イベント運営者, I want CSVと静的アセットを基準に会場情報を更新したい, so that 開催前後の差し替え作業を簡単にしたい

#### Acceptance Criteria
1. The Stamp Rally Service shall `data/facilities.csv`（施設名・住所・特産品、緯度経度任意）を起点に会場マスタを登録/更新する.
2. The Stamp Rally Service shall 会場ごとのスタンプ画像を `frontend/public/stamps/FAC-XXXX.png` として参照できる.
3. The Stamp Rally Service shall `make qrcodes` で会場QR画像を一括生成し、`data/qrcodes/FAC-XXXX.png` に出力できる.
4. The Stamp Rally Service shall デモ参加者に対して `FAC-0001`〜`FAC-0004` と `FAC-0073`〜`FAC-0074` を初期押印済みとして扱える.

### Requirement 8: 画面ブランディング
**Objective:** As a イベント参加者, I want イベントロゴを冒頭で認識したい, so that 公式イベント画面であることを安心して判断できる

#### Acceptance Criteria
1. The Stamp Rally Service shall タイトル文字列の代わりにロゴ画像をヘッダーに表示する.
2. The Stamp Rally Service shall 70周年ロゴをメインロゴの右側に横並び表示する.
