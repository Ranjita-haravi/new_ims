"""
Unit tests for storage module.
Tests database operations and data persistence.
"""

import pytest
import tempfile
import os
from src.storage import StorageManager


class TestStorage:
    """Test storage module."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        fd, path = tempfile.mkstemp(suffix='.sqlite')
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    @pytest.fixture
    def storage(self, temp_db):
        """Create storage with temporary database."""
        return StorageManager(temp_db)

    def test_storage_init(self, storage):
        """Test StorageManager initialization."""
        assert storage.db_path is not None
        assert os.path.exists(storage.db_path)

    def test_get_connection(self, storage):
        """Test getting database connection."""
        conn = storage.get_connection()
        assert conn is not None
        conn.close()

    def test_add_product(self, storage):
        """Test adding a product."""
        product_id = storage.add_product(
            sku="TEST001",
            name="Test Product",
            price=99.99,
            category="Test",
            stock=10,
            description="Test description"
        )
        
        assert product_id > 0

    def test_get_all_products(self, storage):
        """Test getting all products."""
        storage.add_product("PROD001", "Product 1", 10.0, "Cat1", 5)
        storage.add_product("PROD002", "Product 2", 20.0, "Cat2", 10)
        
        products = storage.get_all_products()
        assert len(products) >= 2

    def test_get_product_by_id(self, storage):
        """Test getting product by ID."""
        product_id = storage.add_product("TEST001", "Test", 10.0, "Cat", 5)
        
        product = storage.get_product_by_id(product_id)
        assert product is not None
        assert product['sku'] == "TEST001"

    def test_get_product_by_id_not_found(self, storage):
        """Test getting non-existent product by ID."""
        product = storage.get_product_by_id(99999)
        assert product is None

    def test_get_product_by_sku(self, storage):
        """Test getting product by SKU."""
        storage.add_product("SKU001", "Test", 10.0, "Cat", 5)
        
        product = storage.get_product_by_sku("SKU001")
        assert product is not None
        assert product['name'] == "Test"

    def test_get_product_by_sku_not_found(self, storage):
        """Test getting non-existent product by SKU."""
        product = storage.get_product_by_sku("NONEXISTENT")
        assert product is None

    def test_search_products_by_name(self, storage):
        """Test searching products by name."""
        storage.add_product("SKU001", "Gaming Laptop", 1000.0, "Electronics", 5)
        storage.add_product("SKU002", "Office Laptop", 800.0, "Electronics", 10)
        storage.add_product("SKU003", "Office Chair", 200.0, "Furniture", 15)
        
        results = storage.search_products("Laptop")
        assert len(results) == 2

    def test_search_products_by_sku(self, storage):
        """Test searching products by SKU."""
        storage.add_product("LAP001", "Laptop", 1000.0, "Electronics", 5)
        
        results = storage.search_products("LAP")
        assert len(results) >= 1

    def test_search_products_by_category(self, storage):
        """Test searching products by category."""
        storage.add_product("SKU001", "Product 1", 100.0, "Electronics", 5)
        storage.add_product("SKU002", "Product 2", 200.0, "Electronics", 10)
        
        results = storage.search_products("Electronics")
        assert len(results) == 2

    def test_execute_query(self, storage):
        """Test executing SELECT query."""
        storage.add_product("TEST001", "Test", 10.0, "Cat", 5)
        
        results = storage.execute_query("SELECT * FROM products WHERE sku = ?", ("TEST001",))
        assert len(results) == 1
        assert results[0]['sku'] == "TEST001"

    def test_execute_update(self, storage):
        """Test executing UPDATE query."""
        product_id = storage.add_product("TEST001", "Test", 10.0, "Cat", 5)
        
        storage.execute_update("UPDATE products SET stock = ? WHERE id = ?", (20, product_id))
        
        product = storage.get_product_by_id(product_id)
        assert product['stock'] == 20

    def test_add_log(self, storage):
        """Test adding log entry."""
        log_id = storage.add_log("testuser", "TEST_ACTION", "Test details")
        assert log_id > 0

    def test_get_logs(self, storage):
        """Test getting logs."""
        storage.add_log("user1", "ACTION1", "Details 1")
        storage.add_log("user2", "ACTION2", "Details 2")
        
        logs = storage.get_logs(limit=10)
        assert len(logs) >= 2

    def test_seed_admin_user(self, storage):
        """Test that admin user is seeded."""
        # Admin user should be created automatically
        results = storage.execute_query("SELECT * FROM users WHERE username = ?", ("admin",))
        assert len(results) == 1
        assert results[0]['role'] == "admin"
