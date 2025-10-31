"""
Unit tests for product_manager module.
Tests INV-F-001 (Add product with details).
"""

import pytest
import tempfile
import os
from src.product_manager import ProductManager
from src.storage import StorageManager
from src.logger import LogManager


class TestProductManager:
    """Test product manager - Add product functionality."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix='.sqlite')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    @pytest.fixture
    def product_manager(self, temp_db):
        """Create product manager with temporary database."""
        storage = StorageManager(temp_db)
        logger = LogManager(storage)
        return ProductManager(storage, logger)

    def test_add_product_success(self, product_manager):
        """Test adding product successfully (INV-F-001)."""
        product_id = product_manager.add_product(
            sku="LAPTOP001",
            name="Gaming Laptop",
            price=1299.99,
            category="Electronics",
            stock=15,
            description="High-performance gaming laptop"
        )
        
        assert product_id is not None
        assert product_id > 0

    def test_add_product_duplicate_sku(self, product_manager):
        """Test adding product with duplicate SKU fails."""
        product_manager.add_product("LAPTOP001", "Laptop 1", 999.99, "Electronics", 10)
        
        # Try to add with same SKU
        result = product_manager.add_product("LAPTOP001", "Laptop 2", 899.99, "Electronics", 5)
        
        assert result is None

    def test_add_product_negative_price(self, product_manager):
        """Test adding product with negative price raises error."""
        with pytest.raises(ValueError):
            product_manager.add_product("TEST001", "Test", -10.00, "Cat", 10)

    def test_add_product_negative_stock(self, product_manager):
        """Test adding product with negative stock raises error."""
        with pytest.raises(ValueError):
            product_manager.add_product("TEST001", "Test", 10.00, "Cat", -5)

    def test_get_all_products(self, product_manager):
        """Test getting all products (INV-F-002)."""
        product_manager.add_product("PROD001", "Product 1", 10.00, "Cat1", 50)
        product_manager.add_product("PROD002", "Product 2", 20.00, "Cat2", 30)
        
        products = product_manager.get_all_products()
        
        assert len(products) >= 2

    def test_get_product(self, product_manager):
        """Test getting single product by ID."""
        product_id = product_manager.add_product("PROD001", "Product 1", 10.00, "Cat1", 50)
        
        product = product_manager.get_product(product_id)
        
        assert product is not None
        assert product['sku'] == "PROD001"
        assert product['name'] == "Product 1"

    def test_search_products(self, product_manager):
        """Test searching products (INV-F-002)."""
        product_manager.add_product("LAPTOP001", "Gaming Laptop", 1299.99, "Electronics", 10)
        product_manager.add_product("LAPTOP002", "Business Laptop", 999.99, "Electronics", 15)
        product_manager.add_product("CHAIR001", "Office Chair", 199.99, "Furniture", 20)
        
        # Search by keyword
        results = product_manager.search_products("Laptop")
        assert len(results) == 2
        
        # Search by category
        results = product_manager.search_products("Electronics")
        assert len(results) == 2

    def test_add_product_logs_action(self, product_manager):
        """Test that adding product creates a log entry."""
        product_manager.add_product(
            sku="PROD001",
            name="Test Product",
            price=99.99,
            category="Test",
            stock=10,
            user="testuser"
        )
        
        logs = product_manager.logger.get_recent_logs(limit=5)
        
        # Check that at least one log entry exists
        assert len(logs) > 0
        
        # Check that the most recent log is for ADD_PRODUCT
        latest_log = logs[0]
        assert latest_log['action'] == "ADD_PRODUCT"
        assert latest_log['user'] == "testuser"
        assert "PROD001" in latest_log['details']

    def test_add_product_with_minimal_info(self, product_manager):
        """Test adding product with only required fields."""
        product_id = product_manager.add_product(
            sku="MIN001",
            name="Minimal Product",
            price=50.00,
            category="General",
            stock=5
        )
        
        assert product_id is not None
        
        product = product_manager.get_product(product_id)
        assert product['sku'] == "MIN001"
        assert product['name'] == "Minimal Product"
        assert product['price'] == 50.00
        assert product['stock'] == 5
