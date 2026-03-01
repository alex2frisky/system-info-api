.PHONY: up down logs test lint build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

test:
	pytest tests/ -v

lint:
	flake8 app.py --max-line-length=100

build:
	docker build -t system-info-api .
