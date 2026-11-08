#!/usr/bin/env python3
"""Validate and summarize lifecycle evidence for every product YAML."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_DIR = ROOT / "products"

DECISIONS = {
    "Invest",
    "Sustain",
    "Revise",
    "Consolidate",
    "Retirement candidate",
    "Retired",
}
CONFIDENCE = {"High", "Medium", "Low"}


def load_products() -> list[tuple[Path, dict]]:
    return [
        (path, yaml.safe_load(path.read_text(encoding="utf-8")))
        for path in sorted(PRODUCTS_DIR.glob("*.yaml"))
    ]


def validate(path: Path, product: dict) -> list[str]:
    errors: list[str] = []
    lifecycle = product.get("lifecycle") or {}
    business_case = product.get("business_case") or {}
    sales = business_case.get("tindie_sales") or {}

    required_lifecycle = ("stage", "product_line", "interest_area", "channel", "review_date")
    for field in required_lifecycle:
        if not lifecycle.get(field):
            errors.append(f"{path.name}: lifecycle.{field} is required")
    if business_case.get("decision") not in DECISIONS:
        errors.append(f"{path.name}: invalid business_case.decision")
    if business_case.get("confidence") not in CONFIDENCE:
        errors.append(f"{path.name}: invalid business_case.confidence")
    if business_case.get("approval_state") not in {"Proposed", "Approved"}:
        errors.append(f"{path.name}: invalid business_case.approval_state")
    if not business_case.get("analysis_url"):
        errors.append(f"{path.name}: business_case.analysis_url is required")
    for field in ("lifetime_units", "lifetime_orders"):
        if not isinstance(sales.get(field), int) or sales[field] < 0:
            errors.append(f"{path.name}: tindie_sales.{field} must be a non-negative integer")
    if (
        business_case.get("decision") == "Retirement candidate"
        and business_case.get("approval_state") != "Proposed"
    ):
        errors.append(f"{path.name}: retirement candidates must remain Proposed")
    if (
        business_case.get("decision") == "Retired"
        and product.get("listing_state") != "retired"
    ):
        errors.append(f"{path.name}: retired decisions require listing_state: retired")
    return errors


def markdown(products: list[tuple[Path, dict]]) -> str:
    lines = [
        "| SKU | Stage | Decision | Approval | Confidence | Stock | Lifetime units | Last sale |",
        "| --- | --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for _, product in products:
        lifecycle = product["lifecycle"]
        business_case = product["business_case"]
        sales = business_case["tindie_sales"]
        lines.append(
            "| {sku} | {stage} | {decision} | {approval} | {confidence} | {stock} | "
            "{units} | {last_sale} |".format(
                sku=product["sku"],
                stage=lifecycle["stage"],
                decision=business_case["decision"],
                approval=business_case["approval_state"],
                confidence=business_case["confidence"],
                stock=product.get("stock", 0),
                units=sales["lifetime_units"],
                last_sale=sales.get("last_sale") or "Never",
            )
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if lifecycle evidence is incomplete")
    args = parser.parse_args()

    products = load_products()
    errors = [
        error
        for path, product in products
        for error in validate(path, product)
    ]
    if errors:
        for error in errors:
            print(error)
        return 1

    decisions = Counter(product["business_case"]["decision"] for _, product in products)
    print(markdown(products))
    print()
    print("Decision counts:", ", ".join(f"{key}={value}" for key, value in sorted(decisions.items())))
    if args.check:
        print(f"OK: {len(products)} product files have normalized lifecycle evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
