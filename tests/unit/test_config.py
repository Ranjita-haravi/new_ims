"""
Unit tests for config module.
Tests configuration management functionality.
"""

import pytest
import os
from src.config import ConfigManager, DB_PATH, BACKUP_PATH, REPORTS_PATH, LOW_STOCK_THRESHOLD


class TestConfig:
    """Test configuration module."""

    def test_config_constants(self):
        """Test that configuration constants are defined."""
        assert DB_PATH is not None
        assert BACKUP_PATH is not None
        assert REPORTS_PATH is not None
        assert LOW_STOCK_THRESHOLD == 5

    def test_config_manager_init(self):
        """Test ConfigManager initialization."""
        config = ConfigManager()
        
        assert config.db_path is not None
        assert config.backup_path is not None
        assert config.reports_path is not None
        assert config.low_stock_threshold == 5
        assert config.encryption_key is not None

    def test_config_manager_get_config(self):
        """Test getting configuration values."""
        config = ConfigManager()
        
        assert config.get_config('db_path') == config.db_path
        assert config.get_config('backup_path') == config.backup_path
        assert config.get_config('reports_path') == config.reports_path
        assert config.get_config('low_stock_threshold') == 5
        assert config.get_config('encryption_key') is not None
        assert config.get_config('nonexistent') is None
