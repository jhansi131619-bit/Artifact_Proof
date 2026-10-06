class DiscountEngine:
    @staticmethod
    def calculate_discount(subtotal, percent):
        if percent < 0:
            raise ValueError("percent cannot be negative")
        if percent == 0:
            return 0.0
        return subtotal * (percent / 100.0)
