import os
import database

def pytest_sessionstart(session):
    # fresh DB each run
    try:
        os.remove("library.db")
    except FileNotFoundError:
        pass

    # create tables and seed sample rows
    database.init_database()
    database.add_sample_data()
