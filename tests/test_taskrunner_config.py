"""
Task 4.1: タスクランナーとブラウザサービスの設定のテスト

Code ノードは公式の n8n-runners サイドカーで実行し、
n8n-task-runner は Playwright ブラウザと VNC だけを担当します。

Requirements: 1.1, 2.2, 2.4
"""


def test_taskrunner_service_build_config():
    """
    n8n-task-runner が Dockerfile.taskrunner からビルドされることを確認します。

    Requirements: 1.1
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()

    assert "n8n-task-runner:" in content, \
        "n8n-task-runner サービスが定義されていません"
    assert "Dockerfile.taskrunner" in content, \
        "Dockerfile.taskrunner の参照が見つかりません"


def test_runners_service_uses_official_image():
    """
    公式の n8nio/runners イメージを使うサイドカーがあることを確認します。

    Requirements: 2.2
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()

    assert "n8n-runners:" in content, "n8n-runners サービスが定義されていません"
    assert "n8nio/runners:" in content, "n8nio/runners イメージが使われていません"


def test_runners_service_auth_token():
    """
    n8n-runners が n8n と同じ認証トークンを受け取ることを確認します。

    Requirements: 2.2
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()

    assert "N8N_RUNNERS_AUTH_TOKEN=${N8N_RUNNERS_AUTH_TOKEN" in content, \
        "N8N_RUNNERS_AUTH_TOKEN が環境変数から設定されていません"


def test_runners_service_broker_uri():
    """
    n8n-runners が n8n のタスクブローカーを指していることを確認します。

    Requirements: 2.2
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()

    assert "N8N_RUNNERS_TASK_BROKER_URI=http://n8n:5679" in content, \
        "N8N_RUNNERS_TASK_BROKER_URI が n8n:5679 を指していません"


def test_browser_service_mounts_profile_volume():
    """
    ブラウザプロファイルが playwright_data に保存されることを確認します。

    Requirements: 1.4
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()

    assert "playwright_data:/home/pwuser/user-data" in content, \
        "playwright_data がブラウザのプロファイルディレクトリにマウントされていません"


def test_taskrunner_user_permissions():
    """
    n8n-task-runner のユーザー権限が 1000:1000 に設定されていることを確認します。

    Requirements: 1.1
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()

    assert 'user: "1000:1000"' in content, \
        "ユーザー ID 1000:1000 の設定が見つかりません"


def test_taskrunner_restart_policy():
    """
    再起動ポリシーが設定されていることを確認します。

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
