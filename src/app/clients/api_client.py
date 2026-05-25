import logging
import os
from typing import Any, cast

import httpx

logger = logging.getLogger(__name__)


class PotionLabClient:
    def __init__(self, base_url: str | None = None, token: str | None = None):
        self.base_url = base_url or os.getenv(
            "POTIONLAB_API_URL", "http://localhost:8000"
        )
        self.token = token or os.getenv("POTIONLAB_API_TOKEN")
        self.timeout = 5
        # Most recent error from a mutating call, for surfacing in UIs.
        self.last_error: str | None = None

    def set_token(self, token: str | None) -> None:
        self.token = token

    def _auth_headers(self) -> dict[str, str]:
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    @staticmethod
    def _extract_error(exc: httpx.HTTPError) -> str:
        """Best-effort, human-readable error message from an httpx failure."""
        response = getattr(exc, "response", None)
        if response is not None:
            try:
                body = response.json()
            except ValueError:
                body = None
            detail = None
            if isinstance(body, dict):
                detail = body.get("detail") or body.get("message")
                if isinstance(detail, list):  # FastAPI validation errors
                    detail = "; ".join(
                        f"{'.'.join(str(p) for p in item.get('loc', []))}: "
                        f"{item.get('msg', '')}"
                        for item in detail
                        if isinstance(item, dict)
                    )
            if detail:
                return f"HTTP {response.status_code}: {detail}"
            return f"HTTP {response.status_code}: {response.text[:200]}"
        return str(exc) or exc.__class__.__name__

    def login(self, username: str, password: str) -> str | None:
        """Exchange credentials for a JWT and remember it on the client.

        Returns the access token on success, or ``None`` on failure (with
        ``last_error`` populated).
        """
        self.last_error = None
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.post(
                    f"{self.base_url}/api/v1/auth/token",
                    json={"username": username, "password": password},
                )
                response.raise_for_status()
                token = response.json().get("access_token")
                if not token:
                    self.last_error = "Auth response missing access_token"
                    return None
                self.token = token
                return token
        except httpx.HTTPError as e:
            self.last_error = self._extract_error(e)
            logger.warning(f"Login failed: {self.last_error}")
            return None

    def list_cocktails(self) -> list[dict[str, Any]]:
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(
                    f"{self.base_url}/api/v1/cocktails/", headers=self._auth_headers()
                )
                response.raise_for_status()
                return cast(list[dict[str, Any]], response.json())
        except httpx.HTTPError as e:
            logger.warning(f"Failed to fetch cocktails: {e}")
            return []

    def get_cocktail(self, cocktail_id: int) -> dict[str, Any] | None:
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(
                    f"{self.base_url}/api/v1/cocktails/{cocktail_id}",
                    headers=self._auth_headers(),
                )
                response.raise_for_status()
                return cast(dict[str, Any], response.json())
        except httpx.HTTPError as e:
            logger.warning(f"Failed to fetch cocktail {cocktail_id}: {e}")
            return None

    def create_cocktail(self, data: dict[str, Any]) -> dict[str, Any] | None:
        self.last_error = None
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.post(
                    f"{self.base_url}/api/v1/cocktails/",
                    json=data,
                    headers=self._auth_headers(),
                )
                response.raise_for_status()
                return cast(dict[str, Any], response.json())
        except httpx.HTTPError as e:
            self.last_error = self._extract_error(e)
            logger.error(f"Failed to create cocktail: {self.last_error}")
            return None

    def list_ingredients(self) -> list[dict[str, Any]]:
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(f"{self.base_url}/api/v1/ingredients/")
                response.raise_for_status()
                return cast(list[dict[str, Any]], response.json())
        except httpx.HTTPError as e:
            logger.warning(f"Failed to fetch ingredients: {e}")
            return []

    def create_ingredient(self, data: dict[str, Any]) -> dict[str, Any] | None:
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.post(
                    f"{self.base_url}/api/v1/ingredients/", json=data
                )
                response.raise_for_status()
                return cast(dict[str, Any], response.json())
        except httpx.HTTPError as e:
            logger.error(f"Failed to create ingredient: {e}")
            return None

    def list_flavor_tags(self) -> list[dict[str, Any]]:
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(f"{self.base_url}/api/v1/flavor-tags/")
                response.raise_for_status()
                return cast(list[dict[str, Any]], response.json())
        except httpx.HTTPError as e:
            logger.warning(f"Failed to fetch flavor tags: {e}")
            return []

    def search_cocktails_by_ingredients(
        self, ingredient_ids: list[int]
    ) -> list[dict[str, Any]]:
        all_cocktails = self.list_cocktails()
        if not all_cocktails or not ingredient_ids:
            return []

        matching_cocktails = []
        ingredient_id_set = set(ingredient_ids)

        for cocktail_summary in all_cocktails:
            cocktail = self.get_cocktail(cocktail_summary["id"])
            if not cocktail or "ingredients" not in cocktail:
                continue

            cocktail_ingredient_ids = {
                ing["ingredient_id"] for ing in cocktail["ingredients"]
            }

            if ingredient_id_set.issubset(cocktail_ingredient_ids):
                matching_cocktails.append(cocktail_summary)

        return matching_cocktails
