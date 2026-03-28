import os
import subprocess
import time
import requests

def test_docker_compose_structure():
    """Check if docker-compose.yml has the strictly required services."""
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    assert "n8n-main:" in content
    assert "n8n-taskrunner:" in content
    assert "redis:" in content
    assert "playwright:" not in content
    assert "vnc:" not in content

def test_env_file_exists():
    """Check if .env file exists (created from .env_sample)."""
    assert os.path.exists(".env")

def test_env_variables():
    """Check if required env variables are in .env."""
    with open(".env", "r") as f:
        content = f.read()
    
    assert "N8N_RUNNERS_MODE=external" in content
    assert "N8N_RUNNERS_AUTH_TOKEN=" in content

if __name__ == "__main__":
    try:
        test_docker_compose_structure()
        print("✅ Docker Compose structure test passed")
        
        # This will fail initially because I haven't created .env or updated it
        test_env_file_exists()
        print("✅ .env file exists")
        
        test_env_variables()
        print("✅ Environment variables test passed")
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        exit(1)
