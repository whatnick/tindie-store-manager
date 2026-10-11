#!/usr/bin/env python3
"""Pause Google Ads ad groups whose Elecrow products are unavailable."""

import os
import shutil
import subprocess
from pathlib import Path

import click
import requests
from dotenv import load_dotenv
from playwright.sync_api import Page, sync_playwright
from rich.console import Console

ROOT = Path(__file__).resolve().parents[1]
AD_GROUPS = {
    "https://www.elecrow.com/mcp39f521-breakout.html": (
        "MCP39F521 Breakout",
        "GOOGLE_ADS_ELECROW_MCP39F521_AD_GROUP_ID",
    ),
    "https://www.elecrow.com/v9360-breakout-board.html": (
        "V9360 Breakout",
        "GOOGLE_ADS_ELECROW_V9360_AD_GROUP_ID",
    ),
}
console = Console()


def gcloud_command() -> str:
    command = shutil.which("gcloud")
    if command:
        return command
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidate = (
            Path(local_app_data)
            / "Google"
            / "Cloud SDK"
            / "google-cloud-sdk"
            / "bin"
            / "gcloud.cmd"
        )
        if candidate.exists():
            return str(candidate)
    raise RuntimeError("gcloud is not installed or could not be located.")


def access_token() -> str:
    result = subprocess.run(
        [gcloud_command(), "auth", "application-default", "print-access-token"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def product_available(page: Page, url: str) -> tuple[bool, str]:
    response = page.goto(url, wait_until="domcontentloaded", timeout=60_000)
    if response is None or not response.ok:
        status = "no response" if response is None else f"HTTP {response.status}"
        return False, status

    page.wait_for_timeout(1_000)
    stock = page.locator(".product-info-main .stock.available")
    add_to_cart = page.locator("#product-addtocart-button")
    if (
        stock.count() == 1
        and "in stock" in stock.inner_text().lower()
        and add_to_cart.count() == 1
        and add_to_cart.is_visible()
        and add_to_cart.is_enabled()
    ):
        return True, "in stock"
    return False, "product page is not purchasable"


def pause_ad_groups(customer_id: str, ad_group_ids: list[str]) -> None:
    operations = [
        {
            "update": {
                "resourceName": f"customers/{customer_id}/adGroups/{ad_group_id}",
                "status": "PAUSED",
            },
            "updateMask": "status",
        }
        for ad_group_id in ad_group_ids
    ]
    response = requests.post(
        f"https://googleads.googleapis.com/v25/customers/{customer_id}/adGroups:mutate",
        headers={"Authorization": f"Bearer {access_token()}"},
        json={
            "customerId": customer_id,
            "operations": operations,
            "partialFailure": False,
            "responseContentType": "MUTABLE_RESOURCE",
        },
        timeout=30,
    )
    response.raise_for_status()


@click.command()
@click.option("--dry-run", is_flag=True, help="Report pauses without changing Google Ads.")
def main(dry_run: bool) -> None:
    """Enforce the public Elecrow stock gate for the active Search campaign."""
    load_dotenv(ROOT / ".env")
    customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
    configured_ad_groups = {
        url: (name, os.environ.get(variable))
        for url, (name, variable) in AD_GROUPS.items()
    }
    missing = [
        variable
        for _, (_, variable) in AD_GROUPS.items()
        if not os.environ.get(variable)
    ]
    if not customer_id:
        missing.append("GOOGLE_ADS_CUSTOMER_ID")
    if missing:
        raise click.UsageError(f"Set {', '.join(missing)} in .env.")

    pauses: list[tuple[str, str, str]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            for url, (name, ad_group_id) in configured_ad_groups.items():
                assert ad_group_id is not None
                available, reason = product_available(page, url)
                if not available:
                    pauses.append((name, ad_group_id, reason))
        finally:
            browser.close()

    if not pauses:
        console.print("[green]OK[/] All advertised Elecrow products are purchasable.")
        return

    for name, _, reason in pauses:
        console.print(f"[yellow]Pause required:[/] {name} ({reason})")
    if dry_run:
        console.print("[dim]Dry run: Google Ads was not changed.[/]")
        return

    pause_ad_groups(customer_id, [ad_group_id for _, ad_group_id, _ in pauses])
    console.print(f"[green]Paused {len(pauses)} unavailable ad group(s).[/]")


if __name__ == "__main__":
    main()
