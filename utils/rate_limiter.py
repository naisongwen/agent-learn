"""
速率限制器
防止API调用过于频繁
"""

import time
import threading
from collections import deque

class RateLimiter:
    """令牌桶速率限制器"""
    
    def __init__(self, limit_per_minute: int = 60):
        self.limit = limit_per_minute
        self.interval = 60.0 / limit_per_minute  # 每次请求的最小间隔
        self.last_call = 0
        self.lock = threading.Lock()
    
    def acquire(self):
        """获取令牌，如果超限则等待"""
        with self.lock:
            now = time.time()
            time_since_last = now - self.last_call
            
            if time_since_last < self.interval:
                wait_time = self.interval - time_since_last
                time.sleep(wait_time)
            
            self.last_call = time.time()
    
    def try_acquire(self) -> bool:
        """尝试获取令牌，不等待"""
        with self.lock:
            now = time.time()
            time_since_last = now - self.last_call
            
            if time_since_last >= self.interval:
                self.last_call = now
                return True
            return False
