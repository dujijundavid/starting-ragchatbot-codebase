"""Diagnostic script to check server startup issues."""

import sys
import os
from pathlib import Path

print("=== Environment Check ===")
print(f"Python: {sys.version}")
print(f"CWD: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")

# Check .env file
env_path = Path(".env")
backend_env = Path("backend/.env")
print(f"\n=== .env File Check ===")
print(f".env exists: {env_path.exists()}")
print(f"backend/.env exists: {backend_env.exists()}")

if env_path.exists():
    print(f".env location: {env_path.resolve()}")
if backend_env.exists():
    print(f"backend/.env location: {backend_env.resolve()}")

# Try to import backend modules
print("\n=== Import Check ===")
try:
    sys.path.insert(0, str(Path("backend").resolve()))
    os.chdir("backend")
    print(f"Changed to: {os.getcwd()}")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\nEnvironment variables:")
    print(f"  LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'NOT SET')}")
    print(f"  DEEPSEEK_API_KEY: {'SET' if os.getenv('DEEPSEEK_API_KEY') else 'NOT SET'}")
    print(f"  QWEN_API_KEY: {'SET' if os.getenv('QWEN_API_KEY') else 'NOT SET'}")
    
    from config import config
    print(f"\nConfig loaded successfully!")
    print(f"  Provider: {config.MODEL_PROVIDER}")
    print(f"  Model: {config.LLM_MODEL}")
    print(f"  API Key: {'SET' if config.LLM_API_KEY else 'NOT SET'}")
    
    print("\n=== Trying to import app ===")
    import app
    print("✓ app module imported successfully")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

