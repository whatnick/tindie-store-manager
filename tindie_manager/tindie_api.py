"""Tindie REST API client.

Tindie API docs: https://www.tindie.com/docs/api/

Set credentials via environment variables or a .env file:
    TINDIE_USERNAME=<your_username>
    TINDIE_API_KEY=<your_api_key>
"""

import os
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

TINDIE_API_BASE = "https://www.tindie.com/api/v1"


class TindieAPIError(Exception):
    pass


class TindieAPI:
    """Thin wrapper around the Tindie REST API."""

    def __init__(
        self,
        username: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.username = username or os.environ["TINDIE_USERNAME"]
        self.api_key = api_key or os.environ["TINDIE_API_KEY"]
        self._session = requests.Session()
        self._session.params = {  # type: ignore[assignment]
            "username": self.username,
            "api_key": self.api_key,
            "format": "json",
        }

    def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        url = f"{TINDIE_API_BASE}/{endpoint}/"
        resp = self._session.get(url, params=params or {})
        if not resp.ok:
            raise TindieAPIError(f"GET {url} → {resp.status_code}: {resp.text}")
        return resp.json()

    def _post(self, endpoint: str, data: dict) -> dict:
        url = f"{TINDIE_API_BASE}/{endpoint}/"
        resp = self._session.post(url, json=data)
        if not resp.ok:
            raise TindieAPIError(f"POST {url} → {resp.status_code}: {resp.text}")
        return resp.json()

    # --- Products ---

    def list_products(self) -> list[dict]:
        """Fetch all products from the store."""
        result = self._get("product")
        return result.get("objects", [])

    def get_product(self, product_id: str) -> dict:
        """Fetch a single product by its Tindie product ID."""
        result = self._get(f"product/{product_id}")
        return result

    # --- Inventory ---

    def get_inventory(self) -> list[dict]:
        """Fetch inventory levels for all products."""
        result = self._get("inventory")
        return result.get("objects", [])

    def update_stock(self, product_id: str, quantity: int, options: Optional[list[dict]] = None) -> dict:
        """Update stock for a product (and optional variants).

        Args:
            product_id: Tindie product resource URI or numeric ID.
            quantity:   New stock quantity (use -1 for unlimited).
            options:    List of variant dicts, each with 'sku' and 'quantity'.
        """
        payload: dict = {
            "product": f"/api/v1/product/{product_id}/",
            "quantity": quantity,
        }
        if options:
            payload["options"] = options
        return self._post("inventory", payload)

    # --- Orders ---

    def list_orders(self, status: str = "all", limit: int = 50) -> list[dict]:
        """Fetch orders filtered by status (open / shipped / all)."""
        result = self._get("order", params={"status": status, "limit": limit})
        return result.get("objects", [])

    def ship_order(self, order_id: str, tracking_code: str, carrier: str) -> dict:
        """Mark an order as shipped."""
        return self._post(
            f"order/{order_id}/ship",
            {"tracking_code": tracking_code, "carrier": carrier},
        )
