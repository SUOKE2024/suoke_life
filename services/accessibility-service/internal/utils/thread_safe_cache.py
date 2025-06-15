"""线程安全的缓存实现"""

import threading
from collections import OrderedDict


class ThreadSafeCache:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache = OrderedDict()
        self._lock = threading.RLock()


global_cache = ThreadSafeCache()
