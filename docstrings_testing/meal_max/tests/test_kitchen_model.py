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

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

def test_create_meal(mock_cursor):
    """Testing creating a new meal"""
    create_meal(meal="Sushi", cuisine="Japanese", price=10, difficulty="HIGH")

    expected_query = normalize_whitespace("""
        INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]

    expected_arguments = ("Sushi", "Japanese", 10, "HIGH")
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_meal_duplicate(mock_cursor):
    """Testing creating a meal with a duplicate name"""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: Meal.meal")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError

# #make sure that match is right, it probably is not
    with pytest.raises(ValueError, match="Meal with name 'Sushi' already exists"):
        create_meal(meal="Sushi", cuisine="Asian", price=11, difficulty="MED")

def test_create_meal_invalid_price():
    """Test error when trying to create a meal with invalid price (e.g., negative price)"""

    # Attempt to create a meal with a negative price
    with pytest.raises(ValueError, match="Invalid price: -10. Price must be a positive number."):
        create_meal(meal="Sushi", cuisine="Japanese", price="-10", difficulty="HIGH")

    # Attempt to create a meal with a non-float price
    with pytest.raises(ValueError, match="Invalid price: ten. Price must be a positive number."):
        create_meal(meal="Sushi", cuisine="Japanese", price="ten", difficulty="HIGH")

def test_create_meal_invalid_difficulty():
    """Test error when trying to create a meal with invalid difficulty (e.g., not "HIGH" "MED" or "LOW")"""

    # Attempt to create a meal with a non "HIGH" "MED" "LOW" difficulty
    with pytest.raises(ValueError, match="Invalid difficulty level: Hard. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Sushi", cuisine="Japanese", price=10, difficulty="Hard")

    # Attempt to create a meal with a non-string difficulty
    with pytest.raises(ValueError, match="Invalid difficulty level: 420. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Sushi", cuisine="Japanese", price=10, difficulty=420)

def test_delete_meal(mock_cursor):
    """Test soft deleting a meal by meal ID."""

    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = ([False])

    # Call the delete_song function
    delete_meal(1)

    # Normalize the SQL for both queries (SELECT and UPDATE)
    expected_select_sql = normalize_whitespace("SELECT deleted FROM meals WHERE id = ?")
    expected_update_sql = normalize_whitespace("UPDATE meals SET deleted = TRUE WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Ensure the correct SQL queries were executed
    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""

    # Simulate that no meal exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent song
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""

    # Simulate that the song exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a song that's already been deleted
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)

def test_clear_meals(mock_cursor, mocker):
    """Test clearing the entire meal catalog (removes all meals)."""

    # Mock the file reading
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))

    # Call the clear_database function
    clear_meals()

    # Ensure the file was opened using the environment variable's path
    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')

    # Verify that the correct SQL script was executed
    mock_cursor.executescript.assert_called_once()

######################################################
#
#    Get Meal
#
######################################################

def test_get_meal_by_id(mock_cursor):
    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 15, "HIGH", False)

    # Call the function and check the result
    result = get_meal_by_id(1)

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Pizza", "Italian", 15, "HIGH")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (1,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_id_bad_id(mock_cursor):
    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_name(mock_cursor):
    # Simulate that the meal exists (1, "Pizza", "Italian", 15, "HIGH")
    mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 15, "HIGH", False)

    # Call the function and check the result
    result = get_meal_by_name("Pizza")

    # Expected result based on the simulated fetchone return value
    expected_result = Meal(1, "Pizza", "Italian", 15, "HIGH")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = ("Pizza",)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_meal_by_name_bad_name(mock_cursor):
    # Simulate that no meal exists for the given name
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with name LarryElison not found"):
        get_meal_by_name("LarryElison")

def test_update_meal_stats_win(mock_cursor):
    """Test updating the stats of a meal."""

    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_meal_stats function with a sample meal ID and a W
    meal_id = 1
    update_meal_stats(meal_id, 'win')

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (song ID)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_meal_stats_loss(mock_cursor):
    """Test updating the stats of a meal."""

    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_meal_stats function with a sample meal ID and a L
    meal_id = 1
    update_meal_stats(meal_id, 'loss')

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (song ID)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_meal_stats_deleted_meal(mock_cursor):
    """Test error when trying to update stats for a deleted meal."""

    # Simulate that the song exists but is marked as deleted (id = 1)
    mock_cursor.fetchone.return_value = [True]

    # Expect a ValueError when attempting to update a deleted song
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, 'win')

    # Ensure that no SQL query for updating play count was executed
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM meals WHERE id = ?", (1,))

######################################################
#
#    leaderboard
#
######################################################

def test_get_leaderboard_by_wins(mock_cursor):
    """Test retrieving the leaderboard of meals sorted by wins"""

    # I don't understand this, it seems to me to be cheating to hardcode it in order,
    # but in test_song_model it's hardcoded in order, so I guess that's fine????
    mock_cursor.fetchall.return_value = [
        (3, "Meal C", "Chinese", 10.00, "Hard", 5, 4, 0.80),
        (1, "Meal A", "Italian", 15.99, "Easy", 4, 3, 0.75),
        (2, "Meal B", "Mexican", 12.50, "Medium", 2, 1, 0.5)
    ]

    # Test sorting by wins
    leaderboard = get_leaderboard()

    # Expected output when sorted by wins
    expected_result_by_wins = [
        {"id": 3, "meal": "Meal C", "cuisine": "Chinese", "price": 10.00, "difficulty": "Hard", "battles": 5, "wins": 4, "win_pct": 80.0},
        {"id": 1, "meal": "Meal A", "cuisine": "Italian", "price": 15.99, "difficulty": "Easy", "battles": 4, "wins": 3, "win_pct": 75.0},
        {"id": 2, "meal": "Meal B", "cuisine": "Mexican", "price": 12.50, "difficulty": "Medium", "battles": 2, "wins": 1, "win_pct": 50.0},
    ]

    assert leaderboard == expected_result_by_wins, f"Expected {expected_result_by_wins}, but got {leaderboard}"

    # Ensure the SQL query was executed correctly for "wins" sort
    expected_query_by_wins = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
        ORDER BY wins DESC
    """)
    actual_query_by_wins = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query_by_wins == expected_query_by_wins, "The SQL query for wins did not match the expected structure."

