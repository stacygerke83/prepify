from flask import Blueprint, request, jsonify
from app.services.spoonacular_client import search_recipes_by_ingredients, SpoonacularError

recipes_bp = Blueprint("recipes", __name__, url_prefix="/recipes")

@recipes_bp.get("/suggest")
def suggest():
    """
    ?ingredients=chicken,onion,garlic&number=5&ranking=1&ignorePantry=true
    """
    try:
        ingredients = request.args.get("ingredients", "")
        if not ingredients:
            return jsonify({"error": "ingredients query param required"}), 400
        number = int(request.args.get("number", 5))
        ranking = int(request.args.get("ranking", 1))
        ignore_pantry = request.args.get("ignorePantry", "true").lower() == "true"

        data = search_recipes_by_ingredients(
            ingredients=ingredients.split(","),
            number=number,
            ranking=ranking,
            ignore_pantry=ignore_pantry,
        )
        # Normalize minimal payload for UI cards
        normalized = [
            {
                "id": r.get("id"),
                "title": r.get("title"),
                "image": r.get("image"),
                "usedIngredientCount": r.get("usedIngredientCount"),
                "missedIngredientCount": r.get("missedIngredientCount"),
            }
            for r in data
        ]
        return jsonify({"recipes": normalized})
    except SpoonacularError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500
