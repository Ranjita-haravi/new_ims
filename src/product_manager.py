"""
Product Manager Module
Manages product inventory operations (CRUD).
Implements INV-F-001, INV-F-002, INV-F-003, INV-F-032.
"""

from typing import List, Dict, Optional
from .storage import StorageManager
from .logger import LogManager
from .config import LOW_STOCK_THRESHOLD


class ProductManager:
    """Manages product inventory."""

    def __init__(self, storage: StorageManager = None, logger: LogManager = None):
        """
        Initialize product manager.

        Args:
            storage: StorageManager instance (optional)
            logger: LogManager instance (optional)
        """
        self.storage = storage or StorageManager()
        self.logger = logger or LogManager(self.storage)

    def add_product(self, sku: str, name: str, price: float, category: str,
                   stock: int, description: str = "", user: str = "system") -> Optional[int]:
        """
        Add new product to inventory (INV-F-001).

        Args:
            sku: Unique product SKU
            name: Product name
            price: Product price
            category: Product category
            stock: Initial stock quantity
            description: Product description
            user: Username performing the action

        Returns:
            Product ID if successful, None if SKU already exists
        """
        # Check if SKU already exists
        existing = self.storage.get_product_by_sku(sku)
        if existing:
            return None

        # Validate inputs
        if price < 0:
            raise ValueError("Price cannot be negative")
        if stock < 0:
            raise ValueError("Stock cannot be negative")

        # Add product
        product_id = self.storage.add_product(sku, name, price, category, stock, description)

        # Log action
        self.logger.log_action(
            user,
            "ADD_PRODUCT",
            f"Added product: {name} (SKU: {sku})"
        )

        return product_id

    def get_all_products(self) -> List[Dict]:
        """
        Get all products (INV-F-002).

        Returns:
            List of product dictionaries
        """
        return self.storage.get_all_products()

    def get_product(self, product_id: int) -> Optional[Dict]:
        """
        Get product by ID.

        Args:
            product_id: Product ID

        Returns:
            Product dictionary or None if not found
        """
        return self.storage.get_product_by_id(product_id)

    def search_products(self, search_term: str) -> List[Dict]:
        """
        Search products by name, SKU, or category (INV-F-002).

        Args:
            search_term: Search string

        Returns:
            List of matching product dictionaries
        """
        return self.storage.search_products(search_term)
