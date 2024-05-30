import os
from threading import Lock
import shelve
import logging
from typing import Any, Optional
from rapidfuzz.distance import DamerauLevenshtein


logger = logging.getLogger()
logger.setLevel(logging.INFO)

FILE_LOCKS = {}


class SimpleCache:
    """Simple cache."""

    def __init__(self, file_path: str, open: bool = True, fuzzy_threshold: float = 0.75):
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
        self._lock : Lock = FILE_LOCKS[full_path]

        self._path : str = full_path
        self._db : Optional[shelve.DbfilenameShelf] = None
        self._is_open : bool = False
        self._threshold : float = fuzzy_threshold
        # Open database for reading and writing
        if open:
            self.open()

    def __del__(self) -> None:
        if self._is_open:
            with self._lock:
                self.close()

    def _match(self, key: str, query: str) -> float:
        """Fuzzy matching helper method."""
        return DamerauLevenshtein.normalized_similarity(key, query) >= self._threshold

    def _get(self, key: str) -> dict:
        """Get data."""
        if not self._is_open:
            logger.error("cache is not open.")
            raise IOError("cache is not open.")
        with self._lock:
            data = self._db.get(key, default=[])
        return {key: data} if data else {}

    def _fuzzy_get(self, query: str) -> dict:
        """Get data with fuzzy matching."""
        if not self._is_open:
            logger.error("cache is not open.")
            raise IOError("cache is not open.")
        with self._lock:
            keys = list(
                filter(
                    lambda key: self._match(key, query),
                    sorted(self._db.keys())
                )
            )
            data = [self._db[key] for key in keys]
        return dict(zip(keys, data)) if keys else {}

    def open(self):
        """Open cache."""
        if self._is_open:
            logger.warn("cache is already open.")
            return
        with self._lock:
            self._db = shelve.open(self._path, flag='c', protocol=None, writeback=False)
        self._is_open = True

    def close(self):
        """Close cache."""
        if not self._is_open:
            logger.warn("cache is already closed.")
            return
        with self._lock:
            self._db.close()
        self._is_open = False

    def replace(self, key: Any, data: Any) -> None:
        """Replace data."""
        if not self._is_open:
            logger.error("cache is not open.")
            raise IOError("cache is not open.")
        key_ = str(key).lower()
        with self._lock:
            self._db[key_] = data if isinstance(data, list) else [data]

    def delete(self, key: Any) -> None:
        if not self._is_open:
            logger.error("cache is not open.")
            raise IOError("cache is not open.")
        key_ = str(key).lower()
        with self._lock:
            if key_ in self._db:
                del self._db[key_]

    def add(self, key: Any, data: Any) -> None:
        """Add data."""
        if not self._is_open:
            logger.error("cache is not open.")
            raise IOError("cache is not open.")
        data_ = []
        key_ = str(key).lower()
        with self._lock:
            if key_ in self._db:
                data_ = self._db[key_]
            if isinstance(data, list):
                data_.extend(data)
            else:
                data_.append(data)
            self._db[key_] = data_

    def get(self, query: Any, fuzzy: bool = False) -> Optional[dict]:
        """Get data."""
        if fuzzy:
            return self._fuzzy_get(str(query))
        else:
            return self._get(str(query))
