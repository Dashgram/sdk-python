class DashgramError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InvalidCredentials(DashgramError):
    def __init__(self, message: str = "Invalid project_id or access_key"):
        super().__init__(message)


class DashgramApiError(DashgramError):
    def __init__(self, status_code: int, details: str):
        self.status_code = status_code
        self.details = details
        super().__init__(f"{self.details} - Status Code: {self.status_code}")
