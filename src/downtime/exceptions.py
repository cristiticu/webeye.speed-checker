from exceptions import ItemNotFound


class CurrentStatusNotFound(ItemNotFound):
    def __init__(self, msg=None, error_trace=None):
        super(CurrentStatusNotFound, self).__init__(
            msg=msg or "Status context not found", error_trace=error_trace)
