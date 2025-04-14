class CurrentStatusNotFound(Exception):
    def __init__(self, msg=None, error_trace=None):
        super(CurrentStatusNotFound, self).__init__("Status context not found")
