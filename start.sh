#!/bin/sh

set -e

# ロックファイルを削除
rm -rf /tmp/.X* /tmp/.xvfb* /home/pwuser/user-data/SingletonLock 2>/dev/null || true
mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix || true

# Xサーバー、ウィンドウマネージャー、VNCサーバーをバックグラウンドで起動
export DISPLAY=:99

echo "Starting Xvfb..."
Xvfb :99 -screen 0 1280x720x16 -fbdir /tmp -nolisten tcp > /dev/null 2>&1 &
sleep 2

echo "Starting Fluxbox..."
fluxbox > /dev/null 2>&1 &
sleep 2

echo "Starting x11vnc..."
x11vnc -display :99 -forever -passwd n8npassword -shared > /dev/null 2>&1 &
sleep 2

echo "Starting n8n..."
# PlaywrightがGUI環境を正しく認識できるようにDISPLAYを設定
export DISPLAY=:99

# n8nが適切なホームディレクトリを使用するように設定（念のため）
export N8N_USER_FOLDER=/home/pwuser/.n8n

# n8nを起動
exec n8n
  
  
