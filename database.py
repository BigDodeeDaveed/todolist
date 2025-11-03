import sqlite3
import os
from contextlib import contextmanager
from pathlib import Path

class Database:
    """Handles database connections and initialization."""

    def __init__(self, db_path=Path('YOUR OWN PATH HERE')):
        """
        Initialize the database connection.

        Args:
            db_path: Path to the SQLite database file (defaults to config setting)
        """
        # If db_path is None or empty, use a default path
        self.db_path = db_path
        if not self.db_path:
            # Set default path if DB_PATH is empty
            self.db_path = "tools.db"
        self._initialize_db()

    def _initialize_db(self):
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                complete INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            conn.commit()

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.

        Yields:
            sqlite3.Connection: Active database connection
        """
        # Check if db_path has a directory component
        db_dir = os.path.dirname(self.db_path)

        # Only try to create directories if there's a directory path
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        # Connect to the database
        conn = sqlite3.connect(self.db_path)

        # Configure connection
        conn.row_factory = sqlite3.Row  # Use dictionary-like rows

        try:
            yield conn
        finally:
            conn.close()

# Create a singleton instance
db = Database()


