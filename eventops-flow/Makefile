.PHONY: up down logs build fmt lint

up:
	docker compose up -d

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

build:
	docker compose build --pull

fmt:
	black normalizer enricher feature-rules api || true

lint:
	flake8 normalizer enricher feature-rules api || true
