from validation_service import ValidationService


class UserService:
    def register(self, email, password):
        if not ValidationService.validate_email(email):
            raise ValueError("invalid email")
        if not ValidationService.validate_password(password):
            raise ValueError("weak password")
        return {"email": email, "password": password}
