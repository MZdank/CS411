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
  response=$(curl -s -X DELETE "$BASE_URL/clear-meals")
  echo "Debugging Response: $response"  # This shows what’s actually received
  echo "$response" | grep -q '"status": "success"'
}


clear_catalog2() {
  echo "Clearing all meals..."
  response=$(curl -s -X DELETE "$BASE_URL/clear-meals")

  echo "Response: $response"  # Output the response for debugging

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meals cleared successfully."
  else
    echo "Failed to clear meals. Response: $response"
    exit 1
  fi
}

#check_health
#check_db
clear_catalog
#create_meal "Spaghetti" "Italian" 12.99 "MED"
clear_catalog2