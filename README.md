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
3. QRペイロードを入力して押印

QRペイロードは以下コマンドで生成できます。

```bash
cd backend
source .venv/bin/activate
python -c "from datetime import datetime,UTC,timedelta;from app.db import get_connection;from app.repositories.venue_repo import VenueRepository;from app.repositories.stamp_record_repo import StampRecordRepository;from app.stamp_service import StampService;svc=StampService(VenueRepository(get_connection()),StampRecordRepository(get_connection()));print(svc.create_payload('IMS-TOKYO',int((datetime.now(UTC)+timedelta(minutes=10)).timestamp())))"
```
