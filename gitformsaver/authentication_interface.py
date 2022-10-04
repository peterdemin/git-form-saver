class AuthenticationInterface:

    def create_token(self, repo: str, path: str, secret: str = '') -> str:
        raise NotImplementedError

    def extract_token(self, text: str) -> str:
        raise NotImplementedError

    def is_valid_token(self, token: str, repo: str, path: str, secret: str = '') -> bool:
        raise NotImplementedError
