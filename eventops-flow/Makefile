    .PHONY: up down logs init seed urls clean

    up:
		docker compose up -d --build

    down:
		docker compose down -v

    logs:
		docker compose logs -f --tail=200

    init:
		./scripts/init_topics.sh

    seed:
		./scripts/seed_example.sh

    urls:
		@echo API: http://localhost:8088/metrics/cpu?tenant=acme\&host=host-a
		@echo UI:  http://localhost:8080

    clean:
		rm -rf data
