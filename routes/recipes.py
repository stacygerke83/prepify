from flask import Blueprint, request, render_template
from services.spoonacular_client import find_by_ingredients, SpoonacularClientError

recipes_bp = Blueprint("recipes", __name__, url_prefix="/recipes")

@recipes_bp.route("/suggest", methods=["GET", "POST"])
def suggest():
    # Accept "ingredients" as comma-separated text
    if request.method == "POST":
        payload = request.get_json(silent=True) or request.form
        ing_raw = (payload.get("ingredients") or "").strip()
    else:
        ing_raw = (request.args.get("ingredients") or "").strip()

    ingredients = [i.strip() for i in ing_raw.split(",") if i.strip()]

    if not ingredients:
        return render_template("recipes.html", recipes=[], error="Provide ingredients (comma-separated).")

    try:
        recipes = find_by_ingredients(ingredients, number=5, ranking=1, ignore_pantry=True)
    except SpoonacularClientError as e:
        return render_template("recipes.html", recipes=[], error=str(e)), 502

    return render_template("recipes.html", recipes=recipes, error=None)
