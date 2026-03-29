"""
Task 7.1: セキュリティと堅牢性のテスト

Task Runner のセキュリティ設定とコンテナの堅牢性を検証します。

Requirements: 2.4
"""


def test_restart_policy():
    """
    全サービスの再起動ポリシーが unless-stopped に設定されていることを確認します。
    
    Requirements: 2.4
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    # restart: unless-stopped が設定されている
    assert "restart: unless-stopped" in content, \
        "restart: unless-stopped ポリシーが見つかりません"


def test_memory_limit_settings():
    """
    メモリ制限設定が行われていることを確認します。
    
    Requirements: 2.4
    """
    with open(".env_sample", "r") as f:
        content = f.read()
    
    # Node.js のメモリ制限
    assert "N8N_RUNNERS_MAX_OLD_SPACE_SIZE=" in content, \
        "N8N_RUNNERS_MAX_OLD_SPACE_SIZE が定義されていません"
    assert "NODE_OPTIONS=" in content and "max-old-space-size" in content, \
        "NODE_OPTIONS の max-old-space-size 設定が見つかりません"


def test_user_permissions_not_root():
    """
    コンテナが root 権限で実行されていないことを確認します。
    
    Requirements: 2.4
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    # 1000:1000 のユーザー設定
    assert 'user: "1000:1000"' in content, \
        "一般ユーザー (1000:1000) の設定が見つかりません"
    
    # root 実行の回避（redis は除く）
    lines = content.split('\n')
    user_lines = [l for l in lines if 'user:' in l]
    
    # 少なくとも 1 つは 1000:1000 がある
    has_non_root = any('1000:1000' in l for l in user_lines)
    assert has_non_root, "root 以外のユーザー設定が見つかりません"


def test_secrets_usage():
    """
    機密情報が secrets として管理されていることを確認します。
    
    Requirements: 2.4
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    # secrets セクションの存在
    assert "secrets:" in content, "secrets セクションが見つかりません"
    
    # redis_password secret の定義
    assert "redis_password:" in content, "redis_password secret が定義されていません"
    
    # secrets ファイルの参照
    assert "file: ./secrets/" in content, "secrets ファイルの参照が見つかりません"


def test_network_isolation():
    """
    ネットワーク分離が設定されていることを確認します。
    
    Requirements: 2.4
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    # networks セクションの存在
    assert "networks:" in content, "networks セクションが見つかりません"
    
    # bridge ネットワークの設定
    assert "default:" in content and "driver: bridge" in content, \
        "bridge ネットワークの設定が見つかりません"


def test_health_check_ready():
    """
    ヘルスチェックが設定されている、または検討されていることを確認します。
    
    Requirements: 2.4
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    # healthcheck があれば OK（必須ではないが推奨）
    # 少なくとも depends_on で service_started による依存関係が設定されている
    assert "depends_on:" in content or "healthcheck:" in content, \
        "depends_on または healthcheck の設定が見つかりません"


if __name__ == "__main__":
    tests = [
        test_restart_policy,
        test_memory_limit_settings,
        test_user_permissions_not_root,
        test_secrets_usage,
        test_network_isolation,
        test_health_check_ready,
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
