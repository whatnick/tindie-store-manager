"""Product and inventory dataclasses for Tindie store management."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class ProductSpec:
    """Technical specifications for an energy monitor product."""
    voltage_range: Optional[str] = None
    current_range: Optional[str] = None
    accuracy: Optional[str] = None
    interfaces: list[str] = field(default_factory=list)
    connectivity: list[str] = field(default_factory=list)
    dimensions_mm: Optional[str] = None
    weight_g: Optional[float] = None
    extra: dict = field(default_factory=dict)


@dataclass
class Product:
    """Represents a single Tindie product listing."""
    sku: str
    name: str
    description: str
    price_usd: float
    stock: int
    category: str = "Energy Monitor"
    tags: list[str] = field(default_factory=list)
    specs: ProductSpec = field(default_factory=ProductSpec)
    images: list[str] = field(default_factory=list)
    image_glob: Optional[str] = None
    tindie_product_id: Optional[str] = None
    active: bool = True
    design_url: Optional[str] = None
    code_url: Optional[str] = None
    docs_url: Optional[str] = None
    youtube_url: Optional[str] = None
    seller_manufactured: bool = True
    listing_state: str = "draft"
    ships_from: Optional[str] = None
    shipping: dict = field(default_factory=dict)
    options: list[dict] = field(default_factory=list)

    @classmethod
    def from_yaml(cls, path: Path) -> "Product":
        """Load a product from a YAML file."""
        data = yaml.safe_load(path.read_text())
        specs_data = data.pop("specs", {})
        data["specs"] = ProductSpec(**specs_data)
        return cls(**data)

    def to_yaml(self, path: Path) -> None:
        """Persist product data to a YAML file."""
        d = asdict(self)
        path.write_text(yaml.dump(d, sort_keys=False, allow_unicode=True))

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Inventory:
    """Aggregated inventory across all products."""
    products: list[Product] = field(default_factory=list)

    @classmethod
    def load(cls, products_dir: Path) -> "Inventory":
        """Load all product YAML files from a directory."""
        products = [
            Product.from_yaml(p)
            for p in sorted(products_dir.glob("*.yaml"))
        ]
        return cls(products=products)

    def get(self, sku: str) -> Optional[Product]:
        """Look up a product by SKU."""
        return next((p for p in self.products if p.sku == sku), None)

    def low_stock(self, threshold: int = 5) -> list[Product]:
        """Return products at or below the given stock threshold."""
        return [p for p in self.products if p.stock <= threshold and p.active]

    def out_of_stock(self) -> list[Product]:
        return [p for p in self.products if p.stock == 0 and p.active]

    def summary(self) -> dict:
        return {
            "total_products": len(self.products),
            "active": sum(1 for p in self.products if p.active),
            "out_of_stock": len(self.out_of_stock()),
            "low_stock": len(self.low_stock()),
            "total_stock_value_usd": round(
                sum(p.price_usd * p.stock for p in self.products if p.active), 2
            ),
        }

    def to_json(self) -> str:
        return json.dumps([p.to_dict() for p in self.products], indent=2)
