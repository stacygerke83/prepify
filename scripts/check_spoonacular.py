
from dotenv import load_dotenv
load_dotenv()  # Make sure the .env in project root is read

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.spoonacular_client import SpoonacularClient, SpoonacularAPIError


def main():
    try:
        client = SpoonacularClient()
        print("=== Spoonacular Client ===")
        print(f"Base URL: {client.base_url}")
        print(f"API key loaded: {'yes' if client.api_key else 'no'}")

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