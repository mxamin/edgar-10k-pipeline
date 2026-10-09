import threading
import time
from collections import deque


class SlidingWindowLogLimiter:
    def __init__(self, window: float, limit: int) -> None:
        self.window = window
        self.limit = limit
        self._log: deque[float] = deque(maxlen=limit)
        self._lock = threading.Lock()

    def acquire(self) -> None:
        while True:
            with self._lock:
                now = time.monotonic()
                elapsed = self.window
                if len(self._log) == self.limit:
                    elapsed = now - self._log[0]
                if elapsed >= self.window:
                    self._log.append(now)
                    return
            time.sleep(self.window - elapsed)

    def __enter__(self) -> SlidingWindowLogLimiter:
        self.acquire()
        return self

    def __exit__(self, *exc_info) -> None:
        pass
