# Удобные цели для локального запуска на хосте (macOS / Linux).
# Windows: scripts\powershell\Setup-Host.ps1 и Start-Host.ps1

.PHONY: setup-host install-system-deps start-host start-host-fg stop-host check-host \
        start-backend start-frontend start-languagetool \
        docker-up docker-up-core docker-down docker-ps docker-logs docker-config

docker-up:
	docker compose up --build -d

docker-up-core:
	docker compose -f docker-compose.core.yml up --build -d

docker-down:
	docker compose down

docker-ps:
	docker compose ps

docker-logs:
	docker compose logs -f

docker-config:
	docker compose config

setup-host:
	./scripts/host/setup-host.sh

install-system-deps:
	./scripts/host/install-system-deps.sh

start-host:
	./scripts/host/start-host.sh

start-host-fg:
	./scripts/host/start-host.sh --foreground

stop-host:
	./scripts/host/stop-host.sh

check-host:
	./scripts/host/check-host.sh

start-backend:
	./scripts/host/start-backend.sh

start-frontend:
	./scripts/host/start-frontend.sh

start-languagetool:
	./scripts/host/start-languagetool.sh
