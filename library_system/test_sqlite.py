import pytest
import sqlite3
from connection import DatabaseConection

@pytest.fixture
def create_data_base():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE books
        (id integer, title text, author text, created_at date)
        """
    )

    sample_data = [
        (1, "Pustyni i w puszczy", "Henryk Sienkiewicz", "2020-02-03 12:30:50"),
        (2, "Efektywny Python", "Slatkin", "2020-01-01 05:30:50")
    ]

    cursor.executemany("INSERT INTO books VALUES (?, ?, ?, ?)", sample_data)
    return cursor

def test_get_data(create_data_base):
    cursor = create_data_base
    data = DatabaseConection.get_data(cursor)
    assert data[0] == (1, "Pustyni i w puszczy", "Henryk Sienkiewicz", "2020-02-03 12:30:50")