# Backend (Python 3.14 + SQLite)

## セットアップ

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 起動

```bash
uvicorn app.main:app --reload --port 8000
```

## テスト

```bash
pytest
```
