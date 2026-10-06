class AuthService:
    @staticmethod
    def authenticate(username, password):
        valid_users = {"alice": "s3cret", "bob": "hunter2"}
        if username not in valid_users:
            return False
        return valid_users[username] == password
