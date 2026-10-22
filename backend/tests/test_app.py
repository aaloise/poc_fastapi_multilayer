"""
Tests — Async test suite for the POC.
Run with: pytest tests/ -v --asyncio-mode=auto
"""

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain import Priority, Task, TaskStatus


class TestTaskEntity:
    """Tests for the Task domain entity."""

    def test_create_task(self):
        task = Task(name="test_task", payload={"key": "value"})
        assert task.name == "test_task"
        assert task.status == TaskStatus.PENDING
        assert task.priority == Priority.MEDIUM
        assert task.attempts == 0
        assert task.id is not None

    def test_mark_running(self):
        task = Task(name="test")
        task.mark_running()
        assert task.status == TaskStatus.RUNNING
        assert task.attempts == 1
        assert task.started_at is not None

    def test_mark_completed(self):
        task = Task(name="test")
        task.mark_completed()
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
        assert task.is_terminal is True

    def test_mark_failed(self):
        task = Task(name="test")
        task.mark_failed("Something went wrong")
        assert task.status == TaskStatus.FAILED
        assert task.error == "Something went wrong"
        assert task.is_terminal is True

    def test_is_terminal(self):
        task = Task(name="test")
        assert task.is_terminal is False

        task.status = TaskStatus.COMPLETED
        assert task.is_terminal is True

        task.status = TaskStatus.CANCELLED
        assert task.is_terminal is True

        task.status = TaskStatus.RUNNING
        assert task.is_terminal is False


class TestTaskService:
    """Tests for the TaskService application layer."""

    @pytest.fixture
    def mock_repo(self):
        repo = AsyncMock()
        repo.save = AsyncMock(side_effect=lambda t: t)
        repo.get_by_id = AsyncMock(return_value=None)
        repo.list_all = AsyncMock(return_value=[])
        repo.list_by_status = AsyncMock(return_value=[])
        repo.count = AsyncMock(return_value=0)
        return repo

    @pytest.fixture
    def mock_queue(self):
        queue = AsyncMock()
        queue.enqueue = AsyncMock(return_value="task-id")
        return queue

    @pytest.mark.asyncio
    async def test_create_task(self, mock_repo, mock_queue):
        from app.application import TaskService

        service = TaskService(repository=mock_repo, queue_manager=mock_queue)
        task = await service.create_task(name="test", payload={"data": 123})

        assert task.name == "test"
        assert task.payload == {"data": 123}
        mock_repo.save.assert_called_once()
        mock_queue.enqueue.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_stats(self, mock_repo, mock_queue):
        from app.application import TaskService

        mock_repo.count = AsyncMock(return_value=10)
        mock_repo.list_by_status = AsyncMock(return_value=[])

        service = TaskService(repository=mock_repo, queue_manager=mock_queue)
        stats = await service.get_stats()

        assert stats["total"] == 10
        assert "pending" in stats
        assert "running" in stats
        assert "completed" in stats
        assert "failed" in stats


class TestConfig:
    """Tests for application configuration."""

    def test_default_settings(self):
        from app.config import Settings

        settings = Settings()
        assert settings.app_name == "Async POC"
        assert settings.port == 8000
        assert settings.workers == 4
        assert settings.queue_concurrency == 8

    def test_settings_override(self, monkeypatch):
        from app.config import Settings

        monkeypatch.setenv("POC_PORT", "9000")
        monkeypatch.setenv("POC_DEBUG", "true")

        settings = Settings()
        assert settings.port == 9000
        assert settings.debug is True
