"""
Task 4.1: n8n-taskrunner サービスの設定のテスト

n8n-taskrunner サービスが正しく設定されていることを検証します。

Requirements: 1.1, 2.2, 2.4
"""


def test_taskrunner_service_build_config():
    """
    n8n-taskrunner サービスが Dockerfile.taskrunner からビルドされることを確認します。
    
    Requirements: 1.1
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    # n8n-task-runner または n8n-taskrunner サービスの存在
    assert "n8n-task-runner:" in content or "n8n-taskrunner:" in content, \
        "n8n-taskrunner サービスが定義されていません"
    
    # Dockerfile.taskrunner の参照
    assert "Dockerfile.taskrunner" in content, \
        "Dockerfile.taskrunner の参照が見つかりません"


def test_taskrunner_runner_mode():
    """
    n8n-taskrunner サービスが外部タスクランナーモードに設定されていることを確認します。
    
    Requirements: 2.2
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    assert "N8N_RUNNERS_MODE=external" in content, \
        "N8N_RUNNERS_MODE=external が設定されていません"


def test_taskrunner_auth_token():
    """
    n8n-taskrunner サービスの認証トークンが設定されていることを確認します。
    
    Requirements: 2.2
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    assert "N8N_RUNNERS_AUTH_TOKEN=" in content, \
        "N8N_RUNNERS_AUTH_TOKEN が設定されていません"


def test_taskrunner_redis_settings():
    """
    n8n-taskrunner サービスの Redis 接続設定が正しく構成されていることを確認します。
    
    Requirements: 2.2
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    assert "QUEUE_BULL_REDIS_HOST=redis" in content, \
        "QUEUE_BULL_REDIS_HOST=redis が設定されていません"
    assert "QUEUE_BULL_REDIS_PORT=6379" in content, \
        "QUEUE_BULL_REDIS_PORT=6379 が設定されていません"


def test_taskrunner_volumes():
    """
    n8n-taskrunner サービスに適切なボリュームがマウントされていることを確認します。
    
    Requirements: 1.1
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    # n8n_data のマウント
    assert "n8n_data:" in content, "n8n_data ボリュームのマウントが見つかりません"
    # playwright_data のマウント
    assert "playwright_data:" in content, "playwright_data ボリュームのマウントが見つかりません"


def test_taskrunner_user_permissions():
    """
    n8n-taskrunner サービスのユーザー権限が 1000:1000 に設定されていることを確認します。
    
    Requirements: 1.1
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    assert 'user: "1000:1000"' in content, \
        "ユーザー ID 1000:1000 の設定が見つかりません"


def test_taskrunner_restart_policy():
    """
    n8n-taskrunner サービスの再起動ポリシーが設定されていることを確認します。
    
    Requirements: 2.4
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    assert "restart: unless-stopped" in content, \
        "restart: unless-stopped ポリシーが見つかりません"


def test_taskrunner_memory_settings():
    """
    タスクランナーのメモリ設定が .env_sample に定義されていることを確認します。
    
    Requirements: 2.4
    """
    with open(".env_sample", "r") as f:
        content = f.read()
    
    assert "N8N_RUNNERS_MAX_OLD_SPACE_SIZE=" in content, \
        "N8N_RUNNERS_MAX_OLD_SPACE_SIZE が定義されていません"
    assert "NODE_OPTIONS=" in content and "max-old-space-size" in content, \
        "NODE_OPTIONS の max-old-space-size 設定が見つかりません"


if __name__ == "__main__":
    tests = [
        test_taskrunner_service_build_config,
        test_taskrunner_runner_mode,
        test_taskrunner_auth_token,
        test_taskrunner_redis_settings,
        test_taskrunner_volumes,
        test_taskrunner_user_permissions,
        test_taskrunner_restart_policy,
        test_taskrunner_memory_settings,
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
