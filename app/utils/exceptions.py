class InventoryAppError(Exception):
    """Base exception for all domain-specific InventoryPro errors."""
    def __init__(self, message="An unexpected error occurred in InventoryPro."):
        self.message = message
        super().__init__(self.message)


class InsufficientStockError(InventoryAppError):
    """Raised when an inventory issue/sale exceeds available on-hand stock."""
    def __init__(self, product_name, requested, available):
        self.product_name = product_name
        self.requested = requested
        self.available = available
        message = (
            f"Insufficient stock for '{product_name}'. "
            f"Requested: {requested}, Available: {available}."
        )
        super().__init__(message)


class DuplicateResourceError(InventoryAppError):
    """Raised when attempting to create a record with an existing unique identifier."""
    pass


class ResourceNotFoundError(InventoryAppError):
    """Raised when a requested domain entity does not exist."""
    pass


class InvalidOperationError(InventoryAppError):
    """Raised when an invalid state transition or operation is attempted."""
    pass
