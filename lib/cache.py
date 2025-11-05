"""Cache manager for VirusTotal scan results."""
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class CacheManager:
    """Manages caching of VirusTotal scan results."""
    
    def __init__(self, cache_file: str = None, cache_days: int = 7):
        """
        Initialize cache manager.
        
        Args:
            cache_file: Path to cache file
            cache_days: Number of days to keep cache entries
        """
        if cache_file is None:
            cache_file = os.path.join("data", "vt_cache.json")
        self.cache_file = cache_file
        self.cache_days = cache_days
        self.cache: Dict[str, Dict[str, Any]] = {}
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Load cache from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load cache file: {e}")
                self.cache = {}
        else:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            self.cache = {}
    
    def _save_cache(self) -> None:
        """Save cache to file."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save cache file: {e}")
    
    def get(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get cached result for a file hash.
        
        Args:
            file_hash: SHA-256 hash of the file
            
        Returns:
            Cached result or None if not found or expired
        """
        if file_hash not in self.cache:
            return None
        
        entry = self.cache[file_hash]
        
        # Check if cache entry has expired
        if 'timestamp' in entry:
            cached_time = datetime.fromisoformat(entry['timestamp'])
            if datetime.now() - cached_time > timedelta(days=self.cache_days):
                # Cache expired
                del self.cache[file_hash]
                self._save_cache()
                return None
        
        return entry
    
    def set(self, file_hash: str, file_path: str, scan_result: Dict[str, Any]) -> None:
        """
        Cache a scan result.
        
        Args:
            file_hash: SHA-256 hash of the file
            file_path: Path to the file
            scan_result: VirusTotal scan result
        """
        self.cache[file_hash] = {
            'file_path': file_path,
            'scan_result': scan_result,
            'timestamp': datetime.now().isoformat()
        }
        self._save_cache()
    
    def clear_expired(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        expired_keys = []
        now = datetime.now()
        
        for file_hash, entry in self.cache.items():
            if 'timestamp' in entry:
                cached_time = datetime.fromisoformat(entry['timestamp'])
                if now - cached_time > timedelta(days=self.cache_days):
                    expired_keys.append(file_hash)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self._save_cache()
        
        return len(expired_keys)
