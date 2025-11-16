#!/usr/bin/env python3
"""
Utility CLI to kill any running uvicorn server on the configured port
and start a fresh instance from the backend directory.
"""
import os
import subprocess
from pathlib import Path

import click

REPO_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = REPO_ROOT / "backend"


def _run_command(cmd, cwd=None, check=True):
    """Run a shell command, optionally raising if it fails."""
    result = subprocess.run(cmd, cwd=cwd)
    if check and result.returncode not in (0, 1):
        # pkill returns 1 when nothing matches, which is fine for our use case.
        raise click.ClickException(
            f"Command {' '.join(cmd)} failed with exit code {result.returncode}"
        )
    return result.returncode


@click.command()
@click.option("--port", default=8000, show_default=True, help="Port for uvicorn.")
@click.option(
    "--reload/--no-reload",
    default=False,
    show_default=True,
    help="Run uvicorn with hot reload (mirrors `uvicorn --reload`).",
)
def main(port: int, reload: bool):
    """Kill existing uvicorn processes bound to the port and start a new server."""
    if not BACKEND_DIR.exists():
        raise click.ClickException(f"Backend directory not found at {BACKEND_DIR}")

    patterns = [
        f"uvicorn app:app --port {port}",
        f"uvicorn app:app --reload --port {port}",
    ]

    click.echo(f"Stopping uvicorn processes on port {port} (if any)...")
    killed_any = False
    for pattern in patterns:
        exit_code = _run_command(["pkill", "-f", pattern], check=False)
        if exit_code == 0:
            killed_any = True
            click.echo(f"  • Terminated processes matching '{pattern}'")

    if not killed_any:
        click.echo("  • No matching uvicorn processes were running.")

    click.echo("Starting uvicorn via uv...")
    start_cmd = ["uv", "run", "uvicorn", "app:app", "--port", str(port)]
    if reload:
        start_cmd.insert(4, "--reload")

    click.echo(" ".join(start_cmd))
    try:
        subprocess.run(start_cmd, cwd=BACKEND_DIR, check=True)
    except subprocess.CalledProcessError as exc:
        raise click.ClickException(f"Failed to start uvicorn: {exc}") from exc


if __name__ == "__main__":
    main()
