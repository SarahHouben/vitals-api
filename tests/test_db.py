"""Test where the database file lives."""

from pathlib import Path

from vitals_api.db import database_path, engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_database_path_defaults_to_project_folder(monkeypatch):
    monkeypatch.delenv("VITALS_DB_PATH", raising=False)
    assert database_path() == PROJECT_ROOT / "vitals.db"


def test_database_path_uses_environment_variable(monkeypatch, tmp_path):
    custom_path = tmp_path / "test.db"
    monkeypatch.setenv("VITALS_DB_PATH", str(custom_path))
    assert database_path() == custom_path


def test_engine_uses_database_path():
    assert engine.url.database == str(database_path())
