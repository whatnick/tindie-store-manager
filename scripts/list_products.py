#!/usr/bin/env python3
"""List all local products and (optionally) sync with live Tindie API data."""

import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich import box

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tindie_manager.product import Inventory
from tindie_manager.tindie_api import TindieAPI, TindieAPIError

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")
console = Console()
PRODUCTS_DIR = Path(__file__).resolve().parents[1] / "products"


@click.command()
@click.option("--live", is_flag=True, help="Fetch live stock from Tindie API instead of local files.")
@click.option("--all", "show_all", is_flag=True, help="Include inactive products.")
def main(live: bool, show_all: bool) -> None:
    inventory = Inventory.load(PRODUCTS_DIR)
    products = inventory.products if show_all else [p for p in inventory.products if p.active]

    live_stock: dict[str, int] = {}
    if live:
        try:
            api = TindieAPI()
            for item in api.get_inventory():
                pid = item.get("product", {}).get("key", "")
                live_stock[pid] = item.get("quantity", 0)
            console.print("[dim]Stock sourced from Tindie API[/]\n")
        except TindieAPIError as exc:
            console.print(f"[red]API error:[/] {exc} — showing local data\n")

    store = os.environ.get("TINDIE_USERNAME", "Tindie")
    table = Table(title=f"{store} Tindie Products", box=box.ROUNDED, highlight=True)
    table.add_column("SKU", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Price", justify="right")
    table.add_column("Stock", justify="right")
    table.add_column("Tindie ID", style="dim")
    table.add_column("Active")

    for p in products:
        stock_val = live_stock.get(p.tindie_product_id or "", p.stock) if live else p.stock
        table.add_row(
            p.sku,
            p.name,
            f"${p.price_usd:.2f}",
            str(stock_val),
            p.tindie_product_id or "—",
            "✓" if p.active else "✗",
        )

    console.print(table)


if __name__ == "__main__":
    main()
