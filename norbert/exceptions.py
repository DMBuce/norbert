
# errors
GENERAL_ERROR = 1
INVALID_OPTION = 2
TAG_NOT_FOUND = 4
TAG_NOT_IMPLEMENTED = 5
TAG_CONVERSION_ERROR = 6
INVALID_VALUE = 7
INVALID_TYPE = 8

class Error(Exception):
    """Base class for exceptions in the norbert module."""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class InvalidOptionError(Exception):
    """Exception for invalid options or option arguments"""
    def __init__(self, option, message, value=None):
        self.option = option
        self.value = value
        self.message = message
        self.errno = INVALID_OPTION
        if value:
            self.strerror = "Invalid option: %s: %s: %s" % (option, message, value)
        else:
            self.strerror = "Invalid option: %s: %s" % (option, message)


