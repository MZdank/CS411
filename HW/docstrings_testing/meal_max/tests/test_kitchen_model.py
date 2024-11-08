import pytest
from contextlib import contextmanager
import re
import sqlite3

from meal_max.models.kitchen_model import (
    Meal,
    create_meal,
    clear_meals,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("meal_max.models.kitchen_model.py.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

def test_create_meal(mock_cursor):
    """Testing creating a new meal"""
    create_meal(meal="Sushi", cuisine="Japanese", price="10", difficulty="HIGH")

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
#Add expected query after first successful run
    assert actual_query

    actual_arguments = mock_cursor.execute.call_args[0][1]

    assert actual_arguments

def test_create_song_invalid_duration():
    """Test error when trying to create a song with an invalid duration (e.g., negative duration)"""

    # Attempt to create a song with a negative duration
    with pytest.raises(ValueError, match="Invalid song duration: -180 \(must be a positive integer\)."):
        create_song(artist="Artist Name", title="Song Title", year=2022, genre="Pop", duration=-180)

    # Attempt to create a song with a non-integer duration
    with pytest.raises(ValueError, match="Invalid song duration: invalid \(must be a positive integer\)."):
        create_song(artist="Artist Name", title="Song Title", year=2022, genre="Pop", duration="invalid")

def test_create_meal_invalid_price():
    """Test error when trying to create a meal with invalid price (e.g., negative duration)"""

    # Attempt to create a meal with a negative price
    with pytest.raises(ValueError, match="Invalid price: -10. \Price must be a positive number\."):
        create_meal(meal="Sushi", cuisine="Japanese", price="-10", difficulty="HIGH")

    # Attempt to create a meal with a non-float price
    with pytest.raises(ValueError, match="Invalid price: ten. \Price must be a positive number\."):
        create_meal(meal="Sushi", cuisine="Japanese", price="ten", difficulty="HIGH")

