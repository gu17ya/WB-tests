import time


def wait_until(condition, timeout: float = 5, interval: float = 0.2) -> bool:
    """Re-check `condition` until it is true or the timeout expires (for data the exchange updates with a delay)."""
    deadline = time.monotonic() + timeout
    while not condition():
        if time.monotonic() >= deadline:
            return False
        time.sleep(interval)
    return True
