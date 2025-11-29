"""
Borrowing Routes - Book borrowing and returning endpoints
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.library_service import (
    borrow_book_by_patron,
    return_book_by_patron,
    get_all_books
)

borrowing_bp = Blueprint('borrowing', __name__)

@borrowing_bp.route('/borrow', methods=['GET', 'POST'])
def borrow_book():
    if request.method == "GET":
        books = get_all_books()
        return render_template("borrow.html", books=books)

    # POST
    patron_id = request.form.get("patron_id")
    book_id   = request.form.get("book_id")

    success, message = borrow_book_by_patron(patron_id, int(book_id))
    flash(message, "success" if success else "error")

    books = get_all_books()
    return render_template("borrow.html", books=books)


@borrowing_bp.route('/return', methods=['GET', 'POST'])
def return_book():
    """
    Process book return.
    """
    if request.method == 'GET':
        return render_template('return_book.html')
    
    patron_id = request.form.get('patron_id', '').strip()
    
    try:
        book_id = int(request.form.get('book_id', ''))
    except (ValueError, TypeError):
        flash('Invalid book ID.', 'error')
        return render_template('return_book.html')
    
    success, message = return_book_by_patron(patron_id, book_id)
    
    flash(message, 'success' if success else 'error')
    return render_template('return_book.html')
