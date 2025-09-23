import database

def test_catalog_page_loads(web_app):
    """check that catalog page responds"""
    response = web_app.get("/catalog")
    assert response.status_code == 200


def test_catalog_entry_present(web_app):
    """check that record shows up in catalog output"""
    book_title = "title one"
    book_author = "author one"
    book_isbn = "9111111111111"
    copies_total = 4
    copies_free = 4

    assert database.insert_book(book_title, book_author, book_isbn, copies_total, copies_free)

    page = web_app.get("/catalog")
    page_text = page.get_data(as_text=True)

    assert book_title in page_text
    assert book_author in page_text
    assert book_isbn in page_text


def test_catalog_available(web_app):
    """check that catalog shows correct availability"""
    book_title = "title two"
    book_author = "author two"
    book_isbn = "9222222222222"
    copies_total = 5
    copies_free = 2

    assert database.insert_book(book_title, book_author, book_isbn, copies_total, copies_free)

    page = web_app.get("/catalog")
    page_text = page.get_data(as_text=True)

    assert f"{copies_free}/{copies_total} Available" in page_text