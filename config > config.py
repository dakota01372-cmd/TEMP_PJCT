>
# __init__.py EMPTY #
# config.py

#config.pu
# """
Configuration and constants for TigerMemory.

Define paths, database settings, file type mappings, and other project-wide constants.
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Database configuration
DATABASE_PATH = DATA_DIR / "tigermemory.db"
DATABASE_TIMEOUT = 30  # seconds

# File type mappings
# Extension -> Category
FILE_TYPES = {
    # Documents
    ".pdf": "document",
    ".docx": "document",
    ".doc": "document",
    ".txt": "document",
    ".md": "document",
    ".rtf": "document",
    
    # Spreadsheets
    ".xlsx": "spreadsheet",
    ".xls": "spreadsheet",
    ".csv": "spreadsheet",
    
    # Presentations
    ".pptx": "presentation",
    ".ppt": "presentation",
    
    # Code
    ".py": "code",
    ".js": "code",
    ".java": "code",
    ".cpp": "code",
    ".c": "code",
    ".go": "code",
    ".rs": "code",
    ".sql": "code",
    ".html": "code",
    ".css": "code",
    ".json": "code",
    ".yaml": "code",
    ".yml": "code",
    ".xml": "code",
    
    # Images
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".gif": "image",
    ".bmp": "image",
    ".svg": "image",
    ".webp": "image",
    
    # Audio
    ".mp3": "audio",
    ".wav": "audio",
    ".flac": "audio",
    ".m4a": "audio",
    ".aac": "audio",
    
    # Video
    ".mp4": "video",
    ".avi": "video",
    ".mkv": "video",
    ".mov": "video",
    ".flv": "video",
    ".webm": "video",
    
    # Archives
    ".zip": "archive",
    ".rar": "archive",
    ".7z": "archive",
    ".tar": "archive",
    ".gz": "archive",
}

# Folders to skip during scanning (case-insensitive)
SKIP_FOLDERS = {
    ".git",
    ".github",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".env",
    "env",
    ".idea",
    ".vscode",
    "dist",
    "build",
    ".pytest_cache",
    "*.egg-info",
    "$RECYCLE.BIN",
    "System Volume Information",
    "Thumbs.db",
}

# File patterns to skip (case-insensitive)
SKIP_PATTERNS = {
    ".DS_Store",
    "Thumbs.db",
    "*.tmp",
    "*.temp",
    "*.swp",
    "*.swo",
    "~*",
}

# Logging configuration
LOG_LEVEL = os.getenv("TIGERMEMORY_LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Search configuration
MAX_SEARCH_RESULTS = 100
SEARCH_LIMIT_DEFAULT = 10

# Scanner configuration
BATCH_INSERT_SIZE = 100  # Insert metadata in batches for performance
MAX_FILESIZE_BYTES = 10 * 1024 * 1024 * 1024  # 10 GB limit per file

print(f"[CONFIG] Project root: {PROJECT_ROOT}")
print(f"[CONFIG] Database: {DATABASE_PATH}")

