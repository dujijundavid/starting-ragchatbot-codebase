"""Convenience script for starting the backend FastAPI server."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import uvicorn


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start the Course Materials RAG backend server."
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface to bind (default: 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="TCP port to bind (default: 8000).",
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto-reload (enabled by default for development).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    project_root = Path(__file__).resolve().parent
    backend_dir = project_root / "backend"

    if not backend_dir.exists():
        raise SystemExit("Error: backend directory not found.")

    # Check for .env file and provide helpful error messages
    env_file = project_root / ".env"
    backend_env_file = backend_dir / ".env"
    
    if not env_file.exists() and not backend_env_file.exists():
        print("⚠️  Warning: No .env file found.")
        print("   Create .env in project root with:")
        print("   LLM_PROVIDER=deepseek")
        print("   DEEPSEEK_API_KEY=your_api_key_here")
        print()
    
    # Load environment variables before changing directory
    try:
        from dotenv import load_dotenv
        if env_file.exists():
            load_dotenv(env_file)
            print(f"✓ Loaded environment from {env_file}")
        elif backend_env_file.exists():
            load_dotenv(backend_env_file)
            print(f"✓ Loaded environment from {backend_env_file}")
    except Exception as e:
        print(f"⚠️  Warning: Could not load .env file: {e}")
        print("   Make sure the file has correct permissions (chmod 644 .env)")
        print()

    # Ensure backend package is importable and change to backend directory so
    # relative paths in the app (e.g. ../docs) resolve as expected.
    sys.path.insert(0, str(backend_dir))
    os.chdir(backend_dir)

    reload_enabled = not args.no_reload
    uvicorn_kwargs = {
        "app": "app:app",
        "host": args.host,
        "port": args.port,
        "reload": reload_enabled,
    }
    if reload_enabled:
        uvicorn_kwargs["reload_dirs"] = [str(backend_dir)]

    print(
        f"Starting FastAPI server on http://{args.host}:{args.port} "
        f"(reload={'on' if reload_enabled else 'off'})"
    )

    uvicorn.run(**uvicorn_kwargs)


if __name__ == "__main__":
    main()

