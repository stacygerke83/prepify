Sanity check: initialize SpoonacularClient and fetch a small set of recipes.

Run:
    python scripts/check_spoonacular.py

Expected:
    - Prints base URL and whether API key is loaded
    - Shows 1-5 normalized recipe summaries
"""

from dotenv import load_dotenv
load_dotenv()  # Load variables from .env

from services.spoonacular_client import SpoonacularClient, SpoonacularAPIError


def main():
    try:
        client = SpoonacularClient()
        print("=== Spoonacular Client ===")
        print(f"Base URL: {client.base_url}")
        print(f"API key loaded: {'yes' if client.api_key else 'no'}")

        # Try a tiny query; adjust ingredients as needed
        ingredients = ["egg", "bread"]
        recipes = client.find_by_ingredients(ingredients, number=3)

        print("\n=== Sample Results ===")
        if not recipes:
            print("No recipes returned.")
            return

        for idx, r in enumerate(recipes, start=1):
            print(f"{idx}. {r.get('title')} (id={r.get('id')})")
            print(f"   image: {r.get('image')}")
            print(f"   used: {', '.join(r.get('used_ingredients', []))}")
            print(f"   missed: {', '.join(r.get('missed_ingredients', []))}")
            print(f"   likes: {r.get('likes')}")
            print()

    except SpoonacularAPIError as api_err:
        print("SpoonacularAPIError:", api_err)
        if getattr(api_err, "payload", None):
            print("Payload:", api_err.payload)
    except Exception as exc:
        print("Unexpected error:", exc)


if __name__ == "__main__":
    main()
