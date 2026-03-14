#!/usr/bin/env python3
"""Pull live inventory from Tindie and update local YAML files."""

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
@click.option("--dry-run", is_flag=True, help="Show what would change without writing files.")
def main(dry_run: bool) -> None:
    """Pull stock from Tindie API and update local product YAML files."""
    inventory = Inventory.load(PRODUCTS_DIR)

    try:
        api = TindieAPI()
        live_items = api.get_inventory()
    except TindieAPIError as exc:
        console.print(f"[red]API error:[/] {exc}")
        sys.exit(1)

    # Build a map from tindie_product_id → quantity
    live_map: dict[str, int] = {}
    for item in live_items:
        pid = str(item.get("product", {}).get("pk", ""))
        live_map[pid] = item.get("quantity", 0)

    updated = 0
    for product in inventory.products:
        if not product.tindie_product_id:
            continue
        live_qty = live_map.get(product.tindie_product_id)
        if live_qty is None:
            continue
        if product.stock != live_qty:
            console.print(
                f"[cyan]{product.sku}[/] stock: {product.stock} → {live_qty}"
                + (" [dim](dry run)[/]" if dry_run else "")
            )
            if not dry_run:
                product.stock = live_qty
                yaml_path = PRODUCTS_DIR / f"{product.sku}.yaml"
                product.to_yaml(yaml_path)
            updated += 1

    if updated == 0:
        console.print("[green]✓[/] All local stocks are in sync with Tindie.")
    elif not dry_run:
        console.print(f"[green]✓[/] Updated {updated} product(s).")


if __name__ == "__main__":
    main()
