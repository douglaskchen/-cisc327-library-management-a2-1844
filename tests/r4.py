import pytest
import database
from datetime import datetime, timedelta
from services.library_service import borrow_book_by_patron, return_book_by_patron, calculate_late_fee_for_book

def test_return_valid_book():
    """check if patron returns book, availability and record are updated"""
    book_title = "returnable book"
    book_author = "return author"
    book_isbn = "9666666666666"
    copies_total = 1
    copies_free = 1
    patron_id = "111111"

    assert database.insert_book(book_title, book_author, book_isbn, copies_total, copies_free)
    book = database.get_book_by_isbn(book_isbn)
    book_id = book['id']

    success, message = borrow_book_by_patron(patron_id, book_id)
    assert success

    success, message = return_book_by_patron(patron_id, book_id)
    assert success is True
    assert "successfully returned" in message.lower()

    updated = database.get_book_by_id(book_id)
    assert updated['available_copies'] == copies_free

    conn = database.get_db_connection()
    record = conn.execute(
        "SELECT return_date FROM borrow_records WHERE patron_id=? AND book_id=?",
        (patron_id, book_id)
    ).fetchone()
    conn.close()
    assert record is not None
    assert record['return_date'] is not None

def test_return_book_not_borrowed():
    """check if returning a book not borrowed by patron fails"""
    patron_id = "222222"
    fake_book_id = 9999
    success, message = return_book_by_patron(patron_id, fake_book_id)
    assert success is False
    assert "not borrowed" in message.lower()

def test_return_patron_id_short():
    """check of patron id is valid"""
    success, message = return_book_by_patron("12abc", 1)
    assert success is False
    assert "invalid patron id" in message.lower()

def test_return_patron_id_long():
    """check of patron id is valid"""
    success, message = return_book_by_patron("1234abc", 1)
    assert success is False
    assert "invalid patron id" in message.lower()

def test_return_patron_id_valid():
    """check of patron id is valid"""
    success, message = return_book_by_patron("", 1)
    assert success is False
    assert "invalid patron id" in message.lower()

def test_return_with_late_fee():
    """check if late fee is calculated when book is returned past due date"""
    book_title = "late fee book"
    book_author = "late author"
    book_isbn = "9777777777777"
    patron_id = "333333"

    assert database.insert_book(book_title, book_author, book_isbn, 1, 1)
    book = database.get_book_by_isbn(book_isbn)
    book_id = book['id']

    borrow_date = datetime.now() - timedelta(days=20)
    due_date = borrow_date + timedelta(days=14)
    assert database.insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    database.update_book_availability(book_id, -1)

    success, message = return_book_by_patron(patron_id, book_id)
    assert success is True

    result = calculate_late_fee_for_book(patron_id, book_id)
    assert result['days_overdue'] > 0
    assert result['fee_amount'] >= 0.0