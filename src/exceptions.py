class Error(Exception):
    def __init__(self, *, msg=None, error_trace=None):
        ''' Custom base class for app exceptions '''

        super(Error, self).__init__(msg)

        self.message = msg
        self.error_trace = error_trace


class ItemNotFound(Error):
    def __init__(self, *, msg=None, error_trace=None):
        ''' Custom common class for an item not found exception'''

        super(ItemNotFound, self).__init__(
            msg=msg or "Item not found",
            error_trace=error_trace
        )
