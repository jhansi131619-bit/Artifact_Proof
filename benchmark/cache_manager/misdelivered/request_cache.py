class RequestCache:
    def __init__(self):
        self._store = {}

    def fetch(self, key, default=None):
        return self._store.get(key, default)

    def store(self, key, value):
        self._store[key] = value
        return value
