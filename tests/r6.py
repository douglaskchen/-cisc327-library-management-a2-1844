import pytest
import database
from services.library_service import search_books_in_catalog

def test_search_by_title_partial():
    """check search finds books by partial title case insensitive"""
    title = "book one"
    author = "author one"
    isbn = "9222333444555"
    assert database.insert_book(title, author, isbn, 1, 1)

    results = search_books_in_catalog("book", "title")
    assert any(r["title"] == title for r in results)

def test_search_by_author_partial():
    """check search finds books by partial author case insensitive"""
    title = "book two"
    author = "author two"
    isbn = "9222333444666"
    assert database.insert_book(title, author, isbn, 1, 1)

    results = search_books_in_catalog("two", "author")
    assert any(r["author"] == author for r in results)

def test_search_by_isbn_exact():
    """check search finds books only by exact isbn"""
    title = "book three"
    author = "author three"
    isbn = "9222333444777"
    assert database.insert_book(title, author, isbn, 1, 1)

    results_correct = search_books_in_catalog(isbn, "isbn")
    results_wrong = search_books_in_catalog("9222333", "isbn")

    assert any(r["isbn"] == isbn for r in results_correct)
    assert not any(r["isbn"] == isbn for r in results_wrong)

def test_search_no_results():
    """check search returns empty list when nothing matches"""
    results = search_books_in_catalog("nonexistent", "title")
    assert results == []

def test_search_invalid_isbn():
    """check search with invalid isbn returns no results"""
    results = search_books_in_catalog("123", "isbn")
    assert results == []

def test_search_case_insensitivity():
    """check search works regardless of case in title and author"""
    title = "book four"
    author = "author four"
    isbn = "9222333444888"
    assert database.insert_book(title, author, isbn, 1, 1)

    results_title = search_books_in_catalog("BOOK FOUR", "title")
    results_author = search_books_in_catalog("AuThOr FoUr", "author")

    assert any(r["title"] == title for r in results_title)
    assert any(r["author"] == author for r in results_author)
