import pytest
import database
from services.library_service import borrow_book_by_patron

def test_borrow_valid_book():
    """check if borrow record and # of copies is updated"""
    book_title = "borrowable book"
    book_author = "borrow author"
    book_isbn = "9333333333333"
    copies_total = 2
    copies_free = 2

    assert database.insert_book(book_title, book_author, book_isbn, copies_total, copies_free)
    book = database.get_book_by_isbn(book_isbn)
    book_id = book['id']

    patron_id = "123456"
    success, message = borrow_book_by_patron(patron_id, book_id)

    assert success is True
    assert "successfully borrowed" in message.lower()
    updated = database.get_book_by_id(book_id)
    assert updated['available_copies'] == copies_free - 1

def test_borrow_invalid_patron_id():
    """check patron id is valid"""
    success, message = borrow_book_by_patron("abc12", 1)
    assert success is False
    assert "invalid patron id" in message.lower()

def test_borrow_book_not_found():
    """check book id is valid"""
    success, message = borrow_book_by_patron("123456", 9999)
    assert success is False
    assert "book not found" in message.lower()

def test_borrow_book_unavailable():
    """check if book is available to borrow"""
    book_title = "unavailable book"
    book_author = "no copies"
    book_isbn = "9444444444444"
    copies_total = 1
    copies_free = 0

    assert database.insert_book(book_title, book_author, book_isbn, copies_total, copies_free)
    book = database.get_book_by_isbn(book_isbn)
    book_id = book['id']

    success, message = borrow_book_by_patron("123456", book_id)

    assert success is False
    assert "not available" in message.lower()

def test_borrow_patron_limit():
    """check if patron is within borrow limit"""

    patron_id = "654321"

    # create 6 books so patron can borrow 6 times
    for i in range(6):
        book_title = f"limit book {i}"
        book_author = "limit author"
        book_isbn = f"95555555555{i:02d}"  # unique isbn
        copies_total = 1
        copies_free = 1

        assert database.insert_book(book_title, book_author, book_isbn, copies_total, copies_free)
        book = database.get_book_by_isbn(book_isbn)
        book_id = book['id']

        success, message = borrow_book_by_patron(patron_id, book_id)

        if i < 5:
            assert success is True
        else:
            assert success is False
            assert "maximum borrowing limit" in message.lower()
