import hashlib
import time
import uuid
from datetime import timedelta
from typing import Any

import requests

from config import CACHE_HTTP_DIR
from libs.rate_limiter import SlidingWindowLogLimiter


class SecClient:
    rate_limiter = SlidingWindowLogLimiter(window=1, limit=10)
    cache_records: dict[str, dict[str, Any]] = {}
    _name = uuid.uuid4().hex[:8]
    user_agent = f"{_name} {_name}@example.com"

    def __init__(self, expiration: timedelta | None = None) -> None:
        self.expiration = expiration
        CACHE_HTTP_DIR.mkdir(parents=True, exist_ok=True)

    def get(self, url: str) -> bytes:
        key = hashlib.sha256(url.encode()).hexdigest()
        cache_path = CACHE_HTTP_DIR / key
        record = self.cache_records.get(key)
        cached = record is not None and cache_path.exists()

        if (
            cached
            and self.expiration is not None
            and time.monotonic() - record["fetched_at"] < self.expiration.total_seconds()
        ):
            return cache_path.read_bytes()

        headers = {"User-Agent": self.user_agent}
        if cached:
            if record["etag"]:
                headers["If-None-Match"] = record["etag"]
            if record["last_modified"]:
                headers["If-Modified-Since"] = record["last_modified"]

        with self.rate_limiter:
            response = requests.get(url, headers=headers)

        if response.status_code == 304:
            record["fetched_at"] = time.monotonic()
            return cache_path.read_bytes()
        response.raise_for_status()

        cache_path.write_bytes(response.content)
        self.cache_records[key] = {
            "etag": response.headers.get("ETag"),
            "last_modified": response.headers.get("Last-Modified"),
            "fetched_at": time.monotonic(),
        }
        return response.content
