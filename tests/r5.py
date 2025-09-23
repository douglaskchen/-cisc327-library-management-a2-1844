import pytest
import database
from datetime import datetime, timedelta

def test_late_fee_no_overdue(web_app):
    """check late fee is zero when returned on time"""
    book_title = "on time book"
    book_author = "author one"
    book_isbn = "9888888888888"
    patron_id = "444444"

    assert database.insert_book(book_title, book_author, book_isbn, 1, 1)
    book = database.get_book_by_isbn(book_isbn)
    book_id = book['id']

    borrow_date = datetime.now() - timedelta(days=5)
    due_date = borrow_date + timedelta(days=14)
    assert database.insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    database.update_book_availability(book_id, -1)

    response = web_app.get(f"/api/late_fee/{patron_id}/{book_id}")
    data = response.get_json()

    assert response.status_code == 200
    assert data["days_overdue"] == 0
    assert data["fee_amount"] == 0.0

def test_late_fee_within_seven_days(web_app):
    """check fee is 0.50 per day for up to 7 days overdue"""
    book_title = "short overdue book"
    book_author = "author two"
    book_isbn = "9999999999999"
    patron_id = "555555"

    assert database.insert_book(book_title, book_author, book_isbn, 1, 1)
    book = database.get_book_by_isbn(book_isbn)
    book_id = book['id']

    borrow_date = datetime.now() - timedelta(days=16)  # 2 days overdue
    due_date = borrow_date + timedelta(days=14)
    assert database.insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    database.update_book_availability(book_id, -1)

    response = web_app.get(f"/api/late_fee/{patron_id}/{book_id}")
    data = response.get_json()

    assert response.status_code == 200
    assert data["days_overdue"] == 2
    assert data["fee_amount"] == 1.0

def test_late_fee_beyond_seven_days(web_app):
    """check fee increases to 1.00 per day after 7 days overdue"""
    book_title = "long overdue book"
    book_author = "author three"
    book_isbn = "9000000000000"
    patron_id = "666666"

    assert database.insert_book(book_title, book_author, book_isbn, 1, 1)
    book = database.get_book_by_isbn(book_isbn)
    book_id = book['id']

    borrow_date = datetime.now() - timedelta(days=25)  # 11 days overdue
    due_date = borrow_date + timedelta(days=14)
    assert database.insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    database.update_book_availability(book_id, -1)

    response = web_app.get(f"/api/late_fee/{patron_id}/{book_id}")
    data = response.get_json()

    assert response.status_code == 200
    assert data["days_overdue"] == 11
    assert data["fee_amount"] == 3.5 + 4.0  # 7*0.5 + 4*1.0 = 7.5

def test_late_fee_maximum_cap(web_app):
    """check fee does not exceed maximum of 15.00"""
    book_title = "capped overdue book"
    book_author = "author four"
    book_isbn = "9111111111111"
    patron_id = "777777"

    assert database.insert_book(book_title, book_author, book_isbn, 1, 1)
    book = database.get_book_by_isbn(book_isbn)
    book_id = book['id']

    borrow_date = datetime.now() - timedelta(days=40)  # 26 days overdue
    due_date = borrow_date + timedelta(days=14)
    assert database.insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    database.update_book_availability(book_id, -1)

    response = web_app.get(f"/api/late_fee/{patron_id}/{book_id}")
    data = response.get_json()

    assert response.status_code == 200
    assert data["days_overdue"] == 26
    assert data["fee_amount"] == 15.0
