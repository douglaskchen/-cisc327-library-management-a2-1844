# tests/conftest.py
import os, sys

# ensure repo root (where database.py lives) is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import database  # now resolves in CI too

def pytest_sessionstart(session):
    # fresh DB each run
    try:
        os.remove("library.db")
    except FileNotFoundError:
        pass
    database.init_database()
    database.add_sample_data()