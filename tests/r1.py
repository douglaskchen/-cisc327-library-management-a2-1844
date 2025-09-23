import pytest
from library_service import (
    add_book_to_catalog
)

def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    
    assert success == True
    assert "successfully added" in message.lower()

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    assert success == False
    assert "13 digits" in message


# Add more test methods for each function and edge case. You can keep all your test in a separate folder named `tests`.

def test_add_book_invalid_isbn_too_long():
    """Test adding a book with ISBN too long."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "12345678901234", 5)
    
    assert success == False
    assert "13 digits" in message

def test_add_book_invalid_title_too_long():
    """Test adding a book with title too long"""
    success, message = add_book_to_catalog(41*"Title", "Test Author", "1234567890123", 5)
    
    assert success == False
    assert "title must be less than 200 characters" in message

def test_add_book_invalid_author_too_long():
    """Test adding a book with author too long"""
    success, message = add_book_to_catalog("Title", 26*"Test", "1234567890123", 5)
    
    assert success == False
    assert "title must be less than 200 characters" in message

def test_add_book_invalid_no_title():
    """Test adding a book with no title"""
    success, message = add_book_to_catalog("", "Test Author", "1234567890123", 5)
    
    assert success == False
    assert "author must be specified" in message

def test_add_book_invalid_no_author():
    """Test adding a book with no author"""
    success, message = add_book_to_catalog("Test Book", "", "1234567890123", 5)
    
    assert success == False
    assert "author must be specified" in message

def test_add_book_invalid_negative_total_copies():
    """Test adding a book with negative copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", -2)
    
    assert success == False
    assert "number of copies cannot be negative" in message