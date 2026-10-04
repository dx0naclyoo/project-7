prod:
	uv run fastapi run

dev:
	uv run fastapi dev

docker-run:
	docker compose up

build:
	docker compose build