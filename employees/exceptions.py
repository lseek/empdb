"""Exceptions raised by the employee browser app."""

class EmployeeExc(Exception):
    """Base class for all app exceptions.
        
    Provides a common way to display exceptions. Subclass this class and define
    a 'message' property. That message will get printf'd with the keyword
    arguments provided to the constructor."""

    message = "An unknown exception occurred"

    def __init__(self, message=None, *args, **kwargs):
        if not message:
            message = self.message
        if kwargs:
            try:
                message = message % kwargs
            except Exception:
                # format string and args don't match - ignore it and try to get
                # out the underlying generic message.
                pass
        super(EmployeeExc, self).__init__(message)


class AuthFail(EmployeeExc):
    message = "Authentication failed for user:%(login)s - %(reason)s"


class InconsistentDB(EmployeeExc):
    message = "Records in the DB are not consistent"


class UnknownField(EmployeeExc):
    message = "Unknown field:%(field)s specified"
