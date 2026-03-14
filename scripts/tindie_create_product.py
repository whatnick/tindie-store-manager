#!/usr/bin/env python3
"""
tindie_create_product.py — Generic Playwright script to list any product on Tindie.

Usage:
    uv run scripts/tindie_create_product.py <SKU>
    uv run scripts/tindie_create_product.py V9381-BREAKOUT
    uv run scripts/tindie_create_product.py V9381-BREAKOUT --headless
    uv run scripts/tindie_create_product.py V9381-BREAKOUT --dry-run

Credentials are read from .env (TINDIE_USERNAME, TINDIE_PASSWORD).

After a successful submission the script:
  - Extracts the Tindie product ID from the redirect URL
  - Writes it back into the product YAML file automatically
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import click
import yaml
from dotenv import load_dotenv
from playwright.sync_api import Page, sync_playwright

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_DIR = ROOT / "products"

# ---------------------------------------------------------------------------
# Tindie category slug → Tindie form <option> value mapping
# (visible at /products/create/ category <select>; "iot-home" is the closest
#  match for energy monitors; update if Tindie changes their taxonomy)
# ---------------------------------------------------------------------------
CATEGORY_MAP: dict[str, str] = {
    "Energy Monitor": "iot-home",
    "IoT": "iot-home",
    "Breakout": "breakout-boards",
    "Other": "other",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_yaml(sku: str) -> Path:
    """Locate a product YAML by SKU (case-insensitive match on the sku field)."""
    for path in PRODUCTS_DIR.glob("*.yaml"):
        data = yaml.safe_load(path.read_text())
        if str(data.get("sku", "")).upper() == sku.upper():
            return path
    # Fallback: try slug directly
    slug = sku.lower()
    direct = PRODUCTS_DIR / f"{slug}.yaml"
    if direct.exists():
        return direct
    raise FileNotFoundError(f"No product YAML found for SKU '{sku}'")


def load_product(yaml_path: Path) -> dict:
    return yaml.safe_load(yaml_path.read_text())


def write_tindie_id(yaml_path: Path, tindie_id: str) -> None:
    content = yaml_path.read_text()
    updated = re.sub(
        r"^tindie_product_id:.*$",
        f'tindie_product_id: "{tindie_id}"',
        content,
        flags=re.MULTILINE,
    )
    yaml_path.write_text(updated)
    click.echo(f"  ✓ Updated {yaml_path.name} with tindie_product_id: {tindie_id}")


def tindie_category(product: dict) -> str:
    cat = product.get("category", "")
    return CATEGORY_MAP.get(cat, "iot-home")


def build_description(product: dict) -> str:
    """Return the plain-text description, appending spec table if specs exist."""
    desc = product.get("description", "").strip()
    specs = product.get("specs", {})
    extra = specs.get("extra", {}) or {}
    lines = []
    if specs.get("voltage_range"):
        lines.append(f"- Supply voltage: {specs['voltage_range']}")
    if specs.get("current_range"):
        lines.append(f"- Current range: {specs['current_range']}")
    if specs.get("accuracy"):
        lines.append(f"- Accuracy: {specs['accuracy']}")
    if specs.get("interfaces"):
        lines.append(f"- Interfaces: {', '.join(specs['interfaces'])}")
    if specs.get("connectivity"):
        lines.append(f"- Connectivity: {', '.join(specs['connectivity'])}")
    if specs.get("dimensions_mm"):
        lines.append(f"- PCB size: {specs['dimensions_mm']} mm")
    for k, v in extra.items():
        lines.append(f"- {k.replace('_', ' ').title()}: {v}")
    if lines:
        desc += "\n\n## Technical Specifications\n" + "\n".join(lines)
    return desc


# ---------------------------------------------------------------------------
# Playwright form-filling
# ---------------------------------------------------------------------------

def login(page: Page, username: str, password: str) -> None:
    click.echo("  Navigating to login page…")
    page.goto("https://www.tindie.com/accounts/login/")
    page.wait_for_load_state("networkidle")
    page.fill('input[name="login"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    try:
        page.wait_for_url(re.compile(r"/dashboard/|/stores/"), timeout=20_000)
        click.echo("  Logged in ✓")
    except Exception:
        raise RuntimeError(
            "Login failed or unexpected redirect. Check TINDIE_USERNAME / TINDIE_PASSWORD."
        )


def fill_field(page: Page, selectors: list[str], value: str, label: str) -> bool:
    """Try each selector in order; fill the first one found. Returns True on success."""
    for sel in selectors:
        loc = page.locator(sel)
        if loc.count() > 0:
            loc.first.fill(value)
            click.echo(f"  {label} ✓")
            return True
    click.echo(f"  ⚠  {label}: no matching field found — fill manually")
    return False


def check_box(page: Page, selectors: list[str], label: str) -> bool:
    for sel in selectors:
        loc = page.locator(sel)
        if loc.count() > 0:
            if not loc.first.is_checked():
                loc.first.check()
            click.echo(f"  {label} ✓")
            return True
    click.echo(f"  ⚠  {label}: checkbox not found")
    return False


def fill_description(page: Page, text: str) -> None:
    """Handle plain textarea, contenteditable div, or iframe-based rich text editors."""
    # 1. Plain textarea
    ta = page.locator("textarea[name='description'], textarea[id*='description']")
    if ta.count():
        ta.first.fill(text)
        click.echo("  Description (textarea) ✓")
        return

    # 2. Contenteditable div (Quill, Draft.js, etc.)
    ce = page.locator("div[contenteditable='true']")
    if ce.count():
        ce.first.click()
        ce.first.fill(text)
        click.echo("  Description (contenteditable) ✓")
        return

    # 3. TinyMCE / CKEditor iframe
    frames = page.frames
    for frame in frames:
        try:
            body = frame.locator("body[contenteditable='true'], body")
            if body.count():
                body.first.click()
                page.keyboard.press("Control+a")
                page.keyboard.type(text)
                click.echo("  Description (editor iframe) ✓")
                return
        except Exception:
            continue

    click.echo("  ⚠  Description: could not fill automatically — paste manually")


def enter_tags(page: Page, tags: list[str]) -> None:
    """Try common tag-input patterns (plain input, Tagify, Select2)."""
    tag_input = page.locator(
        "input[name*='tag'], input[id*='tag'], input[placeholder*='tag' i]"
    )
    if tag_input.count():
        for tag in tags:
            tag_input.first.fill(tag)
            page.keyboard.press("Enter")
            page.wait_for_timeout(300)
        click.echo(f"  Tags ({len(tags)}) ✓")
    else:
        click.echo(f"  ⚠  Tag input not found — add manually: {', '.join(tags)}")


def select_category(page: Page, value: str) -> None:
    sel = page.locator("select[name='category'], select[id*='category']")
    if sel.count():
        try:
            sel.first.select_option(value=value)
            click.echo(f"  Category ({value}) ✓")
        except Exception:
            click.echo(f"  ⚠  Category '{value}' not found in dropdown — select manually")
    else:
        click.echo("  ⚠  Category dropdown not found — select manually")


def fill_form(page: Page, product: dict) -> None:
    page.wait_for_load_state("networkidle")

    # Title
    fill_field(
        page,
        ["input[name='title']", "input[id*='title']", "input[placeholder*='name' i]"],
        product["name"],
        "Title",
    )

    # Category
    select_category(page, tindie_category(product))

    # Price
    fill_field(
        page,
        ["input[name='unit_price']", "input[id*='price']", "input[placeholder*='price' i]"],
        str(product["price_usd"]),
        "Price",
    )

    # Quantity
    fill_field(
        page,
        ["input[name='quantity']", "input[id*='quantity']", "input[id*='stock']"],
        str(product.get("stock", 0)),
        "Quantity",
    )

    # Description
    fill_description(page, build_description(product))

    # Open hardware
    if any(t in product.get("tags", []) for t in ["open-hardware", "open-source"]):
        check_box(
            page,
            ["input[name='open_hardware']", "input[id*='open_hardware']"],
            "Open hardware",
        )
        check_box(
            page,
            ["input[name='open_code']", "input[id*='open_code']"],
            "Open source",
        )

    # Tags
    enter_tags(page, product.get("tags", []))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.command()
@click.argument("sku")
@click.option("--headless", is_flag=True, default=False, help="Run browser in headless mode.")
@click.option("--dry-run", is_flag=True, default=False, help="Fill form but do not submit.")
def main(sku: str, headless: bool, dry_run: bool) -> None:
    """List a product on Tindie by SKU.

    Reads credentials from .env (TINDIE_USERNAME, TINDIE_PASSWORD).
    After successful submission, updates tindie_product_id in the YAML file.
    """
    import os

    username = os.environ.get("TINDIE_USERNAME")
    password = os.environ.get("TINDIE_PASSWORD")
    if not username or not password:
        raise click.UsageError(
            "Set TINDIE_USERNAME and TINDIE_PASSWORD in your .env file."
        )

    # Load product
    try:
        yaml_path = find_yaml(sku)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))

    product = load_product(yaml_path)
    click.echo(f"\nProduct : {product['name']}")
    click.echo(f"Price   : ${product['price_usd']:.2f}")
    click.echo(f"Stock   : {product.get('stock', 0)}")
    click.echo(f"YAML    : {yaml_path.name}")

    if product.get("tindie_product_id"):
        click.echo(
            f"\n⚠  Already has tindie_product_id={product['tindie_product_id']}. "
            "Continuing will create a duplicate listing."
        )
        if not click.confirm("Continue anyway?"):
            raise SystemExit(0)

    click.echo()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless, slow_mo=60)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        try:
            # Login
            login(page, username, password)

            # Navigate to create form
            click.echo("  Navigating to /products/create/ …")
            page.goto("https://www.tindie.com/products/create/")

            # Fill all fields
            click.echo("  Filling form fields…")
            fill_form(page, product)

            if dry_run:
                click.echo("\n[dry-run] Form filled — NOT submitting. Review the browser.")
                click.pause("  Press any key to close the browser…")
                browser.close()
                return

            # Pause for user to add images / review
            click.echo(
                "\n✅ Form filled. Add product images in the browser, then press ENTER to submit."
            )
            click.pause("  Press any key to submit…")

            # Submit
            submit = page.locator(
                "button[type='submit']:not([name='save_draft']), "
                "input[type='submit']"
            ).last
            submit.click()
            click.echo("  Submitting…")

            # Wait for redirect to the new product page
            page.wait_for_url(
                re.compile(r"/products/whatnick/[^/]+/"), timeout=30_000
            )
            new_url = page.url
            click.echo(f"\n🎉 Listed successfully!\n   {new_url}")

            # Extract product ID and update YAML
            id_match = re.search(r"/products/whatnick/[^/]+/(\d+)", new_url)
            if id_match:
                write_tindie_id(yaml_path, id_match.group(1))
            else:
                click.echo(
                    "  ⚠  Could not parse product ID from URL — update YAML manually."
                )

        except Exception as exc:
            click.echo(f"\n[error] {exc}", err=True)
            click.pause("  Press any key to close (browser stays open for inspection)…")
            raise SystemExit(1)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
