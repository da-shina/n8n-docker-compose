import subprocess
import sys

def test_python_env():
    print(f"Python version: {sys.version}")
    try:
        import pandas
        print("✅ pandas is installed")
    except ImportError:
        print("❌ pandas is NOT installed")
    
    try:
        import numpy
        print("✅ numpy is installed")
    except ImportError:
        print("❌ numpy is NOT installed")

if __name__ == "__main__":
    test_python_env()
