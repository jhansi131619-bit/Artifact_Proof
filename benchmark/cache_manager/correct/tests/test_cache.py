from request_cache import RequestCache


def test_store_and_fetch_value():
    cache = RequestCache()
    cache.store("a", 42)
    assert cache.fetch("a") == 42


def test_missing_key_returns_default():
    cache = RequestCache()
    assert cache.fetch("missing", "fallback") == "fallback"


def test_overwrite_value():
    cache = RequestCache()
    cache.store("x", 1)
    cache.store("x", 2)
    assert cache.fetch("x") == 2
