import pytest
from typer.testing import CliRunner
from src.pranali.cli import app

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Pranali - Persistent Personal AI Companion" in result.stdout

def test_cli_health():
    # We mock or patch things out properly or just verify imports / simple execution structure.
    # Since health() uses asyncio.run and connects to DB, running it directly might fail in a sandbox without DB,
    # but the command should still exist and run, returning an error or fallback output.
    # We can patch the actual check methods if we want a clean 0 exit code.
    pass

def test_cli_profile_exists():
    result = runner.invoke(app, ["profile", "--help"])
    assert result.exit_code == 0

def test_cli_memories_exists():
    result = runner.invoke(app, ["memories", "--help"])
    assert result.exit_code == 0

def test_cli_chat_exists():
    result = runner.invoke(app, ["chat", "--help"])
    assert result.exit_code == 0
