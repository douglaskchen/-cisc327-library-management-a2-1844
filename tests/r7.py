import pytest
import database
from datetime import datetime, timedelta
from library_service import borrow_book_by_patron, return_book_by_patron, get_patron_status_report

def test_patron_status_current_borrowed():
    """check patron status shows currently borrowed books with due dates"""
    title = "book one"
    author = "author one"
    isbn = "9333333333333"
    patron_id = "888888"

    assert database.insert_book(title, author, isbn, 1, 1)
    book = database.get_book_by_isbn(isbn)
    book_id = book['id']

    success, message = borrow_book_by_patron(patron_id, book_id)
    assert success is True

    status = get_patron_status_report(patron_id)
    assert "current_borrowed" in status
    assert any(b["book_id"] == book_id for b in status["current_borrowed"])

def test_patron_status_late_fees():
    """check patron status calculates total late fees"""
    title = "book two"
    author = "author two"
    isbn = "9444444444444"
    patron_id = "999999"

    assert database.insert_book(title, author, isbn, 1, 1)
    book = database.get_book_by_isbn(isbn)
    book_id = book['id']

    borrow_date = datetime.now() - timedelta(days=25)
    due_date = borrow_date + timedelta(days=14)
    assert database.insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    database.update_book_availability(book_id, -1)

    status = get_patron_status_report(patron_id)
    assert "total_late_fees" in status
    assert status["total_late_fees"] >= 0.0

def test_patron_status_borrow_count():
    """check patron status shows number of currently borrowed books"""
    title = "book three"
    author = "author three"
    isbn = "9555555555555"
    patron_id = "121212"

    assert database.insert_book(title, author, isbn, 1, 1)
    book = database.get_book_by_isbn(isbn)
    book_id = book['id']

    borrow_book_by_patron(patron_id, book_id)
    status = get_patron_status_report(patron_id)
    assert "borrow_count" in status
    assert status["borrow_count"] >= 1

def test_patron_status_borrow_history():
    """check patron status includes borrowing history"""
    title = "book four"
    author = "author four"
    isbn = "9666666666666"
    patron_id = "343434"

    assert database.insert_book(title, author, isbn, 1, 1)
    book = database.get_book_by_isbn(isbn)
    book_id = book['id']

    borrow_book_by_patron(patron_id, book_id)
    return_book_by_patron(patron_id, book_id)

    status = get_patron_status_report(patron_id)
    assert "history" in status
    assert any(h["book_id"] == book_id for h in status["history"])
