class AuctionException(Exception):
    message = "An auction error occurred"

    def __init__(self, message: str = None):
        if message:
            self.message = message
        super().__init__(self.message)


class LotNotFoundException(AuctionException):
    message = "Lot not found"


class LotEndedException(AuctionException):
    message = "The auction for this lot has already ended"


class BidTooLowException(AuctionException):
    message = "Your bid is too low. It must be higher than the current lot price"


class LotCreateException(AuctionException):
    message = "Failed to create lot"


class BidCreateException(AuctionException):
    message = "Failed to place bid"
