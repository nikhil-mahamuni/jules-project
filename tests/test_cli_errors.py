import pytest
import os
from unittest.mock import patch
from typer.testing import CliRunner
from src.pranali.cli import app

runner = CliRunner()

@pytest.fixture
def mock_db_error():
    with patch("src.pranali.cli.get_session_factory", side_effect=Exception("Connection refused")):
        yield

def test_cli_health_no_crash(mock_db_error):
    result = runner.invoke(app, ["health"])
    assert result.exit_code == 0
    assert "Database OK: [red]No[/red]" in result.stdout
    assert "pgvector OK: [red]No[/red]" in result.stdout

def test_cli_chat_graceful_failure(mock_db_error):
    result = runner.invoke(app, ["chat"], input="/exit\n")
    assert result.exit_code == 0
    assert "Database unavailable: Connection refused" in result.stdout

def test_cli_voice_graceful_failure(mock_db_error):
    result = runner.invoke(app, ["voice"], input="/exit\n")
    assert result.exit_code == 0
    assert "Database unavailable: Connection refused" in result.stdout

def test_cli_reflect_graceful_failure(mock_db_error):
    result = runner.invoke(app, ["reflect"])
    assert result.exit_code == 0
    assert "Database unavailable: Connection refused" in result.stdout

def test_cli_memories_graceful_failure(mock_db_error):
    result = runner.invoke(app, ["memories"])
    assert result.exit_code == 0
    assert "Database unavailable: Connection refused" in result.stdout

def test_cli_profile_graceful_failure(mock_db_error):
    result = runner.invoke(app, ["profile"])
    assert result.exit_code == 0
    assert "Database unavailable: Connection refused" in result.stdout
