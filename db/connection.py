"""
DuckDB connection management with singleton pattern for Aqualog.
Provides centralized database connection handling with automatic initialization.
"""

import threading
from pathlib import Path
from typing import Optional

import duckdb
from loguru import logger


class DatabaseConnection:
    """Singleton class for managing DuckDB connection."""

    _instance: Optional["DatabaseConnection"] = None
    _lock = threading.Lock()

    def __new__(cls, db_path: str = "data/aqualog.duckdb") -> "DatabaseConnection":
        """Create or return existing singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str = "data/aqualog.duckdb") -> None:
        """Initialize the database connection if not already initialized."""
        if not getattr(self, "_initialized", False):
            self.db_path = Path(db_path)
            self._connection: duckdb.DuckDBPyConnection | None = None
            self._initialized = True
            logger.info(f"DatabaseConnection initialized with path: {self.db_path}")

    def connect(self) -> duckdb.DuckDBPyConnection:
        """Get or create database connection."""
        if self._connection is None:
            try:
                # Ensure the data directory exists
                self.db_path.parent.mkdir(parents=True, exist_ok=True)

                # Create connection to DuckDB file
                self._connection = duckdb.connect(str(self.db_path))
                logger.info(f"Connected to DuckDB at {self.db_path}")

                # Initialize database schema
                self._initialize_schema()

            except Exception as e:
                logger.error(f"Failed to connect to database: {e}")
                raise

        return self._connection

    def _initialize_schema(self) -> None:
        """Initialize database schema from SQL file."""
        try:
            schema_path = Path(__file__).parent / "schema.sql"
            if schema_path.exists():
                with open(schema_path) as f:
                    schema_sql = f.read()

                # Execute schema creation
                self._connection.execute(schema_sql)
                logger.info("Database schema initialized successfully")
            else:
                logger.warning(f"Schema file not found at {schema_path}")

        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise

    def execute_query(self, query: str, parameters: tuple | None = None):
        """Execute a query with optional parameters."""
        try:
            conn = self.connect()
            if parameters:
                result = conn.execute(query, parameters)
            else:
                result = conn.execute(query)
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {query[:100]}... Error: {e}")
            raise

    def fetch_all(self, query: str, parameters: tuple | None = None) -> list:
        """Execute query and fetch all results."""
        result = self.execute_query(query, parameters)
        return result.fetchall()

    def fetch_one(self, query: str, parameters: tuple | None = None) -> tuple | None:
        """Execute query and fetch one result."""
        result = self.execute_query(query, parameters)
        return result.fetchone()

    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    def get_database_size(self) -> float:
        """Get database file size in MB."""
        try:
            if self.db_path.exists():
                size_bytes = self.db_path.stat().st_size
                return size_bytes / (1024 * 1024)  # Convert to MB
            return 0.0
        except Exception as e:
            logger.error(f"Failed to get database size: {e}")
            return 0.0


# Global database instance
db = DatabaseConnection()


def get_db_connection() -> DatabaseConnection:
    """Get the global database connection instance."""
    return db
