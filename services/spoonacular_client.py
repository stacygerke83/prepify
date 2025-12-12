from __future__ import annotations

import os
import time
from typing import List, Optional, Dict, Any

import requests


DEFAULT_BASE_URL = os.getenv("SPOONACULAR_BASE_URL", "https://api.spoonacular.com")
FIND_BY_INGREDIENTS_PATH = "/recipes/findByIngredients"


class SpoonacularConfigError(Exception):
    """Raised when Spoonacular configuration is invalid or missing."""


class SpoonacularAPIError(Exception):
    """Raised when the Spoonacular API returns a non-success response."""
    def __init__(self, status_code: int, message: str, payload: Optional[dict] = None):
        super().__init__(f"Spoonacular API error {status_code}: {message}")
        self.status_code = status_code
        self.payload = payload or {}


class SpoonacularClient:

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: float = 10.0,
        max_retries: int = 3,
        backoff_seconds: float = 1.0,
    ):
        self.api_key = api_key or os.getenv("SPOONACULAR_API_KEY")
        self.base_url = base_url or DEFAULT_BASE_URL
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

        if not self.api_key:
            raise SpoonacularConfigError(
                "SPOONACULAR_API_KEY is missing. Set it in .env or pass explicitly to SpoonacularClient(api_key=...)."
            )
        if not self.base_url.startswith("https://"):
            raise SpoonacularConfigError("Invalid base URL. Must start with 'https://'.")

        self._session = requests.Session()


    def find_by_ingredients(
        self,
        ingredients: List[str],
        number: int = 5,
        ranking: int = 1,
        ignore_pantry: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Calls Spoonacular's /recipes/findByIngredients to get recipe suggestions.

        Args:
            ingredients: List of ingredient strings (e.g., ["chicken", "rice"])
            number: Max number of recipes to return (default: 5)
            ranking: 1 = maximize used ingredients, 2 = minimize missing ingredients
            ignore_pantry: If True, treats pantry staples as being unavailable

        Returns:
            List of normalized recipe dicts:
                {
                    "id": int,
                    "title": str,
                    "image": str | None,
                    "source_url": Optional[str],  # may require a subsequent call for full URL in advanced usage
                    "used_ingredients": [str],
                    "missed_ingredients": [str],
                    "likes": int | None
                }

        Raises:
            SpoonacularAPIError for non-2xx responses
        """
        if not ingredients:
            return []

        params = {
            "ingredients": ",".join(ingredients),
            "number": number,
            "ranking": ranking,
            "ignorePantry": str(ignore_pantry).lower(),
            "apiKey": self.api_key,
        }

        raw = self._get(FIND_BY_INGREDIENTS_PATH, params=params)
        # Normalize response structure
        normalized: List[Dict[str, Any]] = []
        for item in raw:
            normalized.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "image": item.get("image"),
                # Spoonacular 'findByIngredients' doesn't always include the direct source URL; keeping None for now.
                # You could add a follow-up call to /recipes/{id}/information to fetch sourceUrl if needed in Step 2.
                "source_url": item.get("sourceUrl"),
                "used_ingredients": [ing.get("name") for ing in item.get("usedIngredients", []) if ing.get("name")],
                "missed_ingredients": [ing.get("name") for ing in item.get("missedIngredients", []) if ing.get("name")],
                "likes": item.get("likes"),
            })
        return normalized

    # ---------- Internal Helpers ----------

    def _build_url(self, path: str) -> str:
        # Safe join without double slashes
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def _get(self, path: str, params: Optional[dict] = None) -> Any:
        """
        Internal GET with basic retry for common transient errors:
