import hashlib
import uuid

import requests

from config import CACHE_HTTP_DIR
from libs.rate_limiter import SlidingWindowLogLimiter


class SecClient:
    rate_limiter = SlidingWindowLogLimiter(window=1, limit=10)
    cache_records: dict[str, dict[str, str | None]] = {}
    _name = uuid.uuid4().hex[:8]
    user_agent = f"{_name} {_name}@example.com"

    def __init__(self) -> None:
        CACHE_HTTP_DIR.mkdir(parents=True, exist_ok=True)

    def get(self, url: str) -> bytes:
        key = hashlib.sha256(url.encode()).hexdigest()
        cache_path = CACHE_HTTP_DIR / key
        record = self.cache_records.get(key)

        headers = {"User-Agent": self.user_agent}
        if record is not None and cache_path.exists():
            if record["etag"]:
                headers["If-None-Match"] = record["etag"]
            if record["last_modified"]:
                headers["If-Modified-Since"] = record["last_modified"]

        with self.rate_limiter:
            response = requests.get(url, headers=headers)

        if response.status_code == 304:
            return cache_path.read_bytes()
        response.raise_for_status()

        cache_path.write_bytes(response.content)
        self.cache_records[key] = {
            "etag": response.headers.get("ETag"),
            "last_modified": response.headers.get("Last-Modified"),
        }
        return response.content
