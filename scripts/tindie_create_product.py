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
import tempfile
import time
import urllib.request
from pathlib import Path

import click
import yaml
from dotenv import load_dotenv
from playwright.sync_api import Page, sync_playwright

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_DIR = ROOT / "products"

# ---------------------------------------------------------------------------
# Tindie category name → <option value> mapping (from /products/create/ form)
# ---------------------------------------------------------------------------
CATEGORY_MAP: dict[str, str] = {
    "Energy Monitor": "77",    # IoT & Smart Home
    "IoT": "77",               # IoT & Smart Home
    "Breakout": "65",          # DIY Electronics > Prototyping & Fabrication
    "Other": "69",             # DIY Electronics
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
    # Tindie allauth fields: name="auth-username" / name="auth-password"
    page.fill('input[name="auth-username"]', username)
    page.fill('input[name="auth-password"]', password)
    # Submit by pressing Enter on the password field
    page.press('input[name="auth-password"]', "Enter")
    try:
        page.wait_for_load_state("networkidle", timeout=20_000)
        click.echo("  Logged in ✓")
    except Exception:
        pass
    if "login" in page.url:
        raise RuntimeError(
            "Login failed — still on login page. Check TINDIE_USERNAME / TINDIE_PASSWORD."
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
    # 1. Plain textarea (Tindie uses name="description")
    ta = page.locator('textarea[name="description"], textarea[id="id_description"]')
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
    sel = page.locator('select[name="category"]')
    if sel.count():
        try:
            sel.first.select_option(value=value)
            click.echo(f"  Category ({value}) ✓")
        except Exception:
            click.echo(f"  ⚠  Category value '{value}' not found in dropdown — select manually")
    else:
        click.echo("  ⚠  Category dropdown not found — select manually")


def download_image(url: str) -> Path:
    """Download an image URL to a temp file and return its path."""
    suffix = Path(url.split("?")[0]).suffix or ".jpg"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    click.echo(f"  Downloading image from {url} …")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        tmp.write(resp.read())
    tmp.close()
    click.echo(f"  Image saved to {tmp.name}")
    return Path(tmp.name)


def upload_image(page: Page, image_path: Path) -> bool:
    """Upload an image via the qq-uploader file input on the Tindie create form."""
    selectors = [
        'input[name="qqfile"]',          # Tindie's FineUploader input
        "input[type='file'][accept*='image']",
        "input[type='file']",
    ]
    for sel in selectors:
        loc = page.locator(sel)
        if loc.count() > 0:
            loc.first.set_input_files(str(image_path))
            page.wait_for_timeout(2000)
            click.echo(f"  Image uploaded ({image_path.name}) ✓")
            return True
    click.echo("  ⚠  Image file input not found — upload manually in the browser")
    return False


def fill_form(page: Page, product: dict) -> None:
    # domcontentloaded is safer than networkidle — Tindie's create page
    # has persistent background requests that never fully settle.
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)  # let JS hydrate the form

    # Title  (name="title", max 50 chars)
    fill_field(page, ['input[name="title"]'], product["name"][:50], "Title")

    # Category (name="category", numeric option values)
    select_category(page, tindie_category(product))

    # Price  (name="unit_price")
    fill_field(page, ['input[name="unit_price"]'], str(product["price_usd"]), "Price")

    # Stock  (name="num_in_stock")
    fill_field(page, ['input[name="num_in_stock"]'], str(product.get("stock", 0)), "Quantity")

    # Model number / SKU
    fill_field(page, ['input[name="model_number"]'], product.get("sku", ""), "Model number")

    # Short description (140 char limit)
    short = (product.get("description", "") or "").replace("\n", " ").strip()[:140]
    fill_field(page, ['input[name="short_description"]'], short, "Short description")

    # Dimensions (width × height in mm → cm for Tindie)
    dims = (product.get("specs") or {}).get("dimensions_mm", "")
    if dims:
        try:
            parts = [p.strip() for p in str(dims).replace("×", "x").split("x")]
            if len(parts) >= 2:
                fill_field(page, ['input[name="width"]'],  f"{float(parts[0])/10:.2f}", "Width (cm)")
                fill_field(page, ['input[name="height"]'], f"{float(parts[1])/10:.2f}", "Height (cm)")
        except Exception:
            pass

    # Full description  (name="description", markdown textarea)
    fill_description(page, build_description(product))

    # Open-source / open-hardware URLs — read from YAML fields if present
    tags = product.get("tags", [])
    if "open-hardware" in tags or "open-source" in tags:
        design_url = product.get("design_url", "")
        code_url   = product.get("code_url", "")
        if design_url:
            fill_field(page, ['input[name="design_url"]'], design_url, "Design URL")
        if code_url:
            fill_field(page, ['input[name="code_url"]'],   code_url,   "Code URL")

    # YouTube URL — read from YAML if present
    youtube_url = product.get("youtube_url", "")
    if youtube_url:
        fill_field(page, ['input[name="youtube_url"]'], youtube_url, "YouTube URL")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.command()
@click.argument("sku")
@click.option("--headless", is_flag=True, default=False, help="Run browser in headless mode.")
@click.option("--dry-run", is_flag=True, default=False, help="Fill form but do not submit.")
@click.option(
    "--image",
    default=None,
    help="URL or local path to a product image to upload automatically.",
)
def main(sku: str, headless: bool, dry_run: bool, image: str | None) -> None:
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

    # Resolve image to a local path (download if URL)
    image_path: Path | None = None
    _tmp_image: Path | None = None
    if image:
        if image.startswith("http://") or image.startswith("https://"):
            image_path = download_image(image)
            _tmp_image = image_path
        else:
            image_path = Path(image)
            if not image_path.exists():
                raise click.ClickException(f"Image file not found: {image}")

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
    if image_path:
        click.echo(f"Image   : {image_path}")

    if product.get("tindie_product_id"):
        click.echo(
            f"\n⚠  Already has tindie_product_id={product['tindie_product_id']}. "
            "Continuing will create a duplicate listing."
        )
        if not click.confirm("Continue anyway?"):
            raise SystemExit(0)

    click.echo()

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=headless, slow_mo=60)
            context = browser.new_context(viewport={"width": 1280, "height": 900})
            page = context.new_page()

            try:
                # Login
                login(page, username, password)

                # Navigate to create form
                click.echo("  Navigating to /products/create/ …")
                page.goto("https://www.tindie.com/products/create/", wait_until="domcontentloaded")

                # Fill all fields
                click.echo("  Filling form fields…")
                fill_form(page, product)

                # Upload image if provided
                if image_path:
                    upload_image(page, image_path)

                if dry_run:
                    click.echo("\n[dry-run] Form filled — NOT submitting. Review the browser.")
                    click.pause("  Press any key to close the browser…")
                    browser.close()
                    return

                # Pause for user to add images / review (only if no image supplied)
                if not image_path:
                    click.echo(
                        "\n✅ Form filled. Add product images in the browser, then press ENTER to submit."
                    )
                    click.pause("  Press any key to submit…")
                else:
                    click.echo("\n✅ Form filled with image. Press ENTER to submit.")
                    click.pause("  Press any key to submit…")

                # Submit — use the exact Save button from the Tindie form
                submit = page.locator('input[name="submit"]#id_submit')
                submit.click()
                click.echo("  Submitting…")

                # Wait for navigation away from the create page (any redirect)
                try:
                    page.wait_for_url(
                        re.compile(r"/products/(?!create)"),
                        timeout=30_000,
                    )
                except Exception:
                    pass  # fall through — inspect whatever URL we landed on

                new_url = page.url
                click.echo(f"\n  Landed on: {new_url}")

                # Check for validation errors still on the create page
                if "/create/" in new_url or "/products/create" in new_url:
                    errors = page.locator(".errorlist, .alert-danger, .has-error").all_text_contents()
                    if errors:
                        click.echo(f"\n⚠  Form errors:\n" + "\n".join(errors))
                    raise RuntimeError(
                        "Still on create page after submit — check the browser for validation errors."
                    )

                click.echo(f"\n🎉 Listed successfully!\n   {new_url}")

                # Extract product ID from URL — works for any store slug
                id_match = re.search(r"/products/[^/]+/[^/]+/(\d+)", new_url)
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
    finally:
        # Clean up downloaded temp image
        if _tmp_image and _tmp_image.exists():
            _tmp_image.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
