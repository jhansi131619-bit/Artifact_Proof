class CacheManager:
    def __init__(self):
        self._store = {}

    def get(self, key, default=None):
        return default

    def set(self, key, value):
        return value
