"""
Export module for TigerMemory.

Convert indexed data to various formats (JSON, CSV) for backup and external use.

Key functions:
- export_json(query) — Export search results as JSON
- export_all_json() — Export entire index as JSON
- export_csv(results) — Export as CSV format
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Import database and search
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src import database, search


def export_json(
    results: List[Dict],
    output_path: Optional[str] = None,
    pretty: bool = True
) -> str:
    """
    Export search results as JSON.
    
    Args:
        results: List of file records
        output_path: Where to save JSON (optional)
        pretty: Pretty-print JSON (True) or compact (False)
    
    Returns:
        JSON string
    """
    json_data = {
        "exported_at": datetime.now().isoformat(),
        "total_results": len(results),
        "files": results,
    }
    
    json_str = json.dumps(json_data, indent=2 if pretty else None, default=str)
    
    if output_path:
        Path(output_path).write_text(json_str, encoding="utf-8")
        print(f"[EXPORT] Saved to: {output_path}")
    
    return json_str


def export_all_json(output_path: Optional[str] = None) -> str:
    """
    Export entire index as JSON.
    
    Args:
        output_path: Where to save JSON
    
    Returns:
        JSON string
    """
    print("[EXPORT] Exporting all indexed files...")
    
    # Get all files (large limit)
    all_files = database._db.search_files("", limit=100000)
    
    stats = database.stats()
    
    json_data = {
        "exported_at": datetime.now().isoformat(),
        "statistics": stats,
        "files": all_files,
    }
    
    json_str = json.dumps(json_data, indent=2, default=str)
    
    if output_path:
        Path(output_path).write_text(json_str, encoding="utf-8")
        print(f"[EXPORT] Exported {len(all_files)} files to: {output_path}")
    
    return json_str


def export_csv(
    results: List[Dict],
    output_path: str
) -> int:
    """
    Export results as CSV.
    
    Args:
        results: List of file records
        output_path: Where to save CSV
    
    Returns:
        Number of rows written
    """
    if not results:
        print("[EXPORT] No results to export.")
        return 0
    
    # Define CSV columns
    fieldnames = [
        "filename",
        "path",
        "extension",
        "file_type",
        "size_bytes",
        "size_mb",
        "modified_date",
        "indexed_date",
    ]
    
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in results:
                row = {
                    "filename": record.get("filename", ""),
                    "path": record.get("path", ""),
                    "extension": record.get("extension", ""),
                    "file_type": record.get("file_type", ""),
                    "size_bytes": record.get("size", 0),
                    "size_mb": round(record.get("size", 0) / (1024 * 1024), 2),
                    "modified_date": record.get("modified_date", ""),
                    "indexed_date": record.get("indexed_date", ""),
                }
                writer.writerow(row)
        
        print(f"[EXPORT] Saved {len(results)} records to: {output_path}")
        return len(results)
    
    except IOError as e:
        print(f"[EXPORT] Error writing CSV: {e}")
        return 0
