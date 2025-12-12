import os
import time
import logging
from typing import List, Dict, Any, Optional

import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

BASE_URL = "https://api.spoonacular.com"
API_KEY = os.getenv("SPOONACULAR_API_KEY")

class SpoonacularError(Exception):
    """Raised for Spoonacular client-level errors."""

def _check_api_key():
    if not API_KEY:
        raise SpoonacularError("Missing SPOONACULAR_API_KEY. Set it in your .env file.")

def _request_with_retry(url: str, params: Dict[str, Any], max_retries: int = 3, backoff_seconds: float = 1.0):
    """Minimal retry with exponential backoff for transient errors."""
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=10)
            # Rate limiting commonly yields HTTP 429; treat 5xx/429 as retryable
            if resp.status_code in (429, 500, 502, 503, 504):
                raise SpoonacularError(f"Retryable status {resp.status_code}: {resp.text}")
            resp.raise_for_status()
            return resp
        except (requests.exceptions.RequestException, SpoonacularError) as e:
            if attempt == max_retries:
                logger.error("Spoonacular request failed after retries: %s", e)
                raise
            sleep_for = backoff_seconds * (2 ** (attempt - 1))
            logger.warning("Request failed (attempt %d/%d). Retrying in %.1fs...", attempt, max_retries, sleep_for)
            time.sleep(sleep_for)

def search_recipes_by_ingredients(
    ingredients: List[str],
    number: int = 5,
    ranking: int = 1,
    ignore_pantry: bool = True,
) -> List[Dict[str, Any]]:
    """
    Calls Spoonacular 'findByIngredients' to return recipes for given ingredients.
    Docs: GET /recipes/findByIngredients
    """
    _check_api_key()
    url = f"{BASE_URL}/recipes/findByIngredients"
    params = {
        "apiKey": API_KEY,
        "ingredients": ",".join(ingredients),
        "number": number,
        "ranking": ranking,         # 1=maximize used ingredients, 2=minimize missing
        "ignorePantry": str(ignore_pantry).lower(),
    }
    resp = _request_with_retry(url, params)
    return resp.json()
