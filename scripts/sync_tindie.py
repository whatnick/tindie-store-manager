#!/usr/bin/env python3
"""Pull live inventory from Tindie and update local YAML files."""

import re
import sys
from pathlib import Path

import click
from rich.console import Console

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tindie_manager.product import Inventory
from tindie_manager.tindie_api import TindieAPI, TindieAPIError

console = Console()
PRODUCTS_DIR = Path(__file__).resolve().parents[1] / "products"


def product_path(sku: str) -> Path:
    for path in PRODUCTS_DIR.glob("*.yaml"):
        if re.search(
            rf'(?mi)^sku:\s*["\']?{re.escape(sku)}["\']?\s*$',
            path.read_text(),
        ):
            return path
    raise FileNotFoundError(f"No YAML file found for SKU '{sku}'")


def update_yaml(path: Path, *, stock: int | None = None, tindie_id: str | None = None) -> None:
    content = path.read_text()
    if stock is not None:
        content = re.sub(r"(?m)^stock:.*$", f"stock: {stock}", content)
    if tindie_id is not None:
        content = re.sub(
            r"(?m)^tindie_product_id:.*$",
            f'tindie_product_id: "{tindie_id}"',
            content,
        )
    path.write_text(content)


@click.command()
@click.option("--dry-run", is_flag=True, help="Show what would change without writing files.")
def main(dry_run: bool) -> None:
    """Pull stock from Tindie API and update local product YAML files."""
    inventory = Inventory.load(PRODUCTS_DIR)

    try:
        api = TindieAPI()
        reference_id = next(
            (
                product.tindie_product_id
                for product in inventory.products
                if product.tindie_product_id
            ),
            None,
        )
        live_items = api.get_inventory(reference_product_id=reference_id)
    except TindieAPIError as exc:
        from rich.markup import escape
        console.print(f"[red]API error:[/] {escape(str(exc))}")
        sys.exit(1)

    live_by_id = {str(item.get("id", "")): item for item in live_items}
    live_by_name = {
        str(item.get("title", "")).casefold(): item
        for item in live_items
        if item.get("title")
    }

    updated = 0
    for product in inventory.products:
        if not product.tindie_product_id:
            match = live_by_name.get(product.name.casefold())
            if match:
                new_id = str(match["id"])
                console.print(
                    f"[cyan]{product.sku}[/] Tindie ID: unset -> {new_id}"
                    + (" [dim](dry run)[/]" if dry_run else "")
                )
                if not dry_run:
                    update_yaml(product_path(product.sku), tindie_id=new_id)
                    product.tindie_product_id = new_id
                updated += 1

        live_item = live_by_id.get(product.tindie_product_id or "")
        if live_item is None:
            continue
        live_qty = int(live_item.get("num_in_stock") or 0)
        if product.stock != live_qty:
            console.print(
                f"[cyan]{product.sku}[/] stock: {product.stock} -> {live_qty}"
                + (" [dim](dry run)[/]" if dry_run else "")
            )
            if not dry_run:
                update_yaml(product_path(product.sku), stock=live_qty)
            updated += 1

    if updated == 0:
        console.print("[green]OK[/] All local stocks are in sync with Tindie.")
    elif not dry_run:
        console.print(f"[green]OK[/] Updated {updated} product(s).")


if __name__ == "__main__":
    main()
