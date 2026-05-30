# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Container Management
```bash
# Start all services
podman compose up -d

# Rebuild and start (after Dockerfile changes)
podman compose up -d --build

# View logs (all or specific service)
podman compose logs -f
podman compose logs -f n8n-task-runner

# Stop services
podman compose down
```

### Testing
```bash
# Run all tests
cd tests && python -m pytest

# Run specific test file
cd tests && python -m pytest test_env_config.py

# Run a single test
cd tests && python -m pytest test_env_config.py::test_env_sample_has_runner_settings -v
```

## Architecture

This project runs n8n (workflow automation platform) with external task runners and Playwright browser automation.

### Services
- **n8n**: Main n8n instance on port 5678
- **n8n-task-runner**: External task runner with Playwright MCP server on port 8931
- **redis**: Message queue on port 6379 (AOF persistence enabled)
- **vnc**: VNC server on port 5900 (for Playwright browser GUI)

### Key Files
- `docker-compose.yml`: Service definitions and configuration
- `start.sh`: Container entry point - starts Xvfb, Fluxbox, x11vnc, and Playwright MCP (shared by task-runner and vnc services)
- `Dockerfile.taskrunner`: Builds n8n-task-runner image (n8n + Playwright MCP + GUI stack)
- `Dockerfile.vnc`: Builds VNC image (lighter, GUI stack only)
- `redis.conf`: Redis configuration with AOF persistence
- `.env` / `.env_sample`: Environment variables (N8N_ENCRYPTION_KEY required)

### Networking
- Services communicate via Docker network (not host networking)
- `host.docker.internal:host-gateway` maps to host machine
- Redis requires secret in `secrets/redis_password`

### Volumes (External Named Volumes)
All persistent data uses external named volumes:
- `n8n-docker-compose_n8n_data`: n8n user data and workflows
- `n8n-docker-compose_playwright_data`: Playwright browser data
- `n8n-docker-compose_redis_data`: Redis persistence (AOF)

## Configuration

Critical environment variables:
- `N8N_ENCRYPTION_KEY`: JWT secret for authentication (required)
- `N8N_RUNNERS_AUTH_TOKEN`: Shared secret for runner authentication
- `VNC_PASSWORD`: VNC access password (default: n8npassword)

Required secrets:
- `secrets/redis_password`: Redis authentication password