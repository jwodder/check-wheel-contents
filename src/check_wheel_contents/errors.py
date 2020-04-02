class UserInputError(ValueError):
    """
    Subclass of `ValueError` raised whenever the user supplies an invalid value
    for something
    """
    pass


class WheelValidationError(Exception):
    """ Error raised when a given wheel proves to be invalid or malformed """
    pass
