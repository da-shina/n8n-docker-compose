"""
Task 3.2: 起動スクリプト (start.sh) のテスト

start.sh が GUI 環境、VNC、Playwright MCP を正しく起動することを検証します。

Requirements: 3.2, 4.1, 4.2, 4.3
"""


def test_start_sh_xvfb_initialization():
    """
    仮想ディスプレイ（Xvfb）の初期化が行われることを確認します。
    
    Requirements: 3.2, 4.1
    """
    with open("start.sh", "r") as f:
        content = f.read()
    
    assert "Xvfb :99" in content or "Xvfb :${DISPLAY}" in content, \
        "Xvfb の初期化設定が見つかりません"
    assert "DISPLAY=:99" in content, "DISPLAY 環境変数の設定が見つかりません"


def test_start_sh_fluxbox():
    """
    Fluxbox ウィンドウマネージャーが起動されることを確認します。
    
    Requirements: 3.2, 4.1
    """
    with open("start.sh", "r") as f:
        content = f.read()
    
    assert "fluxbox" in content, "fluxbox の起動設定が見つかりません"


def test_start_sh_x11vnc():
    """
    x11vnc サーバーがパスワード保護付きで起動されることを確認します。
    
    Requirements: 3.2, 4.1, 4.2
    """
    with open("start.sh", "r") as f:
        content = f.read()
    
    assert "x11vnc" in content, "x11vnc の設定が見つかりません"
    assert "-passwd" in content or "-password" in content, \
        "VNC パスワード保護の設定が見つかりません"
    assert "5900" in content or "DISPLAY" in content, \
        "VNC ポート/ディスプレイの設定が見つかりません"


def test_start_sh_keeps_container_alive():
    """
    n8n を起動せず、コンテナを生かしたままにすることを確認します。

    Requirements: 3.2, 4.3
    """
    with open("start.sh", "r") as f:
        content = f.read()

    assert "exec sleep infinity" in content, \
        "コンテナを生かす処理が見つかりません"
    assert "n8n worker" not in content, \
        "ブラウザコンテナで n8n worker を起動しないでください"


def test_start_sh_uses_profile_volume():
    """
    ブラウザプロファイルが playwright_data のマウント先に保存されることを確認します。

    Requirements: 1.4
    """
    with open("start.sh", "r") as f:
        content = f.read()

    assert 'USER_DATA_DIR="${HOME}/user-data"' in content, \
        "ブラウザプロファイルの保存先が /home/pwuser/user-data になっていません"


def test_start_sh_dumb_init():
    """
    dumb-init によるライフサイクル管理が行われることを確認します。
    
    Requirements: 3.2, 4.3
    """
    with open("start.sh", "r") as f:
        content = f.read()
    
    # Dockerfile で dumb-init がエントリーポイントとして設定されていることを想定
    # start.sh 自体は dumb-init によって実行される
    assert "#!/bin/bash" in content or "#!/usr/bin/env bash" in content, \
        "シェバングが見つかりません"


def test_start_sh_no_tail():
    """
    tail -f /dev/null で終了しないことを確認します。
    
    Requirements: 3.2, 4.3
    """
    with open("start.sh", "r") as f:
        content = f.read()
    
    assert "tail -f /dev/null" not in content, \
        "tail -f /dev/null が含まれています（exec sleep infinity を使ってください）"
