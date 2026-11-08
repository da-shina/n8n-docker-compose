# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Container Management
```bash
# First run: create .env and fill in the required secrets
cp .env_sample .env

# Start all services
podman-compose up -d

# Rebuild and start (after Dockerfile changes)
podman-compose up -d --build

# View logs (all or specific service)
podman-compose logs -f
podman-compose logs -f n8n-runners

# Stop services
podman-compose down
```

### Testing
```bash
# Run all tests from the repository root (the tests read files by relative path)
python -m pytest tests

# Run specific test file
python -m pytest tests/test_env_config.py

# Run a single test
python -m pytest tests/test_env_config.py::test_env_sample_has_runner_settings -v
```

## Architecture

This project runs n8n (workflow automation platform) with an external task runner for Code nodes and a separate Playwright browser for automation.

### Services
- **n8n**: Main n8n instance on port 5678. Runs the UI and workflow executions.
- **n8n-runners**: Official external task runner sidecar (`n8nio/runners`). Executes JavaScript and Python Code nodes in an isolated process.
- **n8n-task-runner**: Playwright browser with a virtual display. Runs Playwright MCP on port 8931 and x11vnc on port 5900.
- **redis**: Queue store. Not used until queue mode is enabled.

### Key Files
- `docker-compose.yml`: Service definitions and configuration
- `start.sh`: Browser entry point: starts Xvfb, Fluxbox, x11vnc and Playwright MCP
- `Dockerfile.taskrunner`: Builds the Playwright/VNC browser image. It installs `@playwright/mcp` and the matching Chromium into `PLAYWRIGHT_BROWSERS_PATH`.
- `redis.conf`: Redis configuration (password comes from `REDIS_PASSWORD`)
- `.env` / `.env_sample`: Environment variables and required secrets

### Networking
- Services communicate via the Docker network (not host networking)
- n8n reaches Playwright MCP at `http://n8n-task-runner:8931/mcp` (the `playwright` alias also works)
- MCP is published only on `127.0.0.1:8931` because it has no authentication
- VNC is published on port 5900 and always requires `VNC_PASSWORD`
- The task broker listens on port 5679 inside the Docker network only
- `host.docker.internal:host-gateway` maps to the host machine

### Volumes (Named Volumes)
All persistent data uses named volumes. Compose creates them on first start:
- `n8n-docker-compose_n8n_data`: n8n user data and workflows
- `n8n-docker-compose_playwright_data`: browser profile (cookies, logins)
- `n8n-docker-compose_redis_data`: Redis persistence (AOF)

## Configuration

Required secrets (the stack refuses to start if they are empty):
- `N8N_ENCRYPTION_KEY`: encryption key for stored credentials
- `N8N_RUNNERS_AUTH_TOKEN`: shared secret between n8n and n8n-runners
- `REDIS_PASSWORD`: Redis authentication password
- `VNC_PASSWORD`: VNC access password (VNC accepts at most 8 characters)

Versioning:
- `N8N_VERSION` is used for both the n8n and n8n-runners images. They must match.

Queue mode:
- Queue mode is not enabled. The Redis settings are kept for a future setup, which also requires PostgreSQL (n8n does not support queue mode with SQLite).
