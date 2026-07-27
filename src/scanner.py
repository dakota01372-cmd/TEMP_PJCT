"""
Scanner module for TigerMemory.

Recursively scans directories and indexes files with metadata extraction.

Key functions:
- scan_directory(path) — Recursively scan and index files
- get_file_type(extension) — Determine file category
- extract_metadata(path) — Extract file metadata
"""

from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import os

# Import config and database
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.config import FILE_TYPES, SKIP_FOLDERS, SKIP_PATTERNS, MAX_FILESIZE_BYTES
from src import database


def get_file_type(extension: str) -> str:
    """
    Determine file category from extension.
    
    Args:
        extension: File extension (e.g., '.pdf')
    
    Returns:
        File type category, or 'other' if unknown
    """
    return FILE_TYPES.get(extension.lower(), "other")


def should_skip(path: Path) -> bool:
    """
    Check if path should be skipped during scanning.
    
    Args:
        path: File or directory path
    
    Returns:
        True if path should be skipped
    """
    name = path.name.lower()
    
    # Check folder names
    if path.is_dir() and name in SKIP_FOLDERS:
        return True
    
    # Check file patterns
    for pattern in SKIP_PATTERNS:
        pattern_lower = pattern.lower()
        if pattern.startswith("*"):
            if name.endswith(pattern_lower[1:]):
                return True
        elif name.startswith("~"):
            return True
        elif name == pattern_lower:
            return True
    
    return False


def extract_metadata(path: Path) -> Optional[Dict]:
    """
    Extract metadata from a file.
    
    Args:
        path: Path to file
    
    Returns:
        Dict with metadata, or None if unable to read
    """
    try:
        stat = path.stat()
        
        return {
            "path": str(path),
            "filename": path.name,
            "extension": path.suffix,
            "size": stat.st_size,
            "file_type": get_file_type(path.suffix),
            "modified_date": datetime.fromtimestamp(stat.st_mtime),
            "created_date": datetime.fromtimestamp(stat.st_ctime),
        }
    except (OSError, IOError) as e:
        print(f"[SCAN] Error reading {path}: {e}")
        return None


def scan_directory(start_path: str, max_depth: int = 10) -> Dict:
    """
    Recursively scan directory and index files.
    
    Args:
        start_path: Directory to scan
        max_depth: Maximum directory depth to scan (prevent infinite loops)
    
    Returns:
        Dict with scan results: {'scanned': N, 'indexed': N, 'errors': N}
    """
    start = Path(start_path)
    
    if not start.exists():
        print(f"[SCAN] Path does not exist: {start_path}")
        return {"scanned": 0, "indexed": 0, "errors": 0}
    
    if not start.is_dir():
        print(f"[SCAN] Path is not a directory: {start_path}")
        return {"scanned": 0, "indexed": 0, "errors": 0}
    
    # Initialize database
    database.init()
    
    results = {"scanned": 0, "indexed": 0, "errors": 0}
    
    print(f"[SCAN] Starting scan of: {start}")
    print(f"[SCAN] Database: {database._db.db_path}")
    print()
    
    # Use iterdir to walk the tree
    def walk(path: Path, depth: int = 0):
        if depth > max_depth:
            return
        
        try:
            for item in path.iterdir():
                # Check if we should skip
                if should_skip(item):
                    print(f"[SCAN] Skipping: {item}")
                    continue
                
                # Process directories recursively
                if item.is_dir():
                    walk(item, depth + 1)
                    continue
                
                # Process files
                results["scanned"] += 1
                
                # Skip very large files
                if item.stat().st_size > MAX_FILESIZE_BYTES:
                    print(f"[SCAN] Skipping (too large): {item.name}")
                    continue
                
                # Extract and store metadata
                metadata = extract_metadata(item)
                if metadata:
                    file_id = database.add_file(
                        path=metadata["path"],
                        filename=metadata["filename"],
                        extension=metadata["extension"],
                        size=metadata["size"],
                        file_type=metadata["file_type"],
                        modified_date=metadata["modified_date"],
                        created_date=metadata["created_date"],
                    )
                    
                    if file_id > 0:
                        results["indexed"] += 1
                        if results["scanned"] % 100 == 0:
                            print(f"[SCAN] Processed {results['scanned']} files...")
                    else:
                        results["errors"] += 1
                else:
                    results["errors"] += 1
        
        except PermissionError as e:
            print(f"[SCAN] Permission denied: {path}")
            results["errors"] += 1
        except Exception as e:
            print(f"[SCAN] Error scanning {path}: {e}")
            results["errors"] += 1
    
    # Start recursive walk
    walk(start)
    
    print()
    print(f"[SCAN] Scan complete!")
    print(f"[SCAN] Files scanned: {results['scanned']}")
    print(f"[SCAN] Files indexed: {results['indexed']}")
    print(f"[SCAN] Errors: {results['errors']}")
    
    return results


# Command-line usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        scan_directory(path)
    else:
        print("Usage: python scanner.py <directory_path>")
