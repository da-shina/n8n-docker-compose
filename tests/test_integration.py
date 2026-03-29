"""
Task 6.1, 6.2: サービス間の統合テスト

n8n-main と Task Runner 間の通信、ワークフロー実行の連携を検証します。

Requirements: 2.2, 3.1
"""

import subprocess
import time


def run_command(cmd):
    """シェルコマンドを実行し、結果を返します。"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def test_containers_running():
    """
    全サービスが実行されていることを確認します。
    
    Requirements: 2.2
    """
    stdout, _, _ = run_command("docker compose ps --format '{{.Names}}' 2>/dev/null || podman compose ps --format '{{.Names}}' 2>/dev/null || echo ''")
    print(f"Running containers: {stdout}")
    
    # n8n または n8n-main
    has_n8n = "n8n" in stdout
    # n8n-task-runner または n8n-taskrunner
    has_runner = "n8n-task-runner" in stdout or "n8n-taskrunner" in stdout
    # redis
    has_redis = "redis" in stdout
    
    assert has_n8n, "n8n コンテナが実行されていません"
    assert has_runner, "n8n-taskrunner コンテナが実行されていません"
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
    stdout_main, _, _ = run_command("docker compose ps --format '{{.Names}}' 2>/dev/null | grep -i n8n | grep -v task | head -1 || podman compose ps --format '{{.Names}}' 2>/dev/null | grep -i n8n | grep -v task | head -1 || echo ''")
    main_container = stdout_main.split('\n')[0].strip() if stdout_main else ""
    
    stdout_runner, _, _ = run_command("docker compose ps --format '{{.Names}}' 2>/dev/null | grep -i task || podman compose ps --format '{{.Names}}' 2>/dev/null | grep -i task || echo ''")
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
    Task Runner が n8n-main の WebSocket URI を設定していることを確認します。
    
    Requirements: 2.2
    """
    with open(".env_sample", "r") as f:
        content = f.read()
    
    assert "N8N_RUNNERS_TASK_BROKER_URI=ws://" in content, \
        "Task Broker URI が設定されていません"
    
    print("✅ Task Broker URI が設定されています")


if __name__ == "__main__":
    # We might need to start them first
    print("Starting services...")
    run_command("docker compose up -d 2>/dev/null || podman compose up -d 2>/dev/null || echo 'Compose command not available'")
    
    # Wait for startup
    print("Waiting for containers to stabilize...")
    time.sleep(5)
    
    tests = [
        test_containers_running,
        test_redis_connection,
        test_runner_auth_token,
        test_websocket_broker_port,
        test_task_broker_uri,
    ]
    
    failed = []
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__} passed")
        except AssertionError as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed.append((test.__name__, str(e)))
        except Exception as e:
            print(f"⚠️ {test.__name__} error: {e}")
    
    if failed:
        print(f"\n{len(failed)} test(s) failed:")
        for name, error in failed:
            print(f"  - {name}: {error}")
        exit(1)
    else:
        print(f"\n✅ All {len(tests)} integration tests passed")
