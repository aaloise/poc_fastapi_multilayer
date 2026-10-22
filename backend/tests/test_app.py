"""Testes — suite async."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.models import Task, TaskStatus, Priority


class TestTaskModel:
    """Testes do modelo Task."""

    def test_create(self):
        task = Task(name="test", payload={"key": "value"})
        assert task.name == "test"
        assert task.status == TaskStatus.PENDING
        assert task.priority == Priority.MEDIUM

    def test_status_values(self):
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.RUNNING == "running"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.FAILED == "failed"


class TestConfig:
    """Testes de configuração."""

    def test_defaults(self):
        from app.config import Settings
        s = Settings()
        assert s.port == 8000
        assert s.queue_concurrency == 8

    def test_override(self, monkeypatch):
        from app.config import Settings
        monkeypatch.setenv("POC_PORT", "9000")
        s = Settings()
        assert s.port == 9000
