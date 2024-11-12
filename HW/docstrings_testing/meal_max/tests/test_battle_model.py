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

def test_battle(battle_model, sample_battle, mock_update_meal_stats):
    """Test a a battle will return the correct winner."""
    battle_model.combatants.extend(sample_battle)
    battle_model.battle()
    mock_update_meal_stats.assert_called_with(1, 'loss')

def test_battle_error(battle_model, sample_meal1):
     """Test error for starting a battle with only one combatant."""
     battle_model.prep_combatant(sample_meal1)
     with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
           battle_model.battle()


def test_clear_combatants(battle_model, sample_battle):
    """Test clearing the comatants of the battle."""
    battle_model.combatants.extend(sample_battle)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Combatants should be empty after clearing"
 
def test_get_battle_score(battle_model, sample_meal1):
    """Test getting the battle score generated for a combatant."""
    method_score = battle_model.get_battle_score(sample_meal1)
    computed_score = (19.02 * 6) - 3
    assert method_score == computed_score

def test_get_combatants(battle_model, sample_battle):
    """Test successfully retrieving all the combatants from the combatant table."""
    battle_model.combatants.extend(sample_battle)
    all_combatants = battle_model.get_combatants()
    assert len(all_combatants) == 2
    assert all_combatants[0].id == 1
    assert all_combatants[1].id == 2

def test_prep_combatant(battle_model, sample_meal1):
    """Test adding a meal to the combatant list."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'Soup'

def test_add3_prep_combatant(battle_model, sample_battle, sample_meal1):
    """Test error adding a combatant to a already full battle."""
    battle_model.combatants.extend(sample_battle)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal1)

