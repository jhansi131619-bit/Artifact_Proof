from discount_engine import DiscountEngine


class CheckoutService:
    def __init__(self, engine=None):
        self.engine = engine or DiscountEngine()

    def total_with_discount(self, subtotal, percent):
        discount = self.engine.calculate_discount(subtotal, percent)
        return subtotal - discount

    def apply_discount(self, subtotal, percent):
        return self.total_with_discount(subtotal, percent)
