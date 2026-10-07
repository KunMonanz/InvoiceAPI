class InvoiceException(Exception):
    """Base class for all invoice-related exceptions."""

    pass


class MissingTemplateException(InvoiceException):
    """Raised when the invoice template is missing."""

    def __init__(self, message="Template for invoice creation missing"):
        self.message = message
        super().__init__(self.message)
