class AppException(Exception):
    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details
