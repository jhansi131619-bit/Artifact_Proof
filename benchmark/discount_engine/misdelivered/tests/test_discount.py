from checkout import CheckoutService


def test_discount_amount():
    service = CheckoutService()
    assert service.total_with_discount(100, 10) == 90.0


def test_zero_discount():
    service = CheckoutService()
    assert service.total_with_discount(100, 0) == 100.0


def test_negative_discount_invalid():
    service = CheckoutService()
    try:
        service.total_with_discount(100, -5)
        assert False, "Expected ValueError"
    except ValueError:
        pass
