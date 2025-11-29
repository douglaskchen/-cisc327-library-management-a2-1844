import pytest
from unittest.mock import Mock
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway

# pay_late_fees scenarios

def test_pay_success_with_stubbed_fee_and_book(mocker):
    # Stubs: database lookups + fee calc
    mocker.patch("services.library_service.get_book_by_id", return_value={"id": 1, "title": "X"})
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 4.5, "days_overdue": 5, "status": "OK"})
    # Mock: gateway
    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.return_value = (True, "txn123")

    ok, msg = pay_late_fees("123456", 1, gateway)

    assert ok is True
    assert "Paid $4.50" in msg
    gateway.process_payment.assert_called_once_with("123456", 4.5, memo="Late fee for book_id=1")

def test_pay_declined_by_gateway(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value={"id": 1, "title": "X"})
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 2.0, "days_overdue": 2, "status": "OK"})
    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.return_value = (False, "DECLINED")

    ok, msg = pay_late_fees("123456", 1, gateway)

    assert ok is False
    assert "Payment declined" in msg
    gateway.process_payment.assert_called_once()

def test_pay_invalid_patron_id_mock_not_called(mocker):
    gateway = Mock(spec=PaymentGateway)
    ok, msg = pay_late_fees("12A456", 1, gateway)
    assert ok is False
    assert "Invalid patron ID" in msg
    gateway.process_payment.assert_not_called()

def test_pay_zero_fee_mock_not_called(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value={"id": 1, "title": "X"})
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 0.0, "days_overdue": 0, "status": "Not overdue"})
    gateway = Mock(spec=PaymentGateway)

    ok, msg = pay_late_fees("123456", 1, gateway)

    assert ok is False
    assert "No late fee due" in msg
    gateway.process_payment.assert_not_called()

def test_pay_gateway_exception_network(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value={"id": 1, "title": "X"})
    mocker.patch("services.library_service.calculate_late_fee_for_book",
                 return_value={"fee_amount": 3.0, "days_overdue": 3, "status": "OK"})
    gateway = Mock(spec=PaymentGateway)
    gateway.process_payment.side_effect = RuntimeError("timeout")

    ok, msg = pay_late_fees("123456", 1, gateway)

    assert ok is False
    assert "Payment error" in msg
    gateway.process_payment.assert_called_once()

# refund_late_fee_payment scenarios

@pytest.mark.parametrize("amount, err", [(-1.0, "positive"), (0.0, "positive"), (16.0, "exceeds")])
def test_refund_invalid_amounts(amount, err):
    gateway = Mock(spec=PaymentGateway)
    ok, msg = refund_late_fee_payment("txn1", amount, gateway)
    assert ok is False
    assert ("positive" in msg) or ("exceeds" in msg)
    gateway.refund_payment.assert_not_called()

def test_refund_invalid_txn_id():
    gateway = Mock(spec=PaymentGateway)
    ok, msg = refund_late_fee_payment("", 5.0, gateway)
    assert ok is False
    assert "Invalid transaction ID" in msg
    gateway.refund_payment.assert_not_called()

def test_refund_success():
    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.return_value = (True, "r123")
    ok, msg = refund_late_fee_payment("txn123", 5.0, gateway)
    assert ok is True
    assert "Refunded $5.00" in msg
    gateway.refund_payment.assert_called_once_with("txn123", 5.0)

def test_refund_declined():
    gateway = Mock(spec=PaymentGateway)
    gateway.refund_payment.return_value = (False, "DECLINED")
    ok, msg = refund_late_fee_payment("txn123", 5.0, gateway)
    assert ok is False
    assert "Refund declined" in msg
    gateway.refund_payment.assert_called_once()

def test_calculate_late_fee_over_10_days(monkeypatch):
    # Make library_service see a real book
    import services.library_service as ls
    from datetime import datetime, timedelta

    monkeypatch.setattr(ls, "get_book_by_id", lambda book_id: {"id": 1, "title": "X"})

    # Patch the DB accessor that the function imports inside
    import database
    due = datetime.now() - timedelta(days=10)
    def fake_get_patron_borrowed_books(pid):
        return [{"book_id": 1, "due_date": due}]
    monkeypatch.setattr(database, "get_patron_borrowed_books", fake_get_patron_borrowed_books, raising=True)

    info = ls.calculate_late_fee_for_book("123456", 1)
    assert info["status"] == "OK"
    # 7 days at $0.50 + 3 days at $1.00 = $6.50
    assert info["fee_amount"] == 6.5
    assert info["days_overdue"] >= 10  # allow for date rounding