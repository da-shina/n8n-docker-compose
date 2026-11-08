"""
Task 1.1: .env_sample ファイルの更新と環境変数定義のテスト

外部タスクランナー構成に必要な環境変数が定義されていることを検証します。
"""


def test_env_sample_has_runner_settings():
    """
    外部タスクランナー向けの環境変数が .env_sample に定義されていることを確認します。

    Requirements: 1.3
    - N8N_RUNNERS_MODE
    - N8N_RUNNERS_AUTH_TOKEN
    - N8N_RUNNERS_BROKER_LISTEN_ADDRESS
    - N8N_RUNNERS_BROKER_PORT
    - N8N_RUNNERS_TASK_BROKER_URI
    - N8N_RUNNERS_ENABLED は n8n v2.x で不要（コメントのみ記載可）
    """
    with open(".env_sample", "r") as f:
        content = f.read()

    # N8N_RUNNERS_ENABLED は v2.x で非推奨
    assert "N8N_RUNNERS_ENABLED=true" not in content, "N8N_RUNNERS_ENABLED は n8n v2.x で不要です"
    assert "N8N_RUNNERS_MODE=" in content, "N8N_RUNNERS_MODE が定義されていません"
    assert "N8N_RUNNERS_AUTH_TOKEN=" in content, "N8N_RUNNERS_AUTH_TOKEN が定義されていません"
    assert "N8N_RUNNERS_BROKER_LISTEN_ADDRESS=" in content, "N8N_RUNNERS_BROKER_LISTEN_ADDRESS が定義されていません"
    assert "N8N_RUNNERS_BROKER_PORT=" in content, "N8N_RUNNERS_BROKER_PORT が定義されていません"
    assert "N8N_RUNNERS_TASK_BROKER_URI=" in content, "N8N_RUNNERS_TASK_BROKER_URI が定義されていません"


def test_env_sample_has_redis_settings():
    """
    Redis 接続設定が .env_sample に定義されていることを確認します。
    
    Requirements: 1.3
    - QUEUE_BULL_REDIS_HOST
    - QUEUE_BULL_REDIS_PORT
    - N8N_REDIS_TLS_ENABLED
    """
    with open(".env_sample", "r") as f:
        content = f.read()
    
    assert "QUEUE_BULL_REDIS_HOST=" in content, "QUEUE_BULL_REDIS_HOST が定義されていません"
    assert "QUEUE_BULL_REDIS_PORT=" in content, "QUEUE_BULL_REDIS_PORT が定義されていません"
    assert "N8N_REDIS_TLS_ENABLED=" in content, "N8N_REDIS_TLS_ENABLED が定義されていません"


def test_env_sample_has_security_settings():
    """
    セキュリティ関連の環境変数が .env_sample に定義されていることを確認します。

    Requirements: 1.3
    - N8N_ENCRYPTION_KEY
    - REDIS_PASSWORD
    """
    with open(".env_sample", "r") as f:
        content = f.read()

    assert "N8N_ENCRYPTION_KEY=" in content, "N8N_ENCRYPTION_KEY が定義されていません"
    assert "REDIS_PASSWORD=" in content, "REDIS_PASSWORD が定義されていません"


def test_env_sample_has_vnc_settings():
    """
    VNC 関連の環境変数が .env_sample に定義されていることを確認します。
    
    Requirements: 1.3
    - VNC_PASSWORD
    """
    with open(".env_sample", "r") as f:
        content = f.read()
    
    assert "VNC_PASSWORD=" in content, "VNC_PASSWORD が定義されていません"


def test_env_sample_has_task_runner_memory_settings():
    """
    タスクランナーのメモリ設定が .env_sample に定義されていることを確認します。
    
    Requirements: 1.3
    - N8N_RUNNERS_MAX_OLD_SPACE_SIZE
    """
    with open(".env_sample", "r") as f:
        content = f.read()
    
    assert "N8N_RUNNERS_MAX_OLD_SPACE_SIZE=" in content, "N8N_RUNNERS_MAX_OLD_SPACE_SIZE が定義されていません"
