# backend/services/recipe_api.py
import os
import time
import logging
import requests
from typing import List, Dict, Any
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SPOONACULAR_API_KEY")
BASE_URL = "https://api.spoonacular.com"
TIMEOUT = 15

_recipe_cache: Dict[int, Dict[str, Any]] = {}
_cache_ttl_seconds = 60 * 60 * 12  # 12 hours

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SpoonacularError(Exception):
    pass


def _get(url: str, params: Dict[str, Any]) -> requests.Response:
    """GET with basic retry/backoff and error handling."""
    if not API_KEY:
        raise SpoonacularError("Missing SPOONACULAR_API_KEY in environment.")

    # Always include API key
    params = {**params, "apiKey": API_KEY}

    backoff = [0.5, 1.0, 2.0]  # simple exponential backoff
    for i, sleep_s in enumerate(backoff + [0]):  # last attempt no sleep
        try:
            resp = requests.get(url, params=params, timeout=TIMEOUT)
            # Handle rate limiting (HTTP 429)
            if resp.status_code == 429 and i < len(backoff):
                time.sleep(sleep_s)
                continue
            resp.raise_for_status()
            return resp
        except requests.HTTPError as e:
            # For non-429 errors, bubble up immediately
            if resp is not None and resp.status_code != 429:
                raise SpoonacularError(f"HTTP error {resp.status_code}: {resp.text}") from e
            if i == len(backoff):  # final attempt failed
                raise SpoonacularError(f"Rate limit exceeded: {e}") from e
        except requests.RequestException as e:
            if i == len(backoff):
                raise SpoonacularError(f"Network error: {e}") from e
            time.sleep(sleep_s)


def find_by_ingredients(ingredients: List[str], number: int = 5, ranking: int = 1) -> List[Dict[str, Any]]:
    """
    Call Spoonacular /recipes/findByIngredients.
    Returns a list of recipe stubs (no sourceUrl yet).
    """
    url = f"{BASE_URL}/recipes/findByIngredients"
    params = {
        "ingredients": ",".join(ingredients),
        "number": max(1, min(number, 10)),  # keep reasonable
        "ranking": ranking,  # 1: maximize used ingredients, 2: minimize missing ingredients
        "ignorePantry": True,
    }
    resp = _get(url, params)
    return resp.json()


def _cache_get(recipe_id: int) -> Dict[str, Any] | None:
    item = _recipe_cache.get(recipe_id)
    if not item:
        return None
    if time.time() - item.get("_cached_at", 0) > _cache_ttl_seconds:
        # expired
        _recipe_cache.pop(recipe_id, None)
        return None
    return item


def recipe_information(recipe_id: int) -> Dict[str, Any]:
    """
    Get detailed info including sourceUrl.
    Uses cache to avoid repeated calls.
    """
    cached = _cache_get(recipe_id)
    if cached:
        return cached

    url = f"{BASE_URL}/recipes/{recipe_id}/information"
    params = {"includeNutrition": False}
    resp = _get(url, params)
    data = resp.json()
    data["_cached_at"] = time.time()
    _recipe_cache[recipe_id] = data
    return data


def slugify_title(title: str) -> str:
    return quote(title.lower().replace(" ", "-"))


def enrich_with_links(recipes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    For each recipe stub, attach a 'sourceUrl' (preferred) or a Spoonacular web URL fallback.
    Also normalize fields for frontend.
    """
    enriched = []
    for r in recipes:
        rid = r.get("id")
        info = {}
        try:
            info = recipe_information(rid)
        except SpoonacularError as e:
            logger.warning(f"Failed to fetch info for recipe {rid}: {e}")

        source_url = info.get("sourceUrl")
        if not source_url:
            # Fallback to spoonacular recipe page
            source_url = f"https://spoonacular.com/recipes/{slugify_title(r.get('title','recipe'))}-{rid}"

        enriched.append({
            "id": rid,
            "title": r.get("title"),
            "image": r.get("image"),
            "sourceUrl": source_url,
            "readyInMinutes": info.get("readyInMinutes"),
            "servings": info.get("servings"),
            "usedIngredients": [i.get("name") for i in r.get("usedIngredients", [])],
            "missedIngredients": [i.get("name") for i in r.get("missedIngredients", [])],
            "likes": r.get("likes"),
        })
    return enriched


def get_recipes_with_links(ingredients: List[str], number: int = 5, ranking: int = 1) -> List[Dict[str, Any]]:
    stubs = find_by_ingredients(ingredients, number=number, ranking=ranking)
    return enrich_with_links(stubs)
