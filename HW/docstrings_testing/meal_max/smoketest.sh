# Should be the same????
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=flase

###############################################
#
# Health checks
#
###############################################

check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed. :("
    exit 1
  fi
}

##########################################################
#
# Meals
#
##########################################################

create_meal() {
  meal_name=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Creating meal: Name: $meal_name, Cuisine: $cuisine, Price: $price, difficulty: $difficulty"
  curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal_name\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    exit 1
  fi
}

clear_catalog() {
  echo "Clearing all meals..."
  curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'
}

delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "/api/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-from-catalog-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get Meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1

  echo "Getting meal by name ($meal_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name ($meal_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (Name: $meal_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name ($meal_name)."
    exit 1
  fi
}


############################################################
#
# Battle
#
############################################################

prep_combatant() {
  meal_name=$1
  echo "Preparing combatant: $meal_name..."
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" -d "{\"meal\":\"$meal_name\"}")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatant prepared successfully: $meal_name"
  else
    echo "Failed to prepare combatant: $meal_name"
    exit 1
  fi
}

get_combatants() {
  echo "Retrieving list of combatants..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants retrieved successfully."
    echo "$response" | jq .combatants
  else
    echo "Failed to retrieve combatants."
    exit 1
  fi
}

test_battle() {
  echo "Initiating battle between prepared meals..."
  
  response=$(curl -s -X GET "$BASE_URL/api/battle")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle initiated successfully."
    winner=$(echo "$response" | jq -r '.winner')
    echo "The winner of the battle is: $winner"
  else
    echo "Battle initiation failed."
    exit 1
  fi
}

clear_combatants() {
  echo "Clearing all combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi
}

check_health
check_db
clear_catalog
create_meal "Spaghetti" "Italian" 69 "MED"
create_meal "Button" "Mongolian? I think" 42 "LOW"

clear_combatants

prep_combatant "Spaghetti"
prep_combatant "Button"

get_combatants

test_battle

clear_combatants

get_meal_by_name "Spaghetti"

get_meal_by_id 1
delete_meal_by_id 1

