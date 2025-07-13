import time
import asyncio
from typing import Dict, List, Optional
from collections import defaultdict

class RateLimiter:
    """Rate limiter to prevent spam and abuse"""
    
    def __init__(self, config: dict):
        self.config = config['behavior']['rate_limit']
        self.enabled = self.config['enabled']
        self.max_requests = self.config['max_requests']
        self.time_window = self.config['time_window']
        
        # Store request timestamps per user
        self.user_requests: Dict[str, List[float]] = defaultdict(list)
        
        # Global rate limiting
        self.global_requests: List[float] = []
        
    def is_allowed(self, user_id: str) -> bool:
        """Check if user is allowed to make a request"""
        if not self.enabled:
            return True
        
        current_time = time.time()
        
        # Clean old requests outside the time window
        self._clean_old_requests(current_time)
        
        # Check user-specific rate limit
        user_count = len(self.user_requests[user_id])
        if user_count >= self.max_requests:
            return False
        
        # Check global rate limit (2x user limit)
        global_count = len(self.global_requests)
        if global_count >= self.max_requests * 2:
            return False
        
        return True
    
    def record_request(self, user_id: str):
        """Record a request for rate limiting"""
        if not self.enabled:
            return
        
        current_time = time.time()
        
        # Add to user requests
        self.user_requests[user_id].append(current_time)
        
        # Add to global requests
        self.global_requests.append(current_time)
        
        # Clean old requests
        self._clean_old_requests(current_time)
    
    def _clean_old_requests(self, current_time: float):
        """Remove requests older than the time window"""
        cutoff_time = current_time - self.time_window
        
        # Clean user requests
        for user_id in list(self.user_requests.keys()):
            self.user_requests[user_id] = [
                req_time for req_time in self.user_requests[user_id]
                if req_time > cutoff_time
            ]
            
            # Remove empty user entries
            if not self.user_requests[user_id]:
                del self.user_requests[user_id]
        
        # Clean global requests
        self.global_requests = [
            req_time for req_time in self.global_requests
            if req_time > cutoff_time
        ]
    
    def get_user_stats(self, user_id: str) -> Dict[str, int]:
        """Get rate limiting stats for a user"""
        current_time = time.time()
        self._clean_old_requests(current_time)
        
        user_count = len(self.user_requests.get(user_id, []))
        global_count = len(self.global_requests)
        
        return {
            'user_requests': user_count,
            'user_limit': self.max_requests,
            'global_requests': global_count,
            'global_limit': self.max_requests * 2,
            'time_window': self.time_window
        }
    
    def reset_user(self, user_id: str):
        """Reset rate limiting for a specific user"""
        if user_id in self.user_requests:
            del self.user_requests[user_id]
    
    def reset_all(self):
        """Reset all rate limiting data"""
        self.user_requests.clear()
        self.global_requests.clear() 