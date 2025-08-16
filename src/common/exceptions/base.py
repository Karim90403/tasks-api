class AppException(Exception):
    """Base Exception"""

    def __init__(self, msg, **params):
        if not hasattr(self, "params"):
            self.params = {}
        self.params.update(params)
