# whatnick Tindie Store — Energy Monitor Products

Manage product descriptions, stock levels, and Tindie store operations for the **whatnick** store.

## Structure

```
tindie_products/
├── products/            # One YAML file per product (<SKU>.yaml)
├── tindie_manager/      # Python package (API client + data models)
│   ├── product.py       # Product & Inventory dataclasses
│   └── tindie_api.py    # Tindie REST API wrapper
├── scripts/             # CLI management scripts
│   ├── check_stock.py   # Print inventory summary
│   ├── list_products.py # List products (local or live from API)
│   ├── update_stock.py  # Set stock for a product
│   └── sync_tindie.py   # Pull live Tindie stock → update local YAMLs
├── data/                # Generated exports / snapshots
├── .env.example         # Credential template
└── requirements.txt
```

## Setup

```bash
# Install uv if you don't have it: https://docs.astral.sh/uv/getting-started/installation/

uv sync                    # creates .venv and installs all dependencies

cp .env.example .env
# Edit .env and add your Tindie credentials
```

## Adding a Product

1. Copy `products/example_product.yaml` to `products/<SKU>.yaml`
2. Fill in all fields
3. Set `active: true` when ready to list
4. After creating the Tindie listing, paste the product ID into `tindie_product_id`

## Scripts

```bash
# Show inventory summary
uv run scripts/check_stock.py

# Show only low / out-of-stock items (threshold = 3)
uv run scripts/check_stock.py --low-only --threshold 3

# List all active products
uv run scripts/list_products.py

# List with live stock from Tindie API
uv run scripts/list_products.py --live

# Set local stock for EM-1001 to 10 units
uv run scripts/update_stock.py EM-1001 10

# Set local stock AND push to Tindie API
uv run scripts/update_stock.py EM-1001 10 --push

# List a new product on Tindie via browser automation (opens Chromium)
uv run scripts/tindie_create_product.py V9381-BREAKOUT

# Dry-run: fill the form without submitting (useful for inspecting selectors)
uv run scripts/tindie_create_product.py V9381-BREAKOUT --dry-run

# Headless mode (no visible browser window)
uv run scripts/tindie_create_product.py V9381-BREAKOUT --headless

# Pull stock from Tindie and update all local YAML files
uv run scripts/sync_tindie.py

# Dry-run sync (see what would change)
uv run scripts/sync_tindie.py --dry-run
```

## Adding / Updating Dependencies

```bash
uv add <package>           # add a runtime dependency
uv add --dev <package>     # add a dev dependency
uv remove <package>        # remove a dependency
uv sync                    # re-sync .venv after manual pyproject.toml edits
```

## Tindie API Reference

- API docs: <https://www.tindie.com/docs/api/>
- Credentials: Account → Settings → API Keys
