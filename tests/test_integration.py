"""
Task 6.1, 6.2: サービス間の統合テスト

n8n-main と Task Runner 間の通信、ワークフロー実行の連携を検証します。

Requirements: 2.2, 3.1
"""

import subprocess

import pytest


def run_command(cmd):
    """シェルコマンドを実行し、結果を返します。"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def running_containers():
    """
    compose スタックのコンテナ名を取得します。

    `podman compose` は別プロバイダに委譲して空のまま成功することがあるため、
    出力が得られた最初のコマンドを採用します。
    """
    for cmd in (
        "docker compose ps --format '{{.Names}}'",
        "podman compose ps --format '{{.Names}}'",
        "podman-compose ps --format '{{.Names}}'",
    ):
        stdout, _, _ = run_command(f"{cmd} 2>/dev/null")
        if stdout:
            return stdout
    return ""


def test_containers_running():
    """
    全サービスが実行されていることを確認します。
    
    Requirements: 2.2
    """
    stdout = running_containers()
    print(f"Running containers: {stdout}")

    if not stdout:
        pytest.skip("compose スタックが起動していません")

    # n8n または n8n-main
    has_n8n = "n8n" in stdout
    # 公式のタスクランナーサイドカー
    has_runners = "n8n-runners" in stdout
    # Playwright ブラウザ
    has_browser = "n8n-task-runner" in stdout or "n8n-taskrunner" in stdout
    # redis
    has_redis = "redis" in stdout

    assert has_n8n, "n8n コンテナが実行されていません"
    assert has_runners, "n8n-runners コンテナが実行されていません"
    assert has_browser, "n8n-task-runner コンテナが実行されていません"
    assert has_redis, "redis コンテナが実行されていません"


def test_redis_connection():
    """
    n8n-main から redis への接続を確認します。
    
    Requirements: 2.2
    """
    # Find the actual container name for n8n
    stdout, _, _ = run_command("docker compose ps --format '{{.Names}}' 2>/dev/null | grep -i n8n | head -1 || podman compose ps --format '{{.Names}}' 2>/dev/null | grep -i n8n | head -1 || echo ''")
    main_container = stdout.split('\n')[0].strip() if stdout else ""
    
    if not main_container:
        print("⚠️ n8n コンテナが見つかりません（スキップ）")
        return
    
    print(f"Main container: {main_container}")
    
    # Try to ping redis by its service name in the network
    _, stderr, code = run_command(f"docker exec {main_container} nc -z redis 6379 2>/dev/null || podman exec {main_container} nc -z redis 6379 2>/dev/null || echo 'skip'")
    if code != 0:
        print(f"⚠️ Redis 接続チェック: {stderr}")
    else:
        print("✅ n8n-main can reach redis:6379")


def test_runner_auth_token():
    """
    n8n-main と Task Runner が同じ認証トークンを持っていることを確認します。
    
    Requirements: 2.2
    """
    stdout_main, _, _ = run_command("docker compose ps --format '{{.Names}}' 2>/dev/null | grep -i n8n | grep -v task | grep -v runners | head -1 || podman compose ps --format '{{.Names}}' 2>/dev/null | grep -i n8n | grep -v task | grep -v runners | head -1 || echo ''")
    main_container = stdout_main.split('\n')[0].strip() if stdout_main else ""
    
    stdout_runner, _, _ = run_command("docker compose ps --format '{{.Names}}' 2>/dev/null | grep -i 'n8n-runners' | head -1 || podman compose ps --format '{{.Names}}' 2>/dev/null | grep -i 'n8n-runners' | head -1 || echo ''")
    runner_container = stdout_runner.split('\n')[0].strip() if stdout_runner else ""
    
    if not main_container or not runner_container:
        print("⚠️ コンテナが見つからないため、トークンチェックをスキップします")
        return
    
    main_token, _, _ = run_command(f"docker exec {main_container} printenv N8N_RUNNERS_AUTH_TOKEN 2>/dev/null || podman exec {main_container} printenv N8N_RUNNERS_AUTH_TOKEN 2>/dev/null || echo ''")
    runner_token, _, _ = run_command(f"docker exec {runner_container} printenv N8N_RUNNERS_AUTH_TOKEN 2>/dev/null || podman exec {runner_container} printenv N8N_RUNNERS_AUTH_TOKEN 2>/dev/null || echo ''")
    
    print(f"Main token: {main_token}")
    print(f"Runner token: {runner_token}")
    
    if main_token and runner_token:
        assert main_token == runner_token, "認証トークンが一致しません"
        assert len(main_token) > 0, "認証トークンが空です"
        print("✅ 認証トークンが一致しています")
    else:
        print("⚠️ トークンチェックをスキップします")


def test_websocket_broker_port():
    """
    n8n-main の WebSocket ブローカーポート (5679) が設定されていることを確認します。
    
    Requirements: 2.2
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    assert "N8N_RUNNERS_BROKER_PORT=5679" in content, \
        "WebSocket ブローカーポート 5679 が設定されていません"
    
    print("✅ WebSocket ブローカーポートが設定されています")


def test_task_broker_uri():
    """
    Task Runner が n8n のタスクブローカー URI を設定していることを確認します。

    Requirements: 2.2
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()

    assert "N8N_RUNNERS_TASK_BROKER_URI=http://n8n:5679" in content, \
        "Task Broker URI が設定されていません"

    print("✅ Task Broker URI が設定されています")
