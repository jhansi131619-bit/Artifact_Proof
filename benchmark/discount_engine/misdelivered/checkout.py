class CheckoutService:
    def total_with_discount(self, subtotal, percent):
        if percent < 0:
            raise ValueError("percent cannot be negative")
        if percent == 0:
            return subtotal
        return subtotal * (1 - (percent / 100.0))

    def apply_discount(self, subtotal, percent):
        return self.total_with_discount(subtotal, percent)
