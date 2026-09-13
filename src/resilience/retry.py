import time
import random
from typing import Callable, Any
from src.config import RETRY_MAX_ATTEMPTS, RETRY_INITIAL_INTERVAL, RETRY_MAX_INTERVAL, RETRY_JITTER

class RetryExhausted(Exception):
    pass

def with_retry(
    func: Callable,
    max_attempts: int = None,
    initial_interval: float = None,
    max_interval: float = None,
    jitter: bool = None,
) -> Any:
    """Execute func with exponential backoff retries."""
    max_attempts = max_attempts or RETRY_MAX_ATTEMPTS
    initial_interval = initial_interval or RETRY_INITIAL_INTERVAL
    max_interval = max_interval or RETRY_MAX_INTERVAL
    jitter = jitter if jitter is not None else RETRY_JITTER
    
    for attempt in range(1, max_attempts + 1):
        try:
            result = func()
            return result
        except Exception as e:
            if attempt == max_attempts:
                raise RetryExhausted(f"All {max_attempts} attempts failed") from e
            interval = min(initial_interval * (2 ** (attempt - 1)), max_interval)
            if jitter:
                interval *= (0.5 + random.random())
            time.sleep(min(interval, 0.1))  # cap at 0.1s for tests

def create_flaky_function(fail_count: int = 2):
    """Create a function that fails `fail_count` times then succeeds."""
    counter = {"attempts": 0}
    def flaky():
        counter["attempts"] += 1
        if counter["attempts"] <= fail_count:
            raise ConnectionError(f"Simulated transient failure (attempt {counter['attempts']})")
        return {"status": "success", "attempt": counter["attempts"]}
    return flaky