def test_get_leaderboard_win_pct(mock_cursor):
    """Test retrieving the leaderboard of meals sorted by win_pct"""
    # Again, don't get this
    mock_cursor.fetchall.return_value = [
        (3, "Meal C", "Chinese", 10.00, "Hard", 5, 4, 0.80),
        (1, "Meal A", "Italian", 15.99, "Easy", 4, 3, 0.75),
        (2, "Meal B", "Mexican", 12.50, "Medium", 100, 50, 0.5)
    ]

    leaderboard = get_leaderboard(sort_by="win_pct")

    # Expected output when sorted by win percentage
    expected_result_by_win_pct = [
        {"id": 3, "meal": "Meal C", "cuisine": "Chinese", "price": 10.00, "difficulty": "Hard", "battles": 5, "wins": 4, "win_pct": 80.0},
        {"id": 1, "meal": "Meal A", "cuisine": "Italian", "price": 15.99, "difficulty": "Easy", "battles": 4, "wins": 3, "win_pct": 75.0},
        {"id": 2, "meal": "Meal B", "cuisine": "Mexican", "price": 12.50, "difficulty": "Medium", "battles": 100, "wins": 50, "win_pct": 50.0},
    ]

    assert leaderboard == expected_result_by_win_pct, f"Expected {expected_result_by_win_pct}, but got {leaderboard}"

    # Ensure the SQL query was executed correctly for "win_pct" sort
    expected_query_by_win_pct = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
        ORDER BY win_pct DESC
    """)
    actual_query_by_win_pct = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query_by_win_pct == expected_query_by_win_pct, "The SQL query for win_pct did not match the expected structure."

def test_get_leaderboard_invalid_sort(mock_cursor):
    """Sort it by a string that's not wins or win_pct"""
        
    # Again, don't get this
    mock_cursor.fetchall.return_value = [
        (3, "Meal C", "Chinese", 10.00, "Hard", 5, 4, 0.80),
        (1, "Meal A", "Italian", 15.99, "Easy", 4, 3, 0.75),
        (2, "Meal B", "Mexican", 12.50, "Medium", 100, 50, 0.5)
    ]

    with pytest.raises(ValueError, match="Invalid sort_by parameter: d-o double G"):
        get_leaderboard(sort_by="d-o double G")


def test_get_leaderboard_empty(mock_cursor, caplog):
    """Test getting the leaderboard when it's empty"""

    #empty
    mock_cursor.fetchall.return_value = []

    result = get_leaderboard()

    assert result == [], f"Expected empty list, but got {result}"

    expected_query = normalize_whitespace("""
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
        ORDER BY wins DESC
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."