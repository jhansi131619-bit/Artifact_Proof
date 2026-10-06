from auth_service import AuthService


class AppService:
    def login(self, username, password):
        return AuthService.authenticate(username, password)
