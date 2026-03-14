# tindie-store-manager

A Git-based tool for managing your [Tindie](https://www.tindie.com) store: product descriptions, stock levels, and automated listing via browser automation.

> **Real-world example:** The `products/` directory in this repo contains the actual listings for the [whatnick](https://www.tindie.com/stores/whatnick/) energy monitor store — use them as reference when writing your own YAMLs.

## Features

- **Product-as-code** — one YAML file per product, version-controlled
- **Inventory CLI** — check stock, highlight low/out-of-stock items
- **Tindie API client** — read orders and product data
- **Playwright automation** — fill and submit the Tindie create-product form automatically, including image upload
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

specs:
  voltage_range: "3.3–5 V"
  interfaces:
    - "UART"
  dimensions_mm: "38.1 × 27.9"
  extra:
    chip: "MyChip XYZ"
images: []
```

See the `products/` directory for 24 real-world examples.

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
uv run scripts/update_stock.py MY-WIDGET-V1 10 --push   # also push to API

# Sync stock from Tindie order history
uv run scripts/sync_tindie.py
uv run scripts/sync_tindie.py --dry-run

# Create a new Tindie listing via browser automation
uv run scripts/tindie_create_product.py MY-WIDGET-V1
uv run scripts/tindie_create_product.py MY-WIDGET-V1 --image https://example.com/photo.jpg
uv run scripts/tindie_create_product.py MY-WIDGET-V1 --dry-run   # preview without submitting
uv run scripts/tindie_create_product.py MY-WIDGET-V1 --headless  # no browser window
```

### What `tindie_create_product.py` does

1. Logs into Tindie using `TINDIE_USERNAME` / `TINDIE_PASSWORD` from `.env`
2. Navigates to `/products/create/`
3. Fills: title, category, price, stock, model number, short description, PCB dimensions, full description (markdown), design URL, code URL, YouTube URL
4. Uploads a product image (local file or URL — downloads automatically)
5. Pauses so you can review before submitting
6. After submit, extracts the new product ID from the redirect URL and writes it back to the YAML file

## Credentials

Copy `.env.example` to `.env` and fill in:

| Variable | Where to find it |
|---|---|
| `TINDIE_USERNAME` | Your Tindie username |
| `TINDIE_PASSWORD` | Your Tindie login password (used by Playwright only) |
| `TINDIE_API_KEY` | Tindie → Account → Settings → API Keys |

`.env` is in `.gitignore` — it is never committed.

## Tindie API notes

The Tindie REST API (`/api/v1/`) supports:
- `GET /api/v1/order/` — list orders (used to discover product IDs)
- `GET /api/v1/product/` — list products
- `GET /api/v1/orderitem/` — list order line items

There is **no inventory/stock endpoint** and **no product-create endpoint** via the API. Stock management must be done via the web UI; this repo automates that with Playwright.

## Adding / updating dependencies

```bash
uv add <package>
uv sync
```

## License

MIT — see [LICENSE](LICENSE).
