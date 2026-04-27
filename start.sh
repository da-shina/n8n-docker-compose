#!/bin/bash

# Don't exit on first error - we want to keep services running
# set -e  # REMOVED to prevent premature exits

# Remove lock files if they exist
rm -rf /tmp/.X* /tmp/.xvfb* /home/pwuser/user-data/SingletonLock 2>/dev/null || true
mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix || true

# Start Xvfb
export DISPLAY=:99
echo "Starting Xvfb..."
Xvfb :99 -screen 0 1280x720x16 -fbdir /tmp -nolisten tcp > /dev/null 2>&1 &
sleep 2

# Start Fluxbox (Window Manager)
echo "Starting Fluxbox..."
fluxbox > /dev/null 2>&1 &
sleep 1

# Start x11vnc with password protection
echo "Starting x11vnc..."
x11vnc -display :99 -forever -passwd "${VNC_PASSWORD:-n8npassword}" -shared > /dev/null 2>&1 &
sleep 1

echo "GUI environment ready for VNC access at :5900"

# Start Playwright MCP server only for task-runner
if [ "$N8N_INSTANCE_TYPE" = "runner" ] && type playwright-mcp > /dev/null 2>&1; then
  echo "Starting Playwright MCP server on port 8931..."

  # Create working directory in user's home to avoid permission issues
  MCP_WORK_DIR="$HOME/.playwright-mcp"
  if [ -z "$HOME" ] || [ ! -w "$HOME" ]; then
    MCP_WORK_DIR="/tmp/.playwright-mcp"
  fi
  mkdir -p "$MCP_WORK_DIR" 2>/dev/null || true
  cd "$MCP_WORK_DIR" 2>/dev/null || cd /tmp || true

  # Dynamically detect Playwright Chromium path
  CHROME_PATH=""

  # Try multiple methods to find Chromium
  if command -v playwright > /dev/null 2>&1; then
    CHROME_PATH=$(playwright install --dry-run chromium 2>/dev/null | grep -o '/[^ ]*chrome' | head -1 || echo "")
  fi

  if [ -z "$CHROME_PATH" ]; then
    CHROME_PATH=$(node -e "
      try {
        const { chromium } = require('playwright-core');
        console.log(chromium.executablePath());
      } catch(e) {
        console.log('');
      }
    " 2>/dev/null || echo "")
  fi

  # Try to find chromium in common locations
  if [ -z "$CHROME_PATH" ] || [ ! -f "$CHROME_PATH" ]; then
    for path in \
      /ms-playwright/chromium-*/chrome-linux/chrome \
      /ms-playwright/chromium-*/chrome-win/chrome.exe \
      /home/pwuser/.cache/ms-playwright/chromium-*/chrome-linux/chrome \
      /root/.cache/ms-playwright/chromium-*/chrome-linux/chrome; do
      if ls $path 1> /dev/null 2>&1; then
        CHROME_PATH=$(ls $path | head -1)
        break
      fi
    done
  fi

  # Check if Playwright MCP is already running
  if pgrep -f "playwright-mcp.*--port 8931" > /dev/null; then
    echo "Playwright MCP is already running on port 8931"
  else
    # Clean up any existing browser lock files
    USER_DATA_DIR="$MCP_WORK_DIR/user-data"
    rm -rf "$USER_DATA_DIR/SingletonLock" "$USER_DATA_DIR/SingletonCookie" "$USER_DATA_DIR/SingletonSocket" 2>/dev/null || true

    if [ -n "$CHROME_PATH" ] && [ -f "$CHROME_PATH" ]; then
      echo "Using Chromium at: $CHROME_PATH"
      playwright-mcp \
        --port 8931 \
        --host 0.0.0.0 \
        --allowed-hosts '*' \
        --browser chromium \
        --executable-path "$CHROME_PATH" \
        --no-sandbox \
        --user-data-dir "$USER_DATA_DIR" \
        > /tmp/playwright-mcp.log 2>&1 &
    else
      echo "WARNING: Could not find Chromium, using default browser detection"
      playwright-mcp \
        --port 8931 \
        --host 0.0.0.0 \
        --allowed-hosts '*' \
        --browser chromium \
        --no-sandbox \
        --user-data-dir "$USER_DATA_DIR" \
        > /tmp/playwright-mcp.log 2>&1 &
    fi
  fi

  # Verify startup
  sleep 3
  if ps aux | grep -q "[p]laywright-mcp"; then
    echo "Playwright MCP server started successfully"
  else
    echo "ERROR: Playwright MCP server failed to start. Check /tmp/playwright-mcp.log"
    cat /tmp/playwright-mcp.log 2>/dev/null || echo "No log file found"
  fi
fi

# Start n8n worker as the main process if available (managed by dumb-init)
if type n8n > /dev/null 2>&1 && n8n --version > /dev/null 2>&1; then
  echo "Starting n8n worker..."
  exec n8n worker
else
  echo "n8n not available. Keeping container alive for VNC access..."
  exec sleep infinity
fi
