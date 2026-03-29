"""
Task 2.1: n8n-main サービスの外部タスクランナーモード設定のテスト

n8n-main サービスが外部タスクランナーモードで正しく設定されていることを検証します。

Requirements: 2.2
"""


def test_n8n_main_runner_mode():
    """
    n8n-main サービスが外部タスクランナーモードに設定されていることを確認します。
    
    - N8N_RUNNERS_ENABLED=true
    - N8N_RUNNERS_MODE=external
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    assert "N8N_RUNNERS_ENABLED=true" in content, "N8N_RUNNERS_ENABLED=true が設定されていません"
    assert "N8N_RUNNERS_MODE=external" in content, "N8N_RUNNERS_MODE=external が設定されていません"


def test_n8n_main_auth_token():
    """
    n8n-main サービスの認証トークンが環境変数から設定されていることを確認します。
    
    - N8N_RUNNERS_AUTH_TOKEN=${N8N_RUNNERS_AUTH_TOKEN}
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    assert "N8N_RUNNERS_AUTH_TOKEN=${N8N_RUNNERS_AUTH_TOKEN}" in content, \
        "N8N_RUNNERS_AUTH_TOKEN が環境変数から設定されていません"


def test_n8n_main_broker_settings():
    """
    n8n-main サービスのブローカー設定が正しく構成されていることを確認します。
    
    - N8N_RUNNERS_BROKER_LISTEN_ADDRESS=0.0.0.0
    - N8N_RUNNERS_BROKER_PORT=5679
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    assert "N8N_RUNNERS_BROKER_LISTEN_ADDRESS=0.0.0.0" in content, \
        "N8N_RUNNERS_BROKER_LISTEN_ADDRESS=0.0.0.0 が設定されていません"
    assert "N8N_RUNNERS_BROKER_PORT=5679" in content, \
        "N8N_RUNNERS_BROKER_PORT=5679 が設定されていません"


def test_n8n_main_redis_settings():
    """
    n8n-main サービスの Redis 接続設定が正しく構成されていることを確認します。
    
    - QUEUE_BULL_REDIS_HOST=redis
    - QUEUE_BULL_REDIS_PORT=6379
    - N8N_REDIS_TLS_ENABLED=false
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    assert "QUEUE_BULL_REDIS_HOST=redis" in content, \
        "QUEUE_BULL_REDIS_HOST=redis が設定されていません"
    assert "QUEUE_BULL_REDIS_PORT=6379" in content, \
        "QUEUE_BULL_REDIS_PORT=6379 が設定されていません"
    assert "N8N_REDIS_TLS_ENABLED=false" in content, \
        "N8N_REDIS_TLS_ENABLED=false が設定されていません"


def test_n8n_main_task_broker_uri():
    """
    Task Runner 接続用 URI が .env_sample に定義されていることを確認します。
    
    - N8N_RUNNERS_TASK_BROKER_URI=ws://n8n-main:5679
    """
    with open(".env_sample", "r") as f:
        content = f.read()
    
    assert "N8N_RUNNERS_TASK_BROKER_URI=ws://n8n" in content or \
           "N8N_RUNNERS_TASK_BROKER_URI=ws://n8n-main" in content, \
        "N8N_RUNNERS_TASK_BROKER_URI が定義されていません"


if __name__ == "__main__":
    tests = [
        test_n8n_main_runner_mode,
        test_n8n_main_auth_token,
        test_n8n_main_broker_settings,
        test_n8n_main_redis_settings,
        test_n8n_main_task_broker_uri,
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
