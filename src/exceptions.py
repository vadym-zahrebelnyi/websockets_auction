class AuctionException(Exception):
    """Base exception for all auction-related errors."""

    message = "An auction error occurred"

    def __init__(self, message: str = None):
        if message:
            self.message = message
        super().__init__(self.message)


class LotNotFoundException(AuctionException):
    """Raised when a requested lot does not exist."""

    message = "Lot not found"


class LotEndedException(AuctionException):
    """Raised when an action is attempted on an auction that has already closed."""

    message = "The auction for this lot has already ended"


class BidTooLowException(AuctionException):
    """Raised when a placed bid is not higher than the current lot price."""

    message = "Your bid is too low. It must be higher than the current lot price"


class LotCreateException(AuctionException):
    """Raised when there is an error creating a new lot."""

    message = "Failed to create lot"


class BidCreateException(AuctionException):
    """Raised when there is an error recording a new bid."""

    message = "Failed to place bid"
