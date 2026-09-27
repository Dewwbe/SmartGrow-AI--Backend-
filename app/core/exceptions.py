"""Small set of domain exceptions mapped to HTTP responses in main.py."""


class NotFoundError(Exception):
    def __init__(self, resource: str, identifier: str):
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} '{identifier}' not found")


class DuplicateError(Exception):
    def __init__(self, resource: str, field: str, value: str):
        self.resource = resource
        self.field = field
        self.value = value
        super().__init__(f"{resource} with {field} '{value}' already exists")


class InvalidCredentialsError(Exception):
    def __init__(self):
        super().__init__("Invalid email or password")


class InvalidTokenError(Exception):
    def __init__(self, reason: str = "Invalid or expired token"):
        super().__init__(reason)
