"""
Storage Module
Handles database operations and data persistence.
Implements INV-NF-002 (Persistent storage with SQLite).
Uses parameterized queries to prevent SQL injection.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from .config import DB_PATH


class StorageManager:
    """Manages database operations with SQLite."""

    def __init__(self, db_path: str = None):
        """
        Initialize storage manager.

        Args:
            db_path: Path to SQLite database file (optional, uses config default)
        """
        self.db_path = db_path or DB_PATH
        self._ensure_database_exists()
        self._initialize_tables()
        self._seed_admin_user()

    def _ensure_database_exists(self):
        """Ensure database directory and file exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def get_connection(self):
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_tables(self):
        """Create all required tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table (PRJ-SEC-001)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Products table (INV-F-001)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT,
                stock INTEGER NOT NULL DEFAULT 0,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Suppliers table (INV-F-020)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Sales orders table (INV-F-010)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                total_price REAL NOT NULL,
                order_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')

        # Purchase orders table (INV-F-012)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                supplier_id INTEGER,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                order_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
            )
        ''')

        # Logs table (PRJ-SEC-003)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                action TEXT NOT NULL,
                details TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def _seed_admin_user(self):
        """Seed initial admin user if no users exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as count FROM users')
        count = cursor.fetchone()['count']

        if count == 0:
            # Import here to avoid circular dependency
            import hashlib

            # Create default admin: username=admin, password=admin123
            # Use the same salt as AuthManager to ensure password verification works
            password = "admin123"
            salt = "ims_secure_salt_2025"  # Must match AuthManager.SALT
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()

            cursor.execute('''
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            ''', ('admin', password_hash, 'admin'))

            conn.commit()

        conn.close()

    # ========== Generic CRUD Operations ==========

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """
        Execute SELECT query and return results as list of dicts.

        Args:
            query: SQL query with ? placeholders
            params: Tuple of parameters for query

        Returns:
            List of dictionaries representing rows
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute INSERT/UPDATE/DELETE query.

        Args:
            query: SQL query with ? placeholders
            params: Tuple of parameters for query

        Returns:
            Last row ID for INSERT, or rows affected
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    # ========== Product Operations ==========

    def add_product(self, sku: str, name: str, price: float,
                   category: str, stock: int, description: str = "") -> int:
        """Add new product (INV-F-001)."""
        query = '''
            INSERT INTO products (sku, name, price, category, stock, description)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        return self.execute_update(query, (sku, name, price, category, stock, description))

    def get_all_products(self) -> List[Dict]:
        """Get all products (INV-F-002)."""
        query = 'SELECT * FROM products ORDER BY name'
        return self.execute_query(query)

    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get product by ID."""
        query = 'SELECT * FROM products WHERE id = ?'
        results = self.execute_query(query, (product_id,))
        return results[0] if results else None

    def get_product_by_sku(self, sku: str) -> Optional[Dict]:
        """Get product by SKU."""
        query = 'SELECT * FROM products WHERE sku = ?'
        results = self.execute_query(query, (sku,))
        return results[0] if results else None

    def search_products(self, search_term: str) -> List[Dict]:
        """Search products by name or SKU (INV-F-002)."""
        query = '''
            SELECT * FROM products
            WHERE name LIKE ? OR sku LIKE ? OR category LIKE ?
            ORDER BY name
        '''
        pattern = f'%{search_term}%'
        return self.execute_query(query, (pattern, pattern, pattern))

    # ========== Logging Operations ==========

    def add_log(self, user: str, action: str, details: str = "") -> int:
        """Add log entry (PRJ-SEC-003)."""
        query = '''
            INSERT INTO logs (user, timestamp, action, details)
            VALUES (?, ?, ?, ?)
        '''
        timestamp = datetime.now().isoformat()
        return self.execute_update(query, (user, timestamp, action, details))

    def get_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent log entries."""
        query = 'SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?'
        return self.execute_query(query, (limit,))
