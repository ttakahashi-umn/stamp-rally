# stamp-rally

`cc-sdd` で初期化したうえで、以下の構成を追加しています。

- `frontend`: React + TypeScript (Vite)
- `backend`: Python 3.14 + FastAPI + SQLite

## セットアップ

### Docker Compose で起動/停止

```bash
make up
make down
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`

ログ確認:

```bash
make logs
```

会場QRコード生成:

```bash
make qrcodes
```

- 出力先: `data/qrcodes/FAC-XXXX.png`
- 署名鍵: 環境変数 `STAMP_QR_SECRET`（未指定時は開発用デフォルト）
- 期限: デフォルトで生成時から30日（`backend/scripts/generate_qrcodes.py` の引数で変更可能）

### 1) フロントエンド

```bash
cd frontend
npm install
npm run dev
```

### 2) バックエンド

```bash
cd backend
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

## API

- `GET /health`
- `POST /api/auth/activate`
- `GET /api/auth/session`
- `POST /api/stamps/scan`
- `GET /api/stamps/progress`

## MVPの動作確認

1. `make up` で起動
2. ブラウザで `http://localhost:5173/?token=demo-auth-token` を開く
3. 事前登録済み会場のQRを読み取って押印

このリポジトリでは `data/facilities.csv` を初期データとして `venues` へ取り込みます。  
列は `施設名` / `住所` / `特産品` を必須とし、`緯度` / `経度` は任意です。
