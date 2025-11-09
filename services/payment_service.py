from typing import Tuple

__all__ = ["PaymentGatewayError", "PaymentGateway"]

class PaymentGatewayError(Exception):
    """Raised for gateway-level failures."""
    pass

class PaymentGateway:
    """External payment gateway API surface. Tests should mock this."""
    def process_payment(self, patron_id: str, amount: float, memo: str = "") -> Tuple[bool, str]:
        # Stubbed default; real impl would call a provider
        return True, "txn_demo"

    def refund_payment(self, transaction_id: str, amount: float) -> Tuple[bool, str]:
        return True, "refund_demo"
