"""Read-only Tindie REST API client."""

import os
from typing import Optional
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv

load_dotenv()

TINDIE_ORIGIN = "https://www.tindie.com"
TINDIE_V1_API_BASE = f"{TINDIE_ORIGIN}/api/v1"
TINDIE_V2_API_BASE = f"{TINDIE_ORIGIN}/api/v2"
DEFAULT_PAGE_SIZE = 100


class TindieAPIError(Exception):
    pass


class TindieAPI:
    """Thin wrapper around the Tindie REST API."""

    def __init__(
        self,
        username: Optional[str] = None,
        api_key: Optional[str] = None,
        store_id: Optional[str] = None,
    ):
        self.username = username or os.environ["TINDIE_USERNAME"]
        self.api_key = api_key or os.environ["TINDIE_API_KEY"]
        self.store_id = store_id or os.environ.get("TINDIE_STORE_ID")
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"ApiKey {self.username}:{self.api_key}",
                "Accept": "application/json",
            }
        )

    def _get_url(self, url: str, params: Optional[dict] = None) -> dict:
        try:
            response = self._session.get(url, params=params, timeout=30)
        except requests.RequestException as exc:
            raise TindieAPIError(f"GET {url} failed: {exc}") from exc
        if not response.ok:
            detail = response.text.strip()[:500]
            raise TindieAPIError(
                f"GET {url} returned {response.status_code}"
                + (f": {detail}" if detail else "")
            )
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError as exc:
            raise TindieAPIError(f"GET {url} returned invalid JSON") from exc

    def _get_v1(self, endpoint: str, params: Optional[dict] = None) -> dict:
        return self._get_url(f"{TINDIE_V1_API_BASE}/{endpoint.strip('/')}/", params)

    def _get_v2(self, endpoint: str, params: Optional[dict] = None) -> dict:
        return self._get_url(f"{TINDIE_V2_API_BASE}/{endpoint.strip('/')}/", params)

    def _list_v2(self, endpoint: str, collection_key: str, params: dict) -> list[dict]:
        url: Optional[str] = f"{TINDIE_V2_API_BASE}/{endpoint.strip('/')}/"
        query: Optional[dict] = {**params, "limit": DEFAULT_PAGE_SIZE}
        objects: list[dict] = []

        while url:
            page = self._get_url(url, query)
            values = page.get(collection_key)
            if not isinstance(values, list):
                raise TindieAPIError(
                    f"GET {url} did not return a '{collection_key}' list"
                )
            objects.extend(values)
            next_page = page.get("meta", {}).get("next")
            url = urljoin(TINDIE_ORIGIN, next_page) if next_page else None
            query = None

        return objects

    def _resolve_store_id(self, reference_product_id: Optional[str]) -> str:
        if self.store_id:
            return self.store_id
        if not reference_product_id:
            raise TindieAPIError(
                "Set TINDIE_STORE_ID or provide a known reference product ID."
            )
        product = self.get_product(reference_product_id)
        store_id = str(product.get("store", {}).get("id", ""))
        if not store_id:
            raise TindieAPIError(
                f"Product {reference_product_id} did not include a store ID."
            )
        self.store_id = store_id
        return store_id

    # --- Products and inventory (V2, read-only) ---

    def list_products(
        self,
        store_id: Optional[str] = None,
        reference_product_id: Optional[str] = None,
    ) -> list[dict]:
        """Fetch every product in a store using the V2 API."""
        resolved_store_id = store_id or self._resolve_store_id(reference_product_id)
        return self._list_v2("products", "products", {"store": resolved_store_id})

    def get_product(self, product_id: str) -> dict:
        """Fetch one product, including stock and price, using the V2 API."""
        return self._get_v2(f"products/{product_id}")

    def get_inventory(
        self,
        store_id: Optional[str] = None,
        reference_product_id: Optional[str] = None,
    ) -> list[dict]:
        """Fetch products with their ``num_in_stock`` values."""
        return self.list_products(store_id, reference_product_id)

    def update_stock(self, product_id: str, quantity: int) -> None:
        """Reject unsupported API writes instead of reporting false success."""
        raise TindieAPIError(
            "Tindie API keys are read-only for V2 products; "
            "update stock through the seller UI."
        )

    # --- Orders (official V1 API) ---

    def list_orders(self, status: str = "all", limit: int = 50) -> list[dict]:
        """Fetch orders through the official V1 API."""
        result = self._get_v1("order", {"status": status, "limit": limit})
        orders = result.get("orders", result.get("objects", []))
        if not isinstance(orders, list):
            raise TindieAPIError("The orders endpoint returned an invalid response.")
        return orders
