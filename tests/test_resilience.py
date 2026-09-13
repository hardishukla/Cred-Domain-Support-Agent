import pytest
import time
from src.resilience.checkpointing import get_checkpointer
from src.resilience.retry import with_retry, create_flaky_function, RetryExhausted
from src.resilience.timeouts import with_node_timeout, with_global_timeout, create_slow_function, NodeTimeoutError, GlobalTimeoutError

# Checkpoint tests
def test_checkpointer_creates_db(tmpdir):
    db_path = str(tmpdir / "checkpoints.sqlite")
    saver = get_checkpointer(db_path)
    import os
    assert os.path.exists(db_path)

# Retry tests
def test_retry_succeeds_on_third_attempt():
    flaky = create_flaky_function(fail_count=2)
    res = with_retry(flaky, max_attempts=3, initial_interval=0.01)
    assert res["status"] == "success"

def test_retry_exhausted_raises():
    flaky = create_flaky_function(fail_count=5)
    with pytest.raises(RetryExhausted):
        with_retry(flaky, max_attempts=3, initial_interval=0.01)

def test_retry_immediate_success():
    flaky = create_flaky_function(fail_count=0)
    res = with_retry(flaky, max_attempts=3)
    assert res["attempt"] == 1

# Timeout tests
def test_node_timeout_fires():
    slow = create_slow_function(1.0)
    with pytest.raises(NodeTimeoutError):
        with_node_timeout(slow, timeout_seconds=0.1)

def test_node_timeout_fast_passes():
    slow = create_slow_function(0.01)
    res = with_node_timeout(slow, timeout_seconds=1.0)
    assert res["status"] == "completed"

def test_global_timeout_fires():
    slow = create_slow_function(1.0)
    with pytest.raises(GlobalTimeoutError):
        with_global_timeout(slow, timeout_seconds=0.1)

def test_global_timeout_fast_passes():
    slow = create_slow_function(0.01)
    res = with_global_timeout(slow, timeout_seconds=1.0)
    assert res["status"] == "completed"
