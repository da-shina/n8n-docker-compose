"""
Task 3.1: Playwright ベースの Task Runner Dockerfile のテスト

Dockerfile.taskrunner が外部タスクランナーに必要な構成を持っていることを検証します。

Requirements: 1.2, 3.1
"""


def test_dockerfile_taskrunner_base_image():
    """
    Playwright ベースイメージが使用されていることを確認します。
    
    Requirements: 1.2, 3.1
    """
    with open("Dockerfile.taskrunner", "r") as f:
        content = f.read()
    
    assert "FROM mcr.microsoft.com/playwright:" in content, \
        "Playwright ベースイメージが使用されていません"


def test_dockerfile_taskrunner_playwright_mcp():
    """
    Playwright MCP がインストールされ、n8n 本体は含まれないことを確認します。

    Requirements: 1.2, 3.1
    """
    with open("Dockerfile.taskrunner", "r") as f:
        content = f.read()

    assert "@playwright/mcp" in content, "Playwright MCP のインストール設定が見つかりません"
    assert "n8n worker" not in content, "ブラウザイメージに n8n を含めないでください"


def test_dockerfile_taskrunner_gui_dependencies():
    """
    GUI 実行環境（Xvfb, fluxbox, x11vnc）がインストールされていることを確認します。
    
    Requirements: 1.2, 3.1
    """
    with open("Dockerfile.taskrunner", "r") as f:
        content = f.read()
    
    assert "x11vnc" in content, "x11vnc がインストールされていません"
    assert "xvfb" in content or "Xvfb" in content, "Xvfb がインストールされていません"
    assert "fluxbox" in content, "fluxbox がインストールされていません"


def test_dockerfile_taskrunner_display_env():
    """
    仮想ディスプレイ環境変数が設定されていることを確認します。
    
    Requirements: 1.2, 3.1
    """
    with open("Dockerfile.taskrunner", "r") as f:
        content = f.read()
    
    assert "DISPLAY=:99" in content, "DISPLAY=:99 の環境変数が設定されていません"


def test_dockerfile_taskrunner_dumb_init():
    """
    dumb-init がインストールされていることを確認します（ライフサイクル管理用）。
    
    Requirements: 1.2, 3.1
    """
    with open("Dockerfile.taskrunner", "r") as f:
        content = f.read()
    
    assert "dumb-init" in content, "dumb-init がインストールされていません"
