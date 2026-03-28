def test_dockerfile_taskrunner():
    """Check if Dockerfile.taskrunner has the required commands."""
    with open("Dockerfile.taskrunner", "r") as f:
        content = f.read()
    
    assert "FROM mcr.microsoft.com/playwright:v1.40.0-jammy" in content
    assert "setup_22.x" in content
    assert "n8n" in content
    assert "x11vnc" in content
    assert "xvfb" in content
    assert "fluxbox" in content
    assert "DISPLAY=:99" in content

if __name__ == "__main__":
    try:
        test_dockerfile_taskrunner()
        print("✅ Dockerfile taskrunner test passed")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        exit(1)
