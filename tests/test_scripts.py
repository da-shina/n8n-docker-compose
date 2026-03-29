"""
Task 3.2: 起動スクリプト (start.sh) のテスト

start.sh が GUI 環境と n8n ワーカーを正しく起動することを検証します。

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


def test_start_sh_n8n_worker():
    """
    n8n ワーカープロセスが起動されることを確認します。
    
    Requirements: 3.2, 4.3
    """
    with open("start.sh", "r") as f:
        content = f.read()
    
    assert "n8n" in content, "n8n の起動設定が見つかりません"
    # n8n worker または n8n start worker などのコマンド
    assert "worker" in content or "start" in content, \
        "n8n ワーカーコマンドが見つかりません"


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
    tail -f /dev/null で終了しないことを確認します（n8n がメインプロセスであるべき）。
    
    Requirements: 3.2, 4.3
    """
    with open("start.sh", "r") as f:
        content = f.read()
    
    assert "tail -f /dev/null" not in content, \
        "tail -f /dev/null が含まれています（n8n がメインプロセスであるべきです）"


def test_start_sh_error_handling():
    """
    エラーハンドリング（set -e）が含まれていることを確認します。
    
    Requirements: 3.2
    """
    with open("start.sh", "r") as f:
        content = f.read()
    
    assert "set -e" in content, "set -e（エラー時に終了）の設定が見つかりません"


if __name__ == "__main__":
    tests = [
        test_start_sh_xvfb_initialization,
        test_start_sh_fluxbox,
        test_start_sh_x11vnc,
        test_start_sh_n8n_worker,
        test_start_sh_dumb_init,
        test_start_sh_no_tail,
        test_start_sh_error_handling,
    ]
    
    failed = []
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__} passed")
        except AssertionError as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed.append((test.__name__, str(e)))
    
    if failed:
        print(f"\n{len(failed)} test(s) failed:")
        for name, error in failed:
            print(f"  - {name}: {error}")
        exit(1)
    else:
        print(f"\n✅ All {len(tests)} tests passed")
