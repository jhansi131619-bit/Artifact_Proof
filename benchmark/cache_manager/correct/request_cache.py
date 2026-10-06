from cache_manager import CacheManager


class RequestCache:
    def __init__(self):
        self.manager = CacheManager()

    def fetch(self, key, default=None):
        return self.manager.get(key, default)

    def store(self, key, value):
        return self.manager.set(key, value)
