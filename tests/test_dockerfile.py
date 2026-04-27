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


def test_dockerfile_taskrunner_nodejs_installation():
    """
    Node.js 22.x がインストールされていることを確認します。
    
    Requirements: 1.2, 3.1
    """
    with open("Dockerfile.taskrunner", "r") as f:
        content = f.read()
    
    assert "setup_22.x" in content, "Node.js 22.x のインストール設定が見つかりません"
    assert "n8n" in content, "n8n パッケージのインストール設定が見つかりません"


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


def test_dockerfile_taskrunner_python_support():
    """
    Python サポートがインストールされていることを確認します。
    
    Requirements: 1.2, 3.1
    """
    with open("Dockerfile.taskrunner", "r") as f:
        content = f.read()
    
    assert "python3" in content, "python3 がインストールされていません"
    assert "pip" in content, "pip がインストールされていません"


if __name__ == "__main__":
    tests = [
        test_dockerfile_taskrunner_base_image,
        test_dockerfile_taskrunner_nodejs_installation,
        test_dockerfile_taskrunner_gui_dependencies,
        test_dockerfile_taskrunner_display_env,
        test_dockerfile_taskrunner_dumb_init,
        test_dockerfile_taskrunner_python_support,
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
