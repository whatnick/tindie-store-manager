#!/usr/bin/env python3
"""Pause Google Ads ad groups whose Tindie products are no longer for sale."""

import os
import shutil
import subprocess
from pathlib import Path

import click
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from rich.console import Console

from tindie_ad_inventory import login, scrape_inventory

ROOT = Path(__file__).resolve().parents[1]
AD_GROUPS = {
    "19008": ("CS5490 Breakout", "GOOGLE_ADS_TINDIE_CS5490_AD_GROUP_ID"),
    "44002": ("Gamepad PMOD", "GOOGLE_ADS_TINDIE_GAMEPAD_AD_GROUP_ID"),
    "41553": ("V9381 Breakout", "GOOGLE_ADS_TINDIE_V9381_AD_GROUP_ID"),
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
    """Enforce the live Tindie stock gate for the active Search campaign."""
    load_dotenv(ROOT / ".env")
    customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID")
    username = os.environ.get("TINDIE_USERNAME")
    password = os.environ.get("TINDIE_PASSWORD")
    configured_ad_groups = {
        product_id: (name, os.environ.get(variable))
        for product_id, (name, variable) in AD_GROUPS.items()
    }
    missing = [
        variable
        for _, (_, variable) in AD_GROUPS.items()
        if not os.environ.get(variable)
    ]
    if not customer_id:
        missing.append("GOOGLE_ADS_CUSTOMER_ID")
    if not username:
        missing.append("TINDIE_USERNAME")
    if not password:
        missing.append("TINDIE_PASSWORD")
    if missing:
        raise click.UsageError(f"Set {', '.join(missing)} in .env.")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            login(page, username, password)
            inventory = {
                product["product_id"]: product for product in scrape_inventory(page)
            }
        finally:
            browser.close()

    pauses: list[tuple[str, str, str]] = []
    for product_id, (name, ad_group_id) in configured_ad_groups.items():
        assert ad_group_id is not None
        product = inventory.get(product_id)
        eligible = (
            product is not None
            and product["status"] == "For Sale"
            and product["stock"] > 0
        )
        if not eligible:
            reason = (
                "missing from seller inventory"
                if product is None
                else f"{product['status']}, stock {product['stock']}"
            )
            pauses.append((name, ad_group_id, reason))

    if not pauses:
        console.print("[green]OK[/] All advertised products are live and in stock.")
        return

    for name, _, reason in pauses:
        console.print(f"[yellow]Pause required:[/] {name} ({reason})")
    if dry_run:
        console.print("[dim]Dry run: Google Ads was not changed.[/]")
        return

    pause_ad_groups(customer_id, [ad_group_id for _, ad_group_id, _ in pauses])
    console.print(f"[green]Paused {len(pauses)} out-of-stock ad group(s).[/]")


if __name__ == "__main__":
    main()
