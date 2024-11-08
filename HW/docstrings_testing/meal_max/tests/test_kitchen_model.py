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

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]

    expected_arguments = ("Sushi", "Japanese", 10, "HIGH")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_meal_duplicate():
    """Testing creating a meal with a duplicate name"""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: Meal.meal")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError

# #make sure that match is right, it probably is not
    with pytest.raises(ValueError, match="Meal with meal 'Sushi' already exists."):
        create_meal(meal="Sushi", cuisine="Asian", price="11", difficulty="MED")

def test_create_meal_invalid_price():
    """Test error when trying to create a meal with invalid price (e.g., negative price)"""

    # Attempt to create a meal with a negative price
    with pytest.raises(ValueError, match="Invalid price: -10. \Price must be a positive number\."):
        create_meal(meal="Sushi", cuisine="Japanese", price="-10", difficulty="HIGH")

    # Attempt to create a meal with a non-float price
    with pytest.raises(ValueError, match="Invalid price: ten. \Price must be a positive number\."):
        create_meal(meal="Sushi", cuisine="Japanese", price="ten", difficulty="HIGH")

def test_create_meal_invalid_difficulty():
    """Test error when trying to create a meal with invalid difficulty (e.g., not "HIGH" "MED" or "LOW")"""

    # Attempt to create a meal with a non "HIGH" "MED" "LOW" difficulty
    with pytest.raises(ValueError, match="IInvalid difficulty level: Hard\. Must be 'LOW', 'MED', or 'HIGH'\."):
        create_meal(meal="Sushi", cuisine="Japanese", price="10", difficulty="Hard")

    # Attempt to create a meal with a non-string difficulty
    with pytest.raises(ValueError, match="Invalid difficulty level: 420\. Must be 'LOW', 'MED', or 'HIGH'\."):
        create_meal(meal="Sushi", cuisine="Japanese", price="10", difficulty=420)


