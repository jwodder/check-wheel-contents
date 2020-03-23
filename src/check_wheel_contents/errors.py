class UserInputError(ValueError):
    """
    Subclass of `ValueError` raised whenever the user supplies an invalid value
    for something
    """
    pass


class WheelValidationError(Exception):
    pass


class InvalidFilenameError(WheelValidationError, ValueError):
    """ Raised when an invalid wheel filename is encountered """

    def __init__(self, filename):
        #: The invalid filename
        self.filename = filename

    def __str__(self):
        return 'Invalid wheel filename: ' + repr(self.filename)
