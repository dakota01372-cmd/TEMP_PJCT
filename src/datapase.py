"""
Database module for TigerMemory.

Handles SQLite operations: schema creation, inserting files, querying, and cleanup.

Key functions:
- init_database() — Create schema if needed
- add_file(path, metadata) — Index a file
- search_files(query) — Search by filename or metadata
- get_stats() — Database statistics
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Import config
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.config import DATABASE_PATH, DATABASE_TIMEOUT

class TigerMemoryDB:
    """SQLite database interface for TigerMemory."""
    
    def __init__(self, db_path: Path = DATABASE_PATH):
        """Initialize database connection."""
        self.db_path = db_path
        self.timeout = DATABASE_TIMEOUT
    
    def connect(self) -> sqlite3.Connection:
        """Create a database connection."""
        conn = sqlite3.connect(self.db_path, timeout=self.timeout)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn
    
    def init_schema(self) -> bool:
        """
        Create database schema if it doesn't exist.
        
        Tables:
        - files: Core file metadata
        - metadata: Key-value pairs for extensibility
        - search_cache: Denormalized search index (future optimization)
        
        Returns:
            True if schema created, False if already exists
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # Check if files table already exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='files'"
            )
            if cursor.fetchone():
                print("[DB] Schema already initialized.")
                return False
            
            # Create files table
            cursor.execute("""
                CREATE TABLE files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    filename TEXT NOT NULL,
                    extension TEXT,
                    size INTEGER,
                    file_type TEXT,
                    modified_date TIMESTAMP,
                    created_date TIMESTAMP,
                    indexed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT path_unique UNIQUE(path)
                )
            """)
            
            # Create metadata table for flexible key-value storage
            cursor.execute("""
                CREATE TABLE metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
                )
            """)
            
            # Create indices for fast queries
            cursor.execute("CREATE INDEX idx_filename ON files(filename)")
            cursor.execute("CREATE INDEX idx_extension ON files(extension)")
            cursor.execute("CREATE INDEX idx_file_type ON files(file_type)")
            cursor.execute("CREATE INDEX idx_path ON files(path)")
            cursor.execute("CREATE INDEX idx_metadata_file_id ON metadata(file_id)")
            
            conn.commit()
            print(f"[DB] Schema initialized: {self.db_path}")
            return True
            
        except sqlite3.Error as e:
            print(f"[DB] Error creating schema: {e}")
            return False
        finally:
            conn.close()
    
    def add_file(
        self,
        path: str,
        filename: str,
        extension: str,
        size: int,
        file_type: str,
        modified_date: datetime,
        created_date: Optional[datetime] = None
    ) -> int:
        """
        Add or update a file record.
        
        Args:
            path: Full file path
            filename: Just the filename
            extension: File extension (e.g., '.pdf')
            size: File size in bytes
            file_type: Category (e.g., 'document', 'image')
            modified_date: Last modified timestamp
            created_date: Created timestamp (optional)
        
        Returns:
            File ID, or -1 on error
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO files
                (path, filename, extension, size, file_type, modified_date, created_date, indexed_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                path,
                filename,
                extension,
                size,
                file_type,
                modified_date.isoformat() if modified_date else None,
                created_date.isoformat() if created_date else None,
            ))
            
            conn.commit()
            return cursor.lastrowid
            
        except sqlite3.Error as e:
            print(f"[DB] Error adding file {path}: {e}")
            return -1
        finally:
            conn.close()
    
    def search_files(
        self,
        query: str,
        file_type: Optional[str] = None,
        extension: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Search files by filename and optional filters.
        
        Args:
            query: Search string (matches filename)
            file_type: Filter by file type (optional)
            extension: Filter by extension (optional)
            limit: Max results to return
        
        Returns:
            List of matching file records
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            sql = "SELECT * FROM files WHERE filename LIKE ?"
            params = [f"%{query}%"]
            
            if file_type:
                sql += " AND file_type = ?"
                params.append(file_type)
            
            if extension:
                sql += " AND extension = ?"
                params.append(extension)
            
            sql += " ORDER BY modified_date DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
            
        except sqlite3.Error as e:
            print(f"[DB] Error searching: {e}")
            return []
        finally:
            conn.close()
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM files")
            total_files = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(size) FROM files")
            total_size = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT file_type, COUNT(*) as count
                FROM files
                GROUP BY file_type
                ORDER BY count DESC
            """)
            by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "by_file_type": by_type,
                "database_path": str(self.db_path),
            }
            
        except sqlite3.Error as e:
            print(f"[DB] Error getting stats: {e}")
            return {}
        finally:
            conn.close()


# Module-level convenience functions
_db = TigerMemoryDB()

def init():
    """Initialize database schema."""
    return _db.init_schema()

def add_file(path, filename, extension, size, file_type, modified_date, created_date=None):
    """Add a file to the index."""
    return _db.add_file(path, filename, extension, size, file_type, modified_date, created_date)

def search(query, file_type=None, extension=None, limit=100):
    """Search indexed files."""
    return _db.search_files(query, file_type, extension, limit)

def stats():
    """Get database statistics."""
    return _db.get_stats()
