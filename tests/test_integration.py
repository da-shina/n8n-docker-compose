import subprocess
import time

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def test_containers_running():
    """Check if all services are running."""
    stdout, _, _ = run_command("/opt/podman/bin/podman ps --format '{{.Names}}'")
    print(f"Running containers: {stdout}")
    assert "n8n-main" in stdout
    assert "n8n-taskrunner" in stdout
    assert "redis" in stdout

def test_redis_connection():
    """Verify n8n-main can ping redis."""
    # Find the actual container name for n8n-main
    stdout, _, _ = run_command("/opt/podman/bin/podman ps --filter 'name=n8n-main' --format '{{.Names}}'")
    main_container = stdout.split('\n')[0].strip()
    print(f"Main container: {main_container}")
    
    # Try to ping redis by its service name in the network
    # We use 'redis' which is the service name in docker-compose.yml
    _, stderr, code = run_command(f"/opt/podman/bin/podman exec {main_container} nc -z redis 6379")
    if code != 0:
        print(f"NC failed: {stderr}")
    assert code == 0
    print("✅ n8n-main can reach redis:6379")

def test_runner_auth_token():
    """Verify both containers have the same N8N_RUNNERS_AUTH_TOKEN."""
    stdout_main, _, _ = run_command("/opt/podman/bin/podman ps --filter 'name=n8n-main' --format '{{.Names}}'")
    main_container = stdout_main.split('\n')[0].strip()
    
    stdout_runner, _, _ = run_command("/opt/podman/bin/podman ps --filter 'name=n8n-taskrunner' --format '{{.Names}}'")
    runner_container = stdout_runner.split('\n')[0].strip()
    
    main_token, _, _ = run_command(f"/opt/podman/bin/podman exec {main_container} printenv N8N_RUNNERS_AUTH_TOKEN")
    runner_token, _, _ = run_command(f"/opt/podman/bin/podman exec {runner_container} printenv N8N_RUNNERS_AUTH_TOKEN")
    
    print(f"Main token: {main_token}")
    print(f"Runner token: {runner_token}")
    assert main_token == runner_token
    assert len(main_token) > 0

if __name__ == "__main__":
    # We might need to start them first
    print("Starting services...")
    run_command("/opt/podman/bin/podman compose up -d")
    
    # Wait for startup
    print("Waiting for containers to stabilize...")
    time.sleep(10)
    
    try:
        test_containers_running()
        test_redis_connection()
        test_runner_auth_token()
        print("✅ Integration tests passed")
    except AssertionError as e:
        print(f"❌ Integration test failed: {e}")
        # Not stopping, just reporting
    except Exception as e:
        print(f"❌ Error during integration tests: {e}")
