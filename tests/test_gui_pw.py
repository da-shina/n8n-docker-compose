"""
Task 5.1, 5.2: Playwright と VNC 統合の検証テスト

Playwright 実行環境と VNC による GUI 操作可視化の設定を検証します。

Requirements: 3.1, 3.2, 4.1, 4.2, 4.3
"""


def test_playwright_base_image():
    """
    Playwright ベースイメージが使用されていることを確認します。
    
    Requirements: 3.1
    """
    with open("Dockerfile.taskrunner", "r") as f:
        content = f.read()
    
    assert "FROM mcr.microsoft.com/playwright:" in content, \
        "Playwright ベースイメージが使用されていません"


def test_playwright_browser_dependencies():
    """
    Playwright のブラウザ依存関係がインストールされることを確認します。
    
    Requirements: 3.1
    """
    with open("Dockerfile.taskrunner", "r") as f:
        content = f.read()
    
    # Playwright が必要なシステムライブラリ
    required_libs = [
        "libatk1.0-0",
        "libatk-bridge2.0-0",
        "libcups2",
        "libnss3",
        "libgbm1",
        "libgtk-3-0",
    ]
    
    for lib in required_libs:
        assert lib in content, f"{lib} がインストールされていません"


def test_vnc_port_exposed():
    """
    VNC サーバーのポート 5900 が公開されていることを確認します。
    
    Requirements: 4.1, 4.2
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    # Dockerfile.taskrunner または docker-compose.yml で 5900 ポートが公開されている
    with open("Dockerfile.taskrunner", "r") as df:
        dockerfile_content = df.read()
    
    assert "5900" in content or "5900" in dockerfile_content, \
        "VNC ポート 5900 が公開されていません"


def test_vnc_password_protection():
    """
    VNC サーバーがパスワード保護されていることを確認します。
    
    Requirements: 4.2
    """
    with open("start.sh", "r") as f:
        content = f.read()
    
    assert "x11vnc" in content, "x11vnc の設定が見つかりません"
    assert "-passwd" in content or "-password" in content, \
        "VNC パスワード保護の設定が見つかりません"
    
    # 環境変数からパスワードが設定されている（デフォルト値を含む）
    assert "VNC_PASSWORD" in content, \
        "VNC_PASSWORD 環境変数の使用が見つかりません"


def test_vnc_password_env_defined():
    """
    VNC_PASSWORD 環境変数が .env_sample に定義されていることを確認します。
    
    Requirements: 4.2
    """
    with open(".env_sample", "r") as f:
        content = f.read()
    
    assert "VNC_PASSWORD=" in content, \
        "VNC_PASSWORD が .env_sample に定義されていません"


def test_display_environment():
    """
    仮想ディスプレイ環境が設定されていることを確認します。
    
    Requirements: 3.2, 4.1
    """
    with open("Dockerfile.taskrunner", "r") as f:
        dockerfile_content = f.read()
    
    with open("start.sh", "r") as f:
        start_sh_content = f.read()
    
    # Dockerfile または start.sh で DISPLAY が設定されている
    assert "DISPLAY=:99" in dockerfile_content or "DISPLAY=:99" in start_sh_content, \
        "DISPLAY=:99 の設定が見つかりません"


def test_xvfb_screen_config():
    """
    Xvfb のスクリーン設定が適切であることを確認します。
    
    Requirements: 4.1
    """
    with open("start.sh", "r") as f:
        content = f.read()
    
    # Xvfb のスクリーン設定（解像度など）
    assert "-screen" in content or "1280x720" in content, \
        "Xvfb のスクリーン設定が見つかりません"


if __name__ == "__main__":
    tests = [
        test_playwright_base_image,
        test_playwright_browser_dependencies,
        test_vnc_port_exposed,
        test_vnc_password_protection,
        test_vnc_password_env_defined,
        test_display_environment,
        test_xvfb_screen_config,
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
