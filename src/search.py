"""
Search module for TigerMemory.

Provides searching, filtering, and sorting over indexed files.

Key functions:
- search(query) — Find files by name
- filter_by_type(file_type) — Get all files of a type
- filter_by_size(min_bytes, max_bytes) — Find files by size
- recent_files(days) — Find recently modified files
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Import database
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src import database


def search(query: str, limit: int = 100) -> List[Dict]:
    """
    Search for files by filename.
    
    Args:
        query: Search term (matches filename)
        limit: Max results to return
    
    Returns:
        List of matching files
    """
    if not query:
        return []
    
    results = database.search(query, limit=limit)
    print(f"[SEARCH] Found {len(results)} results for: '{query}'")
    return results


def filter_by_type(file_type: str, limit: int = 100) -> List[Dict]:
    """
    Get all files of a specific type.
    
    Args:
        file_type: File category (e.g., 'image', 'document', 'code')
        limit: Max results
    
    Returns:
        List of matching files
    """
    results = database.search("", file_type=file_type, limit=limit)
    print(f"[SEARCH] Found {len(results)} files of type: '{file_type}'")
    return results


def filter_by_extension(extension: str, limit: int = 100) -> List[Dict]:
    """
    Get all files with a specific extension.
    
    Args:
        extension: File extension (e.g., '.pdf', '.jpg')
        limit: Max results
    
    Returns:
        List of matching files
    """
    results = database.search("", extension=extension, limit=limit)
    print(f"[SEARCH] Found {len(results)} files with extension: '{extension}'")
    return results


def filter_by_size(
    min_bytes: int = 0,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB default
    limit: int = 100
) -> List[Dict]:
    """
    Find files within a size range.
    
    Args:
        min_bytes: Minimum file size
        max_bytes: Maximum file size
        limit: Max results
    
    Returns:
        List of matching files
    """
    results = database._db.search_files("", limit=limit)
    filtered = [f for f in results if min_bytes <= f["size"] <= max_bytes]
    
    size_mb_min = min_bytes / (1024 * 1024)
    size_mb_max = max_bytes / (1024 * 1024)
    print(f"[SEARCH] Found {len(filtered)} files between {size_mb_min:.1f} - {size_mb_max:.1f} MB")
    
    return filtered


def recent_files(days: int = 7, limit: int = 100) -> List[Dict]:
    """
    Find files modified within the last N days.
    
    Args:
        days: Number of days to look back
        limit: Max results
    
    Returns:
        List of recently modified files
    """
    results = database._db.search_files("", limit=limit)
    
    cutoff = datetime.now() - timedelta(days=days)
    filtered = []
    
    for f in results:
        if f["modified_date"]:
            mod_date = datetime.fromisoformat(f["modified_date"])
            if mod_date > cutoff:
                filtered.append(f)
    
    print(f"[SEARCH] Found {len(filtered)} files modified in last {days} days")
    return filtered


def format_result(file_record: Dict) -> str:
    """
    Format a file record for display.
    
    Args:
        file_record: File record from database
    
    Returns:
        Formatted string
    """
    size_mb = file_record["size"] / (1024 * 1024) if file_record["size"] else 0
    path = file_record["path"]
    file_type = file_record.get("file_type", "unknown")
    
    return f"{file_record['filename']:<40} | {size_mb:>8.2f} MB | {file_type:<10} | {path}"


def print_results(results: List[Dict], max_display: int = 20):
    """
    Pretty-print search results.
    
    Args:
        results: List of file records
        max_display: Max rows to display
    """
    if not results:
        print("No results found.")
        return
    
    print()
    print("=" * 120)
    print(f"{'Filename':<40} | {'Size (MB)':>10} | {'Type':<10} | {'Path'}")
    print("=" * 120)
    
    for i, result in enumerate(results[:max_display]):
        print(format_result(result))
    
    if len(results) > max_display:
        print(f"... and {len(results) - max_display} more results")
    
    print("=" * 120)
    print()
