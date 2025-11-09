# tests/test_service_extra.py
from datetime import datetime, timedelta
from unittest.mock import Mock
import services.library_service as ls
from services.payment_service import PaymentGateway

# ---------- R3: borrow_book_by_patron guards ----------

def test_borrow_invalid_patron_id(monkeypatch):
    ok, msg = ls.borrow_book_by_patron("12A456", 1)
    assert not ok and "Invalid patron ID" in msg

def test_borrow_book_not_found(monkeypatch):
    monkeypatch.setattr(ls, "get_book_by_id", lambda _id: None)
    ok, msg = ls.borrow_book_by_patron("123456", 99)
    assert not ok and "Book not found" in msg

def test_borrow_no_copies(monkeypatch):
    monkeypatch.setattr(ls, "get_book_by_id", lambda _id: {"id": 1, "title": "X", "available_copies": 0})
    ok, msg = ls.borrow_book_by_patron("123456", 1)
    assert not ok and "not available" in msg

def test_borrow_limit_reached(monkeypatch):
    monkeypatch.setattr(ls, "get_book_by_id", lambda _id: {"id": 1, "title": "X", "available_copies": 2})
    monkeypatch.setattr(ls, "get_patron_borrow_count", lambda pid: 5)
    ok, msg = ls.borrow_book_by_patron("123456", 1)
    assert not ok and "maximum borrowing limit" in msg

def test_borrow_happy_path(monkeypatch):
    # make everything succeed
    monkeypatch.setattr(ls, "get_book_by_id", lambda _id: {"id": 1, "title": "X", "available_copies": 2})
    monkeypatch.setattr(ls, "get_patron_borrow_count", lambda pid: 0)
    monkeypatch.setattr(ls, "insert_borrow_record", lambda *a, **k: True)
    monkeypatch.setattr(ls, "update_book_availability", lambda *a, **k: True)
    ok, msg = ls.borrow_book_by_patron("123456", 1)
    assert ok and "Successfully borrowed" in msg and "Due date:" in msg

# ---------- R5: calculate_late_fee_for_book edges ----------

def test_late_fee_not_overdue(monkeypatch):
    from datetime import datetime, timedelta
    monkeypatch.setattr(ls, "get_book_by_id", lambda _id: {"id": 1})
    import database
    due = datetime.now() + timedelta(hours=1)  # future → definitely not overdue
    monkeypatch.setattr(database, "get_patron_borrowed_books",
                        lambda pid: [{"book_id": 1, "due_date": due}])
    info = ls.calculate_late_fee_for_book("123456", 1)
    assert info["status"] == "Not overdue" and info["fee_amount"] == 0.0

def test_late_fee_boundary_7_days(monkeypatch):
    monkeypatch.setattr(ls, "get_book_by_id", lambda _id: {"id": 1})
    import database
    due = datetime.now() - timedelta(days=7, hours=1)
    monkeypatch.setattr(database, "get_patron_borrowed_books",
                        lambda pid: [{"book_id": 1, "due_date": due}])
    info = ls.calculate_late_fee_for_book("123456", 1)
    # 7 * $0.50 = $3.50
    assert info["fee_amount"] == 3.5

def test_late_fee_cap_15(monkeypatch):
    monkeypatch.setattr(ls, "get_book_by_id", lambda _id: {"id": 1})
    import database
    due = datetime.now() - timedelta(days=40)
    monkeypatch.setattr(database, "get_patron_borrowed_books",
                        lambda pid: [{"book_id": 1, "due_date": due}])
    info = ls.calculate_late_fee_for_book("123456", 1)
    assert info["fee_amount"] == 15.0  # capped

def test_late_fee_invalid_inputs(monkeypatch):
    info = ls.calculate_late_fee_for_book("abc", 1)
    assert info["status"] == "Error"

# ---------- Payments: remaining guards not hit yet ----------

def test_pay_late_fees_book_missing(monkeypatch):
    monkeypatch.setattr(ls, "get_book_by_id", lambda _id: None)
    gateway = Mock(spec=PaymentGateway)
    ok, msg = ls.pay_late_fees("123456", 42, gateway)
    assert not ok and "Book not found" in msg
    gateway.process_payment.assert_not_called()

def test_refund_late_fee_invalid_types():
    gateway = Mock(spec=PaymentGateway)
    ok, msg = ls.refund_late_fee_payment(None, 5.0, gateway)
    assert not ok and "Invalid transaction ID" in msg
