#!/usr/bin/env python3
"""Update stock for a product — locally and optionally push to Tindie API."""

import sys
from pathlib import Path

import click
from rich.console import Console

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tindie_manager.product import Inventory
from tindie_manager.tindie_api import TindieAPI, TindieAPIError

console = Console()
PRODUCTS_DIR = Path(__file__).resolve().parents[1] / "products"


@click.command()
@click.argument("sku")
@click.argument("quantity", type=int)
@click.option("--push", is_flag=True, help="Also push the new quantity to Tindie API.")
def main(sku: str, quantity: int, push: bool) -> None:
    """Set stock QUANTITY for product SKU.

    Example: update_stock.py EM-1001 10 --push
    """
    inventory = Inventory.load(PRODUCTS_DIR)
    product = inventory.get(sku)

    if product is None:
        console.print(f"[red]Error:[/] No product found with SKU '{sku}'")
        sys.exit(1)

    old_qty = product.stock
    product.stock = quantity

    yaml_path = PRODUCTS_DIR / f"{sku}.yaml"
    product.to_yaml(yaml_path)
    console.print(f"[green]✓[/] Updated [cyan]{sku}[/] stock: {old_qty} → {quantity}")

    if push:
        if not product.tindie_product_id:
            console.print("[yellow]Warning:[/] tindie_product_id not set — skipping API push.")
            return
        try:
            api = TindieAPI()
            api.update_stock(product.tindie_product_id, quantity)
            console.print(f"[green]✓[/] Pushed stock update to Tindie for product {product.tindie_product_id}")
        except TindieAPIError as exc:
            console.print(f"[red]Tindie API error:[/] {exc}")
            sys.exit(1)


if __name__ == "__main__":
    main()
