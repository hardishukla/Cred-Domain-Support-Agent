from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Callable, Any
from src.config import PER_NODE_TIMEOUT, GLOBAL_GRAPH_TIMEOUT

class NodeTimeoutError(Exception):
    pass

class GlobalTimeoutError(Exception):
    pass

def with_node_timeout(func: Callable, timeout_seconds: int = None, *args, **kwargs) -> Any:
    """Execute func with a per-node timeout."""
    timeout = timeout_seconds or PER_NODE_TIMEOUT
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            raise NodeTimeoutError(f"Node timed out after {timeout}s")

def with_global_timeout(func: Callable, timeout_seconds: int = None, *args, **kwargs) -> Any:
    timeout = timeout_seconds or GLOBAL_GRAPH_TIMEOUT  
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            raise GlobalTimeoutError(f"Global graph timed out after {timeout}s")

def create_slow_function(delay_seconds: float):
    """Create a function that sleeps for the given delay."""
    def slow():
        import time
        time.sleep(delay_seconds)
        return {"status": "completed"}
    return slow
