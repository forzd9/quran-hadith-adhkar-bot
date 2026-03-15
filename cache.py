"""
cache.py
نظام تخزين مؤقت بسيط مع خاصية انتهاء الصلاحية (TTL)
"""

import time
from typing import Any, Optional
from collections import OrderedDict
from logger import logger
from config import CACHE_TTL

class TTLCache:
    """ذاكرة تخزين مؤقت مع انتهاء الصلاحية"""

    def __init__(self, ttl: int = CACHE_TTL, maxsize: int = 100):
        self.ttl = ttl
        self.maxsize = maxsize
        self._cache = OrderedDict()  # key -> (value, expiry)

    def _clean_expired(self):
        """إزالة العناصر منتهية الصلاحية"""
        now = time.time()
        expired = [k for k, (_, exp) in self._cache.items() if exp < now]
        for k in expired:
            del self._cache[k]
            logger.debug(f"Cache expired: {k}")

    def _enforce_maxsize(self):
        """تطبيق الحد الأقصى للحجم (FIFO)"""
        while len(self._cache) > self.maxsize:
            self._cache.popitem(last=False)
            logger.debug("Cache maxsize reached, removed oldest")

    def get(self, key: str) -> Optional[Any]:
        """الحصول على قيمة من التخزين المؤقت"""
        self._clean_expired()
        if key in self._cache:
            value, _ = self._cache[key]
            logger.debug(f"Cache hit: {key}")
            return value
        logger.debug(f"Cache miss: {key}")
        return None

    def set(self, key: str, value: Any, ttl: int = None):
        """تخزين قيمة مع مدة صلاحية (اختيارية)"""
        self._clean_expired()
        expiry = time.time() + (ttl if ttl is not None else self.ttl)
        self._cache[key] = (value, expiry)
        self._enforce_maxsize()
        logger.debug(f"Cache set: {key} (expires in {ttl or self.ttl}s)")

    def delete(self, key: str):
        """حذف عنصر من التخزين المؤقت"""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache deleted: {key}")

    def clear(self):
        """مسح التخزين المؤقت بالكامل"""
        self._cache.clear()
        logger.debug("Cache cleared")

# كائن عام للتخزين المؤقت
cache = TTLCache()