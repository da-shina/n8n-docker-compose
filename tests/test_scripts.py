def test_start_sh_content():
    """Check if start.sh contains the GUI start and task runner execution."""
    with open("start.sh", "r") as f:
        content = f.read()
    
    assert "Xvfb :99" in content
    assert "fluxbox" in content
    assert "x11vnc" in content
    # It should launch n8n-taskrunner or n8n worker/worker-runner
    assert "n8n" in content
    # It should NOT end with tail -f /dev/null if it's supposed to run n8n
    assert "tail -f /dev/null" not in content

if __name__ == "__main__":
    try:
        test_start_sh_content()
        print("✅ start.sh test passed")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        exit(1)
