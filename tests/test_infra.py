import os
import subprocess
import time

def test_docker_compose_structure():
    """Check if docker-compose.yml has the strictly required services."""
    with open("docker-compose.yml", "r") as f:
        content = f.read()

    # n8n サービス（n8n-main として機能）
    assert "n8n:" in content or "n8n-main:" in content, "n8n サービスが定義されていません"
    # n8n-taskrunner または n8n-task-runner サービス
    assert "n8n-taskrunner:" in content or "n8n-task-runner:" in content, "n8n-taskrunner サービスが定義されていません"
    assert "redis:" in content, "redis サービスが定義されていません"

def test_env_file_exists():
    """Check if .env file exists (created from .env_sample)."""
    assert os.path.exists(".env")

def test_env_variables():
    """Check if required env variables are in .env."""
    with open(".env", "r") as f:
        content = f.read()

    assert "N8N_RUNNERS_MODE=external" in content
    assert "N8N_RUNNERS_AUTH_TOKEN=" in content


def test_persistent_volumes_defined():
    """
    永続化ボリュームが定義されていることを確認します。
    
    Requirements: 1.4
    - n8n_data
    - playwright_data
    - redis_data
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    # ボリューム定義セクションの確認
    assert "volumes:" in content, "volumes セクションが定義されていません"
    assert "n8n_data:" in content, "n8n_data ボリュームが定義されていません"
    assert "playwright_data:" in content, "playwright_data ボリュームが定義されていません"
    assert "redis_data:" in content, "redis_data ボリュームが定義されていません"


def test_volume_user_permissions():
    """
    コンテナのユーザー ID 設定が 1000:1000 であることを確認します。
    
    Requirements: 1.4
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    # 各サービスのユーザー設定
    assert 'user: "1000:1000"' in content, "ユーザー ID 1000:1000 の設定が見つかりません"


def test_volume_mounts():
    """
    各サービスに適切なボリュームマウントが設定されていることを確認します。
    
    Requirements: 1.4
    """
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    # n8n_data のマウント
    assert "n8n_data:/home/node/.n8n" in content or "n8n_data:/home/pwuser/.n8n" in content, \
        "n8n_data ボリュームのマウント設定が見つかりません"
    
    # playwright_data のマウント
    assert "playwright_data:" in content, "playwright_data ボリュームのマウント設定が見つかりません"


if __name__ == "__main__":
    try:
        test_docker_compose_structure()
        print("✅ Docker Compose structure test passed")

        # This will fail initially because I haven't created .env or updated it
        test_env_file_exists()
        print("✅ .env file exists")

        test_env_variables()
        print("✅ Environment variables test passed")
        
        test_persistent_volumes_defined()
        print("✅ Persistent volumes test passed")
        
        test_volume_user_permissions()
        print("✅ Volume user permissions test passed")
        
        test_volume_mounts()
        print("✅ Volume mounts test passed")

    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        exit(1)
