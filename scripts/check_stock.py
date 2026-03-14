#!/usr/bin/env python3
"""Print an inventory summary and highlight low/out-of-stock products."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich import box

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tindie_manager.product import Inventory

console = Console()
PRODUCTS_DIR = Path(__file__).resolve().parents[1] / "products"


@click.command()
@click.option("--threshold", "-t", default=5, show_default=True,
              help="Stock level considered 'low'.")
@click.option("--low-only", is_flag=True, help="Show only low/out-of-stock items.")
def main(threshold: int, low_only: bool) -> None:
    inventory = Inventory.load(PRODUCTS_DIR)

    summary = inventory.summary()
    console.rule("[bold blue]whatnick Tindie Inventory")
    console.print(f"  Total products : [cyan]{summary['total_products']}[/]")
    console.print(f"  Active         : [cyan]{summary['active']}[/]")
    console.print(f"  Out of stock   : [red]{summary['out_of_stock']}[/]")
    console.print(f"  Low stock (≤{threshold}): [yellow]{summary['low_stock']}[/]")
    console.print(f"  Stock value    : [green]${summary['total_stock_value_usd']:,.2f}[/]")
    console.print()

    products = inventory.low_stock(threshold) if low_only else [
        p for p in inventory.products if p.active
    ]

    table = Table(box=box.ROUNDED, highlight=True)
    table.add_column("SKU", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Price", justify="right")
    table.add_column("Stock", justify="right")
    table.add_column("Status")

    for p in products:
        if p.stock == 0:
            status = "[red]OUT[/]"
        elif p.stock <= threshold:
            status = "[yellow]LOW[/]"
        else:
            status = "[green]OK[/]"
        table.add_row(p.sku, p.name, f"${p.price_usd:.2f}", str(p.stock), status)

    console.print(table)


if __name__ == "__main__":
    main()
