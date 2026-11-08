#!/bin/bash

# ヘルパープロセスの1つが失敗してもコンテナを生かし続ける。
# `set -e` は追加しない: ウィンドウマネージャが停止しても VNC や Playwright MCP を止めないため。

export DISPLAY=:99
USER_DATA_DIR="${HOME}/user-data"

# 前回の実行から残った X やブラウザのロックファイルを削除する。
rm -rf /tmp/.X* /tmp/.xvfb* \
  "$USER_DATA_DIR/SingletonLock" \
  "$USER_DATA_DIR/SingletonCookie" \
  "$USER_DATA_DIR/SingletonSocket" 2>/dev/null || true
mkdir -p /tmp/.X11-unix "$USER_DATA_DIR" 2>/dev/null || true
chmod 1777 /tmp/.X11-unix 2>/dev/null || true

wait_for_socket() {
  for _ in $(seq 1 50); do
    [ -S "$1" ] && return 0
    sleep 0.2
  done
  return 1
}

echo "Starting Xvfb..."
Xvfb :99 -screen 0 1280x720x16 -fbdir /tmp -nolisten tcp > /dev/null 2>&1 &
if ! wait_for_socket /tmp/.X11-unix/X99; then
  echo "ERROR: Xvfb did not start" >&2
fi

echo "Starting Fluxbox..."
fluxbox > /dev/null 2>&1 &

echo "Starting x11vnc..."
x11vnc -display :99 -forever -passwd "${VNC_PASSWORD:?VNC_PASSWORD is required}" -shared > /dev/null 2>&1 &

echo "GUI environment ready for VNC access at :5900"

echo "Starting Playwright MCP server on port 8931..."
cd "$USER_DATA_DIR" 2>/dev/null || cd /tmp || true

# イメージは @playwright/mcp のバージョンに合う Chromium ビルドを PLAYWRIGHT_BROWSERS_PATH にインストールするため、パス検出は不要。
if pgrep -f "playwright-mcp.*--port 8931" > /dev/null; then
  echo "Playwright MCP is already running on port 8931"
else
  playwright-mcp \
    --port 8931 \
    --host 0.0.0.0 \
    --allowed-hosts "n8n-task-runner:8931,playwright:8931,host.docker.internal:8931,127.0.0.1:8931,localhost:8931" \
    --browser chromium \
    --no-sandbox \
    --user-data-dir "$USER_DATA_DIR" \
    > /tmp/playwright-mcp.log 2>&1 &
fi

# 固定のスリープを使わず MCP プロセスの起動を待つ。
for _ in $(seq 1 50); do
  pgrep -f "playwright-mcp.*--port 8931" > /dev/null && break
  sleep 0.2
done
if pgrep -f "playwright-mcp.*--port 8931" > /dev/null; then
  echo "Playwright MCP server started successfully"
else
  echo "ERROR: Playwright MCP server failed to start. Check /tmp/playwright-mcp.log" >&2
  cat /tmp/playwright-mcp.log 2>/dev/null || true
fi

echo "Container is ready. Keeping it alive..."
exec sleep infinity
