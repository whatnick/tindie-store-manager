#!/usr/bin/env python3
"""Read live seller inventory and list products eligible for advertising."""

import json
import os
import re
from pathlib import Path

import click
from dotenv import load_dotenv
from playwright.sync_api import Page, sync_playwright
from rich.console import Console
from rich.table import Table

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_DIR = ROOT / "products"
console = Console()


def login(page: Page, username: str, password: str) -> None:
    page.goto("https://www.tindie.com/accounts/login/", wait_until="networkidle")
    page.fill('input[name="auth-username"]', username)
    page.fill('input[name="auth-password"]', password)
    page.press('input[name="auth-password"]', "Enter")
    page.wait_for_load_state("networkidle", timeout=30_000)
    if "login" in page.url:
        raise RuntimeError("Tindie login failed. Check TINDIE_USERNAME and TINDIE_PASSWORD.")


def scrape_inventory(page: Page) -> list[dict]:
    page.goto("https://www.tindie.com/products/mystore/", wait_until="networkidle")
    products: dict[str, dict] = {}

    for row in page.locator("table tbody tr").all():
        cells = [text.strip() for text in row.locator("td").all_text_contents()]
        if len(cells) < 7:
            continue
        product_id = cells[1].lstrip("#")
        if not product_id.isdigit() or product_id in products:
            continue
        name = cells[0].split("Shortlink:", 1)[0].strip()
        products[product_id] = {
            "product_id": product_id,
            "name": name,
            "stock": int(cells[3]),
            "status": cells[6],
            "url": f"https://www.tindie.com/products/{product_id}/",
        }

    return list(products.values())


def local_product_paths() -> dict[str, Path]:
    paths: dict[str, Path] = {}
    pattern = re.compile(r'(?m)^tindie_product_id:\s*["\']?(\d+)["\']?\s*$')
    for path in PRODUCTS_DIR.glob("*.yaml"):
        match = pattern.search(path.read_text(encoding="utf-8"))
        if match:
            paths[match.group(1)] = path
    return paths


def sync_local_stock(products: list[dict]) -> int:
    paths = local_product_paths()
    updated = 0
    for product in products:
        path = paths.get(product["product_id"])
        if path is None:
            continue
        content = path.read_text(encoding="utf-8")
        replacement = f"stock: {product['stock']}"
        revised, count = re.subn(r"(?m)^stock:.*$", replacement, content, count=1)
        if count and revised != content:
            path.write_text(revised, encoding="utf-8")
            updated += 1
    return updated


@click.command()
@click.option("--sync", is_flag=True, help="Update local YAML stock from live Tindie values.")
@click.option("--json-output", type=click.Path(path_type=Path), help="Write live inventory JSON.")
@click.option("--headful", is_flag=True, help="Show the browser window.")
def main(sync: bool, json_output: Path | None, headful: bool) -> None:
    """List only products that are live, for sale, and currently in stock."""
    load_dotenv(ROOT / ".env")
    username = os.environ.get("TINDIE_USERNAME")
    password = os.environ.get("TINDIE_PASSWORD")
    if not username or not password:
        raise click.UsageError("Set TINDIE_USERNAME and TINDIE_PASSWORD in .env.")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not headful)
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            login(page, username, password)
            products = scrape_inventory(page)
        finally:
            browser.close()

    for product in products:
        product["eligible_for_ads"] = (
            product["status"] == "For Sale" and product["stock"] > 0
        )

    if sync:
        console.print(f"[green]Updated {sync_local_stock(products)} local stock record(s).[/]")

    if json_output:
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(json.dumps(products, indent=2) + "\n", encoding="utf-8")

    eligible = [product for product in products if product["eligible_for_ads"]]
    table = Table(title="Tindie products eligible for Google Ads")
    table.add_column("ID", style="cyan")
    table.add_column("Product")
    table.add_column("Stock", justify="right")
    table.add_column("Status")
    for product in eligible:
        table.add_row(
            product["product_id"],
            product["name"],
            str(product["stock"]),
            product["status"],
        )
    console.print(table)
    console.print(
        f"[bold]{len(eligible)}[/] of {len(products)} live seller listings are ad eligible."
    )


if __name__ == "__main__":
    main()
