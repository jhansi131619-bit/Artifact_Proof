class ValidationService:
    @staticmethod
    def validate_email(email):
        return "@" in email and "." in email.split("@")[-1]

    @staticmethod
    def validate_password(password):
        return len(password) >= 8 and any(ch.isdigit() for ch in password)
