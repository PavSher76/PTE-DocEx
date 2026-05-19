# Удобные цели для локального запуска на хосте (macOS / Linux).
# Windows: scripts\powershell\Setup-Host.ps1 и Start-Host.ps1

.PHONY: setup-host install-system-deps start-host start-host-fg stop-host check-host \
        start-backend start-frontend start-languagetool

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
