"""Rate limiter for VirusTotal API requests."""
import json
import os
import time
from datetime import datetime, timedelta
from typing import List


class RateLimitError(Exception):
    """Exception raised when rate limit is exceeded."""
    pass


class RateLimiter:
    """Manages rate limiting for VirusTotal API calls."""
    
    def __init__(self, state_file: str = None,
                 requests_per_minute: int = 4, daily_limit: int = 500):
        """
        Initialize rate limiter.
        
        Args:
            state_file: Path to state file
            requests_per_minute: Maximum requests per minute
            daily_limit: Maximum requests per day
        """
        if state_file is None:
            state_file = os.path.join("data", "rate_limit_state.json")
        self.state_file = state_file
        self.requests_per_minute = requests_per_minute
        self.daily_limit = daily_limit
        self.request_timestamps: List[float] = []
        self.daily_count = 0
        self.last_reset_date = None
        self._load_state()
    
    def _load_state(self) -> None:
        """Load state from file."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.daily_count = state.get('daily_count', 0)
                    last_reset = state.get('last_reset_date')
                    if last_reset:
                        self.last_reset_date = datetime.fromisoformat(last_reset).date()
            except (IOError, ValueError) as e:
                print(f"Warning: Could not load rate limit state: {e}")
                self._reset_daily_count()
        else:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            self._reset_daily_count()
        
        # Check if we need to reset daily count
        today = datetime.now().date()
        if self.last_reset_date != today:
            self._reset_daily_count()
    
    def _save_state(self) -> None:
        """Save state to file."""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            state = {
                'daily_count': self.daily_count,
                'last_reset_date': self.last_reset_date.isoformat() if self.last_reset_date else None
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save rate limit state: {e}")
    
    def _reset_daily_count(self) -> None:
        """Reset daily request count."""
        self.daily_count = 0
        self.last_reset_date = datetime.now().date()
        self._save_state()
    
    def can_make_request(self) -> bool:
        """
        Check if a request can be made without exceeding limits.
        
        Returns:
            True if request can be made, False otherwise
        """
        # Check daily limit
        if self.daily_count >= self.daily_limit:
            return False
        
        # Check per-minute limit
        now = time.time()
        # Remove timestamps older than 1 minute
        self.request_timestamps = [ts for ts in self.request_timestamps if now - ts < 60]
        
        return len(self.request_timestamps) < self.requests_per_minute
    
    def wait_if_needed(self) -> float:
        """
        Wait if necessary to respect rate limits.
        
        Returns:
            Number of seconds waited
        """
        if self.daily_count >= self.daily_limit:
            raise RateLimitError(f"Daily limit of {self.daily_limit} requests reached. Try again tomorrow.")
        
        wait_time = 0.0
        while not self.can_make_request():
            # Calculate how long to wait
            now = time.time()
            self.request_timestamps = [ts for ts in self.request_timestamps if now - ts < 60]
            
            if self.request_timestamps:
                oldest_timestamp = min(self.request_timestamps)
                sleep_duration = 60 - (now - oldest_timestamp) + 0.1  # Add small buffer
                if sleep_duration > 0:
                    time.sleep(sleep_duration)
                    wait_time += sleep_duration
            else:
                break
        
        return wait_time
    
    def record_request(self) -> None:
        """Record that a request was made."""
        self.request_timestamps.append(time.time())
        self.daily_count += 1
        self._save_state()
    
    def get_remaining_daily_requests(self) -> int:
        """
        Get number of remaining requests for today.
        
        Returns:
            Number of remaining requests
        """
        return max(0, self.daily_limit - self.daily_count)
    
    def get_remaining_minute_requests(self) -> int:
        """
        Get number of remaining requests for current minute.
        
        Returns:
            Number of remaining requests
        """
        now = time.time()
        self.request_timestamps = [ts for ts in self.request_timestamps if now - ts < 60]
        return max(0, self.requests_per_minute - len(self.request_timestamps))
    
    def reset_for_testing(self) -> None:
        """Reset all limits (for testing purposes)."""
        self.request_timestamps = []
        self._reset_daily_count()
