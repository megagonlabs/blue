class InvalidRequestJson(Exception):
    status_code = 422

    def __init__(self, errors):
        super().__init__()
        self.errors = errors
