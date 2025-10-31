"""
Unit tests for logger module.
Tests logging and audit trail functionality.
"""

import pytest
import tempfile
import os
from src.logger import LogManager
from src.storage import StorageManager


class TestLogger:
    """Test logger module."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix='.sqlite')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    @pytest.fixture
    def logger(self, temp_db):
        """Create logger with temporary database."""
        storage = StorageManager(temp_db)
        return LogManager(storage)

    def test_logger_init(self, logger):
        """Test LogManager initialization."""
        assert logger.storage is not None

    def test_log_action(self, logger):
        """Test logging an action."""
        logger.log_action("testuser", "TEST_ACTION", "Test details")
        
        logs = logger.get_recent_logs(limit=1)
        assert len(logs) == 1
        assert logs[0]['user'] == "testuser"
        assert logs[0]['action'] == "TEST_ACTION"
        assert logs[0]['details'] == "Test details"

    def test_get_recent_logs(self, logger):
        """Test retrieving recent logs."""
        logger.log_action("user1", "ACTION1", "Details 1")
        logger.log_action("user2", "ACTION2", "Details 2")
        logger.log_action("user3", "ACTION3", "Details 3")
        
        logs = logger.get_recent_logs(limit=2)
        assert len(logs) == 2

    def test_get_logs_by_user(self, logger):
        """Test filtering logs by user."""
        logger.log_action("alice", "LOGIN", "Logged in")
        logger.log_action("bob", "LOGOUT", "Logged out")
        logger.log_action("alice", "ADD_PRODUCT", "Added product")
        
        alice_logs = logger.get_logs_by_user("alice")
        assert len(alice_logs) == 2
        assert all(log['user'] == "alice" for log in alice_logs)

    def test_get_logs_by_action(self, logger):
        """Test filtering logs by action."""
        logger.log_action("user1", "ADD_PRODUCT", "Added SKU001")
        logger.log_action("user2", "DELETE_PRODUCT", "Deleted SKU002")
        logger.log_action("user3", "ADD_PRODUCT", "Added SKU003")
        
        add_logs = logger.get_logs_by_action("ADD_PRODUCT")
        assert len(add_logs) == 2

    def test_format_log_entry(self, logger):
        """Test log entry formatting."""
        log = {
            'timestamp': '2025-10-31 12:00:00',
            'user': 'testuser',
            'action': 'TEST_ACTION',
            'details': 'Test details'
        }
        
        formatted = logger.format_log_entry(log)
        assert '2025-10-31 12:00:00' in formatted
        assert 'testuser' in formatted
        assert 'TEST_ACTION' in formatted
        assert 'Test details' in formatted

    def test_format_log_entry_without_details(self, logger):
        """Test log entry formatting without details."""
        log = {
            'timestamp': '2025-10-31 12:00:00',
            'user': 'testuser',
            'action': 'TEST_ACTION',
            'details': ''
        }
        
        formatted = logger.format_log_entry(log)
        assert '2025-10-31 12:00:00' in formatted
        assert 'testuser' in formatted
        assert 'TEST_ACTION' in formatted

    def test_display_logs_empty(self, logger, capsys):
        """Test displaying empty logs."""
        logger.display_logs([])
        captured = capsys.readouterr()
        assert "No logs found" in captured.out

    def test_display_logs_with_entries(self, logger, capsys):
        """Test displaying logs with entries."""
        logger.log_action("user1", "ACTION1", "Details 1")
        logs = logger.get_recent_logs(limit=5)
        
        logger.display_logs(logs)
        captured = capsys.readouterr()
        assert "AUDIT LOGS" in captured.out
        assert "user1" in captured.out
        assert "ACTION1" in captured.out
