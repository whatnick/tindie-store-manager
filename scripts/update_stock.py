#!/usr/bin/env python3
"""Update the local stock value for a product."""

import re
import sys
from pathlib import Path

import click
from rich.console import Console

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tindie_manager.product import Inventory
console = Console()
PRODUCTS_DIR = Path(__file__).resolve().parents[1] / "products"


@click.command()
@click.argument("sku")
@click.argument("quantity", type=int)
def main(sku: str, quantity: int) -> None:
    """Set stock QUANTITY for product SKU.

    Tindie V2 API keys cannot update inventory; use the seller UI for live stock.
    """
    inventory = Inventory.load(PRODUCTS_DIR)
    product = inventory.get(sku)

    if product is None:
        console.print(f"[red]Error:[/] No product found with SKU '{sku}'")
        sys.exit(1)

    old_qty = product.stock
    yaml_path = next(
        (
            path
            for path in PRODUCTS_DIR.glob("*.yaml")
            if re.search(
                rf'(?mi)^sku:\s*["\']?{re.escape(product.sku)}["\']?\s*$',
                path.read_text(),
            )
        ),
        None,
    )
    if yaml_path is None:
        raise click.ClickException(f"No YAML file found for SKU '{product.sku}'")
    content = re.sub(r"(?m)^stock:.*$", f"stock: {quantity}", yaml_path.read_text())
    yaml_path.write_text(content)
    console.print(f"[green]OK[/] Updated [cyan]{sku}[/] stock: {old_qty} -> {quantity}")

if __name__ == "__main__":
    main()
