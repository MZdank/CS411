import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the update_meal_stats function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.update_meal_stats")

"""Fixtures providing sample songs for the tests."""
@pytest.fixture
def sample_meal1():
    return Meal(1, 'Soup', 'Liquid', 19.02, 'LOW')

@pytest.fixture
def sample_meal2():
    return Meal(2, 'Steak', 'Meat', 23.0, 'HIGH')

@pytest.fixture
def sample_battle(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]

def test_clear_combatants(battle_model, sample_battle):
    """ Test clearing the comatants of the battle."""
    battle_model.battle(sample_battle)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants should be empty after clearing"
