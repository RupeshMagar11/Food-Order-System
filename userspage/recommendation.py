from collections import Counter
from .models import Order
from demo_app.models import Food

def get_recommended_food_by_order_history(user_id):
    # Step 1: Retrieve all food items from the user's past orders
    past_orders = Order.objects.filter(user_id=user_id).select_related('food')
    ordered_foods = [order.food for order in past_orders]

    if not ordered_foods:
        return []  # No orders found, return an empty list

    # Step 2: Get a list of categories for foods the user has ordered
    ordered_categories = [food.category for food in ordered_foods]
    
    # Step 3: Recommend foods within the same category as the ordered items (exclude already ordered items)
    recommended_foods = Food.objects.filter(
        category__in=ordered_categories, is_available=True
    ).exclude(id__in=[food.id for food in ordered_foods])  # Exclude previously ordered food

    # Step 4: Sort the foods by food name (Bubble Sort, as in your example)
    food_list = list(recommended_foods)

    # Bubble Sort for sorting the food items by food name
    for i in range(len(food_list)):
        for j in range(0, len(food_list) - i - 1):
            if food_list[j].food_name > food_list[j + 1].food_name:
                # Swap if the food name of the current item is greater than the next
                food_list[j], food_list[j + 1] = food_list[j + 1], food_list[j]

    return food_list
