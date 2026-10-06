class UserService:
    def register(self, email, password):
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("invalid email")
        if len(password) < 8 or not any(ch.isdigit() for ch in password):
            raise ValueError("weak password")
        return {"email": email, "password": password}
