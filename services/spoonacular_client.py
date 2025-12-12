
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
                    "source_url": Optional[str],
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
            normalized.append(
                {
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "image": item.get("image"),
                    # Spoonacular 'findByIngredients' doesn't always include the direct source URL; may be None.
                    "source_url": item.get("sourceUrl"),
                    "used_ingredients": [
                        ing.get("name") for ing in item.get("usedIngredients", []) if ing.get("name")
                    ],
                    "missed_ingredients": [
                        ing.get("name") for ing in item.get("missedIngredients", []) if ing.get("name")
                    ],
                    "likes": item.get("likes"),
                }
            )
        return normalized

    # ---------- Internal Helpers ----------

    def _build_url(self, path: str) -> str:
        """Safe join without double slashes."""
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def _get(self, path: str, params: Optional[dict] = None) -> Any:
        """
        Internal GET with basic retry for common transient errors (429 rate limiting and 5xx).
        Raises SpoonacularAPIError on non-success responses.
        """
        url = self._build_url(path)

        for attempt in range(self.max_retries):
            try:
                response = self._session.get(url, params=params, timeout=self.timeout_seconds)

                # Success
                if 200 <= response.status_code < 300:
                    # Try to parse JSON; if not JSON, return text
                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        return response.json()
                    # Fallback if API mislabels or returns text
                    try:
                        return response.json()
                    except ValueError:
                        return response.text

                # Handle rate limiting explicitly
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    sleep_secs = float(retry_after) if retry_after and retry_after.isdigit() else (
                        self.backoff_seconds * (attempt + 1)
                    )
                    if attempt < self.max_retries - 1:
                        time.sleep(sleep_secs)
                        continue
                    raise SpoonacularAPIError(
                        response.status_code,
                        "Rate limited by Spoonacular (429). Retries exhausted.",
                        payload=_safe_json(response),
                    )

                # Handle 5xx with backoff
                if 500 <= response.status_code < 600:
                    if attempt < self.max_retries - 1:
                        time.sleep(self.backoff_seconds * (attempt + 1))
                        continue
                    raise SpoonacularAPIError(
                        response.status_code,
                        f"Server error from Spoonacular ({response.status_code}). Retries exhausted.",
                        payload=_safe_json(response),
                    )

                # Other non-success: raise immediately with body
                raise SpoonacularAPIError(
                    response.status_code,
                    _extract_error_message(response),
                    payload=_safe_json(response),
                )

            except requests.RequestException as e:
                # Network errors/timeouts: backoff then retry
                if attempt < self.max_retries - 1:
                    time.sleep(self.backoff_seconds * (attempt + 1))
                    continue
                # Surface as SpoonacularAPIError with context
                raise SpoonacularAPIError(
                    -1,
                    f"Request failed: {e.__class__.__name__}: {str(e)}",
                    payload={"url": url, "params": params},
                ) from e


def _safe_json(response: requests.Response) -> dict:
    """Best-effort parse of a response body into JSON, else return {'raw': <text>}."""
    try:
        return response.json()
    except ValueError:
        return {"raw": response.text}


def _extract_error_message(response: requests.Response) -> str:
    """
    Extract a human-friendly error message from the response body.
    Tries JSON fields commonly used by APIs; falls back to status text.
    """
    try:
        data = response.json()
        # Look for common fields
        for key in ("message", "error", "status_message"):
            if isinstance(data, dict) and key in data and isinstance(data[key], str):
                return data[key]
        # If data is a string or list, show a snippet
        if isinstance(data, str):
            return data[:300]
        if isinstance(data, list) and data and isinstance(data[0], str):
            return data[0][:300]
    except ValueError:
        pass
    # Fallback: include status + a small text snippet
    snippet = response.text[:300].replace("\n", " ").strip()
    return snippet or f"HTTP {response.status_code}"
