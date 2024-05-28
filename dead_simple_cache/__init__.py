import os
from threading import Lock
import shelve
from bisect import insort
import logging
from typing import Any, Optional
from rapidfuzz.distance import DamerauLevenshtein


logger = logging.getLogger()
logger.setLevel(logging.INFO)

FILE_LOCKS = {}


class SimpleCache:
    """Simple cache."""

    def __init__(self, file_path: str, fuzzy_threshold: float = 0.75):
        if not file_path:
            logger.error("error setting cache: 'path' must be set")
            raise ValueError("'path' must be set")
        try:
            full_path = os.path.abspath(os.path.expanduser(file_path))
            base_dir = os.path.dirname(full_path)
            os.makedirs(base_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"error setting cache: {e}")
            raise ValueError(e)
        if full_path not in FILE_LOCKS:
            FILE_LOCKS[full_path] = Lock()
        self._lock = FILE_LOCKS[full_path]
        # Open database for reading and writing
        self._db = shelve.open(file_path, flag='c', protocol=None, writeback=False)
        self._threshold = fuzzy_threshold
        with self._lock:
            self.keys = list(sorted(self._db.keys()))

    def __del__(self) -> None:
        with self._lock:
            self._db.sync()
            self._db.close()

    def _match(self, key: str, query: str) -> float:
        """Fuzzy matching helper method."""
        return DamerauLevenshtein.normalized_similarity(key, query) >= self._threshold

    def _get(self, key: str) -> dict:
        """Get data."""
        with self._lock:
            data = self._db.get(key, default=[])
        return {key: data} if data else {}

    def _fuzzy_get(self, query: str) -> dict:
        """Get data with fuzzy matching."""
        with self._lock:
            keys = list(
                    filter(
                        lambda key: self._match(key, query),
                        self.keys
                    )
                )
            data = [self._db[key] for key in keys]
        return dict(zip(keys, data)) if keys else {}

    def replace(self, key: Any, data: Any) -> None:
        """Replace data."""
        key_ = str(key).lower()
        with self._lock:
            self._db[key_] = [data]

    def delete(self, key: Any) -> None:
        key_ = str(key).lower()
        with self._lock:
            if key_ in self.keys:
                del self._db[key_]
                self.keys.remove(key_)

    def add(self, key: Any, data: Any) -> None:
        """Add data."""
        data_ = []
        key_ = str(key).lower()
        with self._lock:
            if key_ in self.keys:
                data_ = self._db[key_]
            else:
                insort(self.keys, key_)
            data_.append(data)
            self._db[key_] = data_

    def get(self, query: Any, fuzzy: bool = False) -> Optional[dict]:
        """Get data."""
        if fuzzy:
            return self._fuzzy_get(str(query))
        else:
            return self._get(str(query))
