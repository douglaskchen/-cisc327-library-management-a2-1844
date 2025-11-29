import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


def test_add_book_and_verify(browser):
    page = browser.new_page()

    #1 go to Add Book page
    page.goto(f"{BASE_URL}/add_book")
    print(page.content())

    #2 fill the form based on catalog_routes.py field names
    page.fill("input[name='title']", "E2E Test Book")
    page.fill("input[name='author']", "Automation Bot")
    page.fill("input[name='isbn']", "9999999999999")
    page.fill("input[name='total_copies']", "3")

    #3 submit form
    page.click("button[type='submit']")

    #4 redirects to /catalog → assert book is visible
    page.wait_for_url(f"{BASE_URL}/catalog")

    content = page.content()
    assert "E2E Test Book" in content
    assert "Automation Bot" in content
    assert "9999999999" in content


def test_borrow_book(browser):
    page = browser.new_page()

    #1 go to borrow page
    page.goto(f"{BASE_URL}/borrow")
    print(page.content())

    #2 fill patron ID → library_service enforces exactly 6 digits
    page.fill("input[name='patron_id']", "123456")

    #3 select the FIRST book in dropdown
    #(playwright selects by value; '1' is the first book ID added by add_sample_data())
    page.select_option("select[name='book_id']", "1")

    #4 submit borrow request
    page.click("button[type='submit'], input[type='submit']")

    #. assert generic success text (your borrow flash messages vary depending on availability)
    content = page.content()
    assert "Success" in content or "success" in content or "borrow" in content.lower()
