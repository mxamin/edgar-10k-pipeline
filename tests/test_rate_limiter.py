import threading
import time

from libs.rate_limiter import SlidingWindowLogLimiter


def test_acquire_up_to_limit_does_not_block():
    limiter = SlidingWindowLogLimiter(window=10, limit=3)
    start = time.monotonic()
    for _ in range(3):
        limiter.acquire()
    assert time.monotonic() - start < 0.05


def test_acquire_blocks_until_slot_frees():
    limiter = SlidingWindowLogLimiter(window=0.2, limit=1)
    limiter.acquire()
    start = time.monotonic()
    with limiter:
        pass
    assert time.monotonic() - start >= 0.19


def test_concurrent_acquire_never_exceeds_limit():
    """4 threads x 3 acquires: in sorted grant times, any `limit + 1`
    consecutive stamps must span at least `window` (minus scheduling jitter),
    i.e. no sliding window ever admits more than `limit` acquisitions."""
    window, limit = 0.1, 3
    limiter = SlidingWindowLogLimiter(window=window, limit=limit)
    stamps = []
    stamps_lock = threading.Lock()

    def worker():
        for _ in range(3):
            limiter.acquire()
            with stamps_lock:
                stamps.append(time.monotonic())

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    stamps.sort()
    assert len(stamps) == 12
    tolerance = 0.01
    for i in range(len(stamps) - limit):
        assert stamps[i + limit] - stamps[i] >= window - tolerance
