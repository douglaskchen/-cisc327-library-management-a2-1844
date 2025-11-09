"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books
)

def pay_late_fees(patron_id: str, book_id: int, payment_gateway) -> Tuple[bool, str]:
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    if not isinstance(book_id, int) or book_id <= 0:
        return False, "Invalid book ID."
    
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."

    fee_info = calculate_late_fee_for_book(patron_id, book_id)
    fee = float(fee_info.get("fee_amount", 0.0))

    if fee <= 0.0:
        return False, "No late fee due."

    try:
        ok, ref = payment_gateway.process_payment(patron_id, round(fee, 2),
                                                  memo=f"Late fee for book_id={book_id}")
    except Exception as e:
        return False, f"Payment error: {type(e).__name__}"

    if not ok:
        return False, f"Payment declined: {ref}"

    return True, f"Paid ${fee:.2f}. Transaction: {ref}"


def refund_late_fee_payment(transaction_id: str, amount: float, payment_gateway) -> Tuple[bool, str]:
    if not transaction_id or not isinstance(transaction_id, str):
        return False, "Invalid transaction ID."
    if amount <= 0:
        return False, "Refund amount must be positive."
    if amount > 15.0:
        return False, "Refund exceeds $15 maximum."

    try:
        ok, ref = payment_gateway.refund_payment(transaction_id, round(float(amount), 2))
    except Exception as e:
        return False, f"Refund error: {type(e).__name__}"

    if not ok:
        return False, f"Refund declined: {ref}"

    return True, f"Refunded ${amount:.2f}. Reference: {ref}"
    

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # # Input validation
    # if not title or not title.strip():
    #     return False, "Title is required."
    
    # if len(title.strip()) > 200:
    #     return False, "Title must be less than 200 characters."
    
    # if not author or not author.strip():
    #     return False, "Author is required."
    
    # if len(author.strip()) > 100:
    #     return False, "Author must be less than 100 characters."
    
    # if len(isbn) != 13:
    #     return False, "ISBN must be exactly 13 digits."
    
    # if not isinstance(total_copies, int) or total_copies <= 0:
    #     return False, "Total copies must be a positive integer."
    
    # # Check for duplicate ISBN
    # existing = get_book_by_isbn(isbn)
    # if existing:
    #     return False, "A book with this ISBN already exists."
    
    # # Insert new book
    # success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    # if success:
    #     return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    # else:
    #     return False, "Database error occurred while adding the book."

    # Title
    if not isinstance(title, str) or not title.strip():
        return False, "Title is required."
    if len(title.strip()) > 200:
        return False, "Title must be less than or equal to 200 characters."

    # Author
    if not isinstance(author, str) or not author.strip():
        return False, "Author is required."
    if len(author.strip()) > 100:
        return False, "Author must be less than or equal to 100 characters."

    # ISBN: exactly 13 digits
    if not isinstance(isbn, str) or not isbn.isdigit() or len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."

    # Copies
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."

    # Uniqueness check
    if get_book_by_isbn(isbn) is not None:
        return False, "A book with this ISBN already exists."

    # Insert
    ok = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if not ok:
        return False, "Database error occurred while adding the book."

    return True, f'Successfully added "{title.strip()}" with ISBN {isbn}.'

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    
    TODO: Implement R4 as per requirements
    """
    return False, "Book return functionality is not yet implemented."

def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    
    TODO: Implement R5 as per requirements 

    
    return { // return the calculated values
        'fee_amount': 0.00,
        'days_overdue': 0,
        'status': 'Late fee calculation not implemented'
    }
    """
    from database import get_patron_borrowed_books
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {'fee_amount': 0.0, 'days_overdue': 0, 'status': 'Error'}
    book = get_book_by_id(book_id)
    if not book:
        return {'fee_amount': 0.0, 'days_overdue': 0, 'status': 'Error'}

    borrowed = [r for r in get_patron_borrowed_books(patron_id) if r['book_id'] == book_id]
    if not borrowed:
        return {'fee_amount': 0.0, 'days_overdue': 0, 'status': 'Not overdue'}

    due_date = borrowed[0]['due_date']
    today = datetime.now()
    if today <= due_date:
        return {'fee_amount': 0.0, 'days_overdue': 0, 'status': 'Not overdue'}

    days_over = (today.date() - due_date.date()).days
    first_segment = min(days_over, 7)
    second_segment = max(0, days_over - 7)
    fee = 0.5 * first_segment + 1.0 * second_segment
    fee = min(fee, 15.0)
    return {'fee_amount': round(fee, 2), 'days_overdue': days_over, 'status': 'OK'}

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    
    TODO: Implement R6 as per requirements
    """
    
    return []

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    
    TODO: Implement R7 as per requirements
    """
    return {}
