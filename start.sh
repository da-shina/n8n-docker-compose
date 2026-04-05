#!/bin/bash

set -e

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

# Start n8n worker as the main process if available (managed by dumb-init)
if type n8n > /dev/null 2>&1 && n8n --version > /dev/null 2>&1; then
  echo "Starting n8n worker..."
  exec n8n worker
else
  echo "n8n not available. Keeping container alive for VNC access..."
  exec sleep infinity
fi
