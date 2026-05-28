"""
Utility functions
"""
import asyncio
import time
import random
from functools import wraps
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from config import BOT_CONFIG
from modules.logger import logger

def delay(seconds):
    """Sleep with logging"""
    logger.debug(f"Waiting {seconds} seconds...")
    time.sleep(seconds)

def random_delay(min_sec=1, max_sec=5):
    """Random delay between operations"""
    wait_time = random.uniform(min_sec, max_sec)
    logger.debug(f"Random delay: {wait_time:.2f} seconds")
    time.sleep(wait_time)

def get_retry_decorator(max_attempts=None, wait_base=2):
    """Get retry decorator with exponential backoff"""
    if max_attempts is None:
        max_attempts = BOT_CONFIG["RETRY_ATTEMPTS"]
    
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=wait_base, max=60),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )

async def async_delay(seconds):
    """Async sleep"""
    logger.debug(f"Async waiting {seconds} seconds...")
    await asyncio.sleep(seconds)

def handle_errors(func):
    """Decorator to handle and log errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return None
    return wrapper

def truncate_address(address, length=4):
    """Truncate address for display"""
    if not address:
        return "unknown"
    return f"{address[:length]}...{address[-length:]}"

def format_tx_hash(tx_hash):
    """Format transaction hash"""
    if not tx_hash:
        return "unknown"
    return f"0x{tx_hash[-8:]}" if tx_hash.startswith("0x") else tx_hash[-8:]

def get_gas_price_gwei(gas_price_wei):
    """Convert gas price from wei to gwei"""
    return gas_price_wei / 1e9

class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, calls_per_second=10):
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0
    
    def wait(self):
        """Wait if necessary to maintain rate limit"""
        elapsed = time.time() - self.last_call
        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.3f}s")
            time.sleep(sleep_time)
        self.last_call = time.time()

class CircuitBreaker:
    """Circuit breaker for failing operations"""
    
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.is_open = False
    
    def record_success(self):
        """Record successful operation"""
        self.failure_count = 0
        self.is_open = False
        logger.debug("Circuit breaker: success recorded")
    
    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            logger.warning(f"Circuit breaker: opened after {self.failure_count} failures")
    
    def can_execute(self):
        """Check if operation can be executed"""
        if not self.is_open:
            return True
        
        # Check if recovery timeout has passed
        if time.time() - self.last_failure_time > self.recovery_timeout:
            logger.info("Circuit breaker: attempting recovery")
            self.is_open = False
            self.failure_count = 0
            return True
        
        return False

# Global rate limiter
rate_limiter = RateLimiter(calls_per_second=5)
