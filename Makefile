.PHONY: up down build logs ps restart qrcodes

up:
	docker compose up -d --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f --tail=100

ps:
	docker compose ps

restart:
	docker compose down
	docker compose up -d --build

qrcodes:
	python "backend/scripts/generate_qrcodes.py"
