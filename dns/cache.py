import time
import threading
from collections import OrderedDict

class DNSCache:
    def __init__(self, max_size=1024):
        self.max_size = max_size
        self.store = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key):
        with self.lock:
            item = self.store.get(key)
            if not item:
                return None

            # TTL 过期
            if item["expires_at"] < time.time():
                del self.store[key]
                return None

            # LRU：最近使用
            self.store.move_to_end(key)
            return item["response"]

    def set(self, key, response: bytes, ttl: int):
        with self.lock:
            expires_at = time.time() + ttl

            self.store[key] = {
                "expires_at": expires_at,
                "response": response
            }

            self.store.move_to_end(key)

            # LRU 淘汰
            if len(self.store) > self.max_size:
                self.store.popitem(last=False)
