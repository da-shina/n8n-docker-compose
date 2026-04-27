# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Container Management
```bash
# Start all services
podman compose up -d

# Rebuild and start (after Dockerfile changes)
podman compose up -d --build

# View logs
podman compose logs -f [service-name]

# Stop services
podman compose down
```

### Testing
```bash
# Run all tests
cd tests && python -m pytest

# Run specific test file
python -m pytest tests/test_env_config.py

# Run a single test
python -m pytest tests/test_env_config.py::test_env_sample_has_runner_settings -v
```

## Architecture

This project runs n8n (workflow automation platform) with external task runners and Playwright browser automation.

### Services
- **n8n**: Main n8n instance on port 5678
- **n8n-task-runner**: External task runner with Playwright MCP server on port 8931
- **redis**: Message queue (port 6379)
- **vnc**: VNC server on port 5900 (for Playwright browser GUI)

### Key Files
- `docker-compose.yml`: Service definitions and configuration
- `start.sh`: Container entry point - starts Xvfb, Fluxbox, x11vnc, and Playwright MCP
- `Dockerfile.taskrunner`: Builds n8n-task-runner image
- `Dockerfile.vnc`: Builds VNC image
- `.env` / `.env_sample`: Environment variables (N8N_ENCRYPTION_KEY required)

### Networking
- Services communicate via Docker network (not host networking)
- `host.docker.internal:host-gateway` maps to host machine
- Redis requires secret in `secrets/redis_password`

## Configuration

Critical environment variables:
- `N8N_ENCRYPTION_KEY`: JWT secret for authentication
- `N8N_RUNNERS_AUTH_TOKEN`: Shared secret for runner authentication
- `VNC_PASSWORD`: VNC access password (default: n8npassword)