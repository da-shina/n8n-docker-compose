import subprocess

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def test_vnc_port_open():
    """Verify VNC port is exposed and listening in the container."""
    stdout_runner, _, _ = run_command("/opt/podman/bin/podman ps --filter 'name=n8n-taskrunner' --format '{{.Names}}'")
    runner_container = stdout_runner.split('\n')[0].strip()
    
    # Check if x11vnc is listening on 5900 inside the container
    _, _, code = run_command(f"/opt/podman/bin/podman exec {runner_container} nc -z localhost 5900")
    assert code == 0
    print("✅ VNC server is listening on port 5900 inside the container")

def test_playwright_accessible():
    """Verify Playwright can be imported in the runner container."""
    stdout_runner, _, _ = run_command("/opt/podman/bin/podman ps --filter 'name=n8n-taskrunner' --format '{{.Names}}'")
    runner_container = stdout_runner.split('\n')[0].strip()
    
    # Check if playwright can be required in node
    _, stderr, code = run_command(f"/opt/podman/bin/podman exec {runner_container} node -e 'require(\"playwright\")'")
    if code != 0:
        print(f"Playwright check failed: {stderr}")
    assert code == 0
    print("✅ Playwright is accessible in the runner container")

if __name__ == "__main__":
    try:
        test_vnc_port_open()
        test_playwright_accessible()
        print("✅ GUI and Playwright verification passed")
    except AssertionError as e:
        print(f"❌ Verification failed: {e}")
