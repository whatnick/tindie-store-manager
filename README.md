# tindie-store-manager

A Git-based tool for managing your [Tindie](https://www.tindie.com) store: product descriptions, stock levels, and automated listing via browser automation.

> **Real-world example:** The `products/` directory in this repo contains the actual listings for the [whatnick](https://www.tindie.com/stores/whatnick/) energy monitor store — use them as reference when writing your own YAMLs.

## Features

- **Product-as-code** — one YAML file per product, version-controlled
- **Inventory CLI** — check stock, highlight low/out-of-stock items
- **Tindie V2 API client** — read the complete store catalog, prices, and stock
- **Playwright automation** — create draft listings, upload images, and add product options
- **Generic** — works for any Tindie store; configure via `.env`

## Requirements

- Python ≥ 3.11
- [uv](https://docs.astral.sh/uv/) (fast Python package manager)
- A Tindie seller account

## Setup

```bash
git clone https://github.com/whatnick/tindie-store-manager
cd tindie-store-manager

# Install dependencies (creates .venv automatically)
uv sync

# Install Playwright browser (needed for tindie_create_product.py)
uv run playwright install chromium

# Configure credentials
cp .env.example .env
# Edit .env — set TINDIE_USERNAME, TINDIE_PASSWORD, TINDIE_API_KEY
```

## Project structure

```
tindie-store-manager/
├── products/            # One YAML file per product (<slug>.yaml)
├── tindie_manager/
│   ├── product.py       # Product & Inventory dataclasses (YAML ↔ Python)
│   └── tindie_api.py    # Tindie REST API client
├── scripts/
│   ├── check_stock.py          # Inventory summary with low-stock alerts
│   ├── list_products.py        # List products (local or live from API)
│   ├── update_stock.py         # Set stock for a product
│   ├── sync_tindie.py          # Pull Tindie order data → update local YAMLs
│   └── tindie_create_product.py  # Browser-automate the Tindie create form
├── data/                # Generated exports / snapshots (gitignored)
├── .env.example         # Credential template
└── pyproject.toml       # uv project config
```

## Product YAML format

Each product lives in `products/<slug>.yaml`. Minimal example:

```yaml
sku: "MY-WIDGET-V1"
name: "My Widget v1"
description: |
  A short paragraph describing what the product does.
price_usd: 25.00
stock: 10
category: "Energy Monitor"
tags:
  - open-hardware
  - open-source
tindie_product_id: null   # filled in automatically after listing
active: true

# Optional — used by tindie_create_product.py
design_url: "https://github.com/you/widget-pcb"
code_url:   "https://github.com/you/widget-firmware"
youtube_url: "https://www.youtube.com/watch?v=..."
docs_url: "https://example.com/docs"
seller_manufactured: true
listing_state: "draft"
ships_from: "Adelaide, South Australia, Australia"
shipping:
  domestic:
    destination: "Australia"
    carrier: "Australia Post"
    service: "Tracked Parcel"
    amount_aud: 20.00
    tindie_amount_usd: 14.25

options:
  - label: "Firmware"
    help_text: "Choose the firmware installed before shipping."
    required: true
    choices:
      - label: "Pre-loaded"
        price_adjustment_usd: 0
        sku: "MY-WIDGET-V1-FW"
        default: true
      - label: "Unloaded"
        price_adjustment_usd: 0
        sku: "MY-WIDGET-V1-BLANK"
        default: false

specs:
  voltage_range: "3.3–5 V"
  interfaces:
    - "UART"
  dimensions_mm: "38.1 × 27.9"
  extra:
    chip: "MyChip XYZ"
images: []
image_glob: "my-widget-*.jpg"  # resolved only when --image-dir is supplied
```

See the `products/` directory for real-world examples.

## Scripts

```bash
# Inventory summary
uv run scripts/check_stock.py
uv run scripts/check_stock.py --low-only --threshold 3

# List products
uv run scripts/list_products.py
uv run scripts/list_products.py --live      # merge live Tindie API stock

# Update stock
uv run scripts/update_stock.py MY-WIDGET-V1 10

# Sync product IDs and stock from the Tindie V2 catalog
uv run scripts/sync_tindie.py
uv run scripts/sync_tindie.py --dry-run

# Create a new Tindie listing via browser automation
uv run scripts/tindie_create_product.py MY-WIDGET-V1
uv run scripts/tindie_create_product.py MY-WIDGET-V1 --image photo-1.jpg --image photo-2.jpg
uv run scripts/tindie_create_product.py MY-WIDGET-V1 --image-dir C:\path\to\photos
uv run scripts/tindie_create_product.py MY-WIDGET-V1 --dry-run   # preview without submitting
uv run scripts/tindie_create_product.py MY-WIDGET-V1 --headless  # no browser window
```

### What `tindie_create_product.py` does

1. Logs into Tindie using `TINDIE_USERNAME` / `TINDIE_PASSWORD` from `.env`
2. Navigates to `/products/create/`
3. Fills title, category, seller-manufactured state, draft/approval state, price, stock, model number, descriptions, dimensions, and project URLs
4. Uploads all YAML images, repeated `--image` values, or files matched through `--image-dir`
5. Pauses so you can review before submitting
6. Saves the base product and creates any configured product options
7. Leaves new listings as drafts by default; after approval, `sync_tindie.py` discovers the numeric V2 product ID by title

## Credentials

Copy `.env.example` to `.env` and fill in:

| Variable | Where to find it |
|---|---|
| `TINDIE_USERNAME` | Your Tindie username |
| `TINDIE_PASSWORD` | Your Tindie login password (used by Playwright only) |
| `TINDIE_API_KEY` | Tindie → Account → Settings → API Keys |
| `TINDIE_STORE_ID` | Optional numeric V2 store ID; otherwise inferred from an existing product |

`.env` is in `.gitignore` — it is never committed.

## Tindie API notes

The authenticated V2 API supports read-only catalog maintenance:

- `GET /api/v2/products/?store=<store_id>` — paginated store products
- `GET /api/v2/products/<id>/` — product details, price, and stock
- `GET /api/v2/products/<id>/options/` — product options
- `GET /api/v2/products/<id>/images/` — product images
- `GET /api/v1/order/` — orders through the official V1 API

Although V2 advertises write methods, seller API keys return `401 Unauthorized`
for product updates. This tool therefore uses V2 for reconciliation and the
authenticated Tindie web UI through Playwright for product creation.

Tindie shipping rates are configured in USD through the seller UI. If a YAML
records source rates in another currency, retain both the source amount and the
converted Tindie amount together with the exchange rate and effective date.

## Adding / updating dependencies

```bash
uv add <package>
uv sync
```

## License

MIT — see [LICENSE](LICENSE).
