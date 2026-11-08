"""Create or update the lifecycle kanban project board described in ROADMAP.md.

Idempotent: re-running reuses the existing project, fields, labels, epics and
draft items (matched by title). Requires the GitHub CLI with the ``project``
scope (``gh auth refresh -s project``).

Product-version items are seeded from ``products/*.yaml``. Supplier orders can
be seeded from an optional, uncommitted JSON file so quote prices and supplier
references stay in the private project rather than in public issues.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PROJECT_TITLE = "Store and Product Lifecycle"

STATUS = [
    ("Inbox", "GRAY", "Captured ideas awaiting triage"),
    ("Backlog", "GRAY", "Accepted ideas awaiting an R&D slot"),
    ("R&D", "BLUE", "Design repo active: schematic, layout, simulation (WIP 3)"),
    ("Prototype", "BLUE", "Prototype run and bench test (WIP 2)"),
    ("Quote", "YELLOW", "Production package submitted; supplier quote pending or under review"),
    ("Revision", "ORANGE", "Changes required by quote review or bench test"),
    ("Payment", "ORANGE", "Quote accepted; awaiting human-approved payment"),
    ("Production", "PURPLE", "Supplier manufacturing in progress"),
    ("Receive and QA", "PURPLE", "Incoming inspection and functional test"),
    ("Listed", "GREEN", "Published on Tindie and/or Elecrow with stock"),
    ("Sustaining", "GREEN", "Selling or out of stock; reorder, revise or retire decision"),
    ("Decommission", "RED", "Retiring: last stock, EOL notice, archive docs"),
    ("Done", "GRAY", "Closed"),
]

SINGLE_SELECT = {
    "Product line": ["Energy monitoring", "LED cosplay props", "Store tooling", "Contract and custom"],
    "Interest area": ["Electronics", "Mechanical", "Software and firmware", "Business and operations"],
    "Channel": ["Tindie", "Elecrow", "Both", "None"],
    "Decision": ["Invest", "Sustain", "Revise", "Consolidate", "Retirement candidate", "Retired"],
    "Approval state": ["Proposed", "Approved"],
    "Evidence confidence": ["High", "Medium", "Low"],
}
TEXT_FIELDS = ["Version", "Supplier ref", "SKU", "Analysis URL"]
NUMBER_FIELDS = ["Quantity", "Unit cost USD", "Stock", "Lifetime units"]
DATE_FIELDS = ["Target date", "Last sale", "Review date"]

LABELS = {
    "lifecycle": ("5319e7", "Product lifecycle tracking"),
    "epic": ("3e4b9e", "Roadmap phase or multi-issue initiative"),
    "idea": ("fbca04", "New product or feature idea from intake"),
    "feedback": ("d4c5f9", "Customer feedback, review or return"),
    "manufacturing": ("c2e0c6", "Supplier quote, order or production run"),
    "inventory": ("bfdadc", "Stock, reorder and channel inventory"),
    "sales": ("0e8a16", "Orders, sales ledger and reporting"),
    "contract": ("b60205", "Custom development and contract work"),
    "retirement-candidate": ("d93f0b", "Proposed retirement awaiting owner approval"),
    "needs-evidence": ("fbca04", "Lifecycle decision needs stronger cost, demand or replacement evidence"),
    "area:electronics": ("1d76db", "Electronics interest area"),
    "area:mechanical": ("c5def5", "Mechanical interest area"),
    "area:software": ("0052cc", "Software and firmware interest area"),
    "line:energy": ("f9d0c4", "Energy monitoring product line"),
    "line:led-props": ("f7c6c7", "LED cosplay props product line"),
}

EPICS = [
    ("Phase 0: Foundations and lifecycle board", ["epic", "lifecycle"],
     "Create the kanban board, labels and lifecycle fields; seed items; add lifecycle metadata to product YAMLs."),
    ("Phase 1: Multi-channel catalogue and inventory", ["epic", "inventory"],
     "Channel blocks for Tindie and Elecrow, split local/partner stock, reorder points, Elecrow storefront sync, component inventory."),
    ("Phase 2: Orders and sales records", ["epic", "sales"],
     "Append-only sales ledger without personal data, Tindie V1 order import, Elecrow sales import, monthly reports, feedback issues."),
    ("Phase 3: Manufacturing pipeline automation", ["epic", "manufacturing"],
     "Design-repo template, supplier status sync, quote review and receive-QA checklists, stale-quote housekeeping."),
    ("Phase 4: Idea intake and agents on self-hosted Kubernetes", ["epic", "idea", "area:software"],
     "WhatsApp idea intake to Inbox issues, least-privilege GitHub App, scheduled sync CronJobs, encrypted secrets, daily digest."),
    ("Phase 5: Catalogue growth and ecosystem", ["epic", "line:energy", "line:led-props"],
     "Energy-monitoring family consolidation, LED cosplay prop family, kits and bundles, YAML-driven docs site, community."),
    ("Phase 6: Services and contract work", ["epic", "contract"],
     "Custom-version call to action, case studies, fixed-scope offerings and contract pipeline on the board."),
]

ITEM_OVERRIDES = {
    "Approve proposed product retirements: CS5464, Onion Feather, Wemos shield": {
        "Status": "Inbox",
        "Interest area": "Business and operations",
        "Product line": "Energy monitoring",
    },
    "Complete ADS1115 CT/Grove decommission notice on Tindie": {
        "Status": "Decommission",
        "Interest area": "Business and operations",
        "Product line": "Energy monitoring",
    },
    "Complete NodeMCU Energy Monitor retirement on Tindie (kit and SMD)": {
        "Status": "Decommission",
        "Interest area": "Business and operations",
        "Product line": "Energy monitoring",
    },
    "Complete Xadow SD retirement notice on Tindie": {
        "Status": "Decommission",
        "Interest area": "Business and operations",
        "Product line": "Contract and custom",
    },
    "Add op-amp preamp option for low-sensitivity piezos": {
        "Status": "Backlog",
        "Interest area": "Electronics",
        "Product line": "LED cosplay props",
    },
    "Add LiPo battery and USB charging to the board": {
        "Status": "Backlog",
        "Interest area": "Electronics",
        "Product line": "LED cosplay props",
    },
    "Peak detection / velocity-sensitive brightness": {
        "Status": "Backlog",
        "Interest area": "Software and firmware",
        "Product line": "LED cosplay props",
    },
    "Multi-channel version for several drums/piezos": {
        "Status": "Backlog",
        "Interest area": "Electronics",
        "Product line": "LED cosplay props",
    },
    "Port firmware to ESP32 / WLED-style effects": {
        "Status": "Backlog",
        "Interest area": "Software and firmware",
        "Product line": "LED cosplay props",
    },
    "Document build, assembly and tuning guide": {
        "Status": "Backlog",
        "Interest area": "Business and operations",
        "Product line": "LED cosplay props",
    },
    "Link videos and Tindie listing updates": {
        "Status": "Backlog",
        "Interest area": "Business and operations",
        "Product line": "LED cosplay props",
    },
    "Migrate KiCad project to current KiCad version": {
        "Status": "Revision",
        "Interest area": "Electronics",
        "Product line": "LED cosplay props",
    },
    "ESP32-S3 Nano fleet control via ESP-NOW": {
        "Status": "R&D",
        "Interest area": "Software and firmware",
        "Product line": "LED cosplay props",
    },
}


def gh(*args: str, check: bool = True) -> str:
    for attempt in range(3):
        result = subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8")
        if result.returncode == 0 or not check:
            return result.stdout
        transient = any(
            message in result.stderr.lower()
            for message in (
                "connection was forcibly closed",
                "connection reset",
                "tls handshake timeout",
                "timeout awaiting response headers",
            )
        )
        if not transient or attempt == 2:
            raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr.strip()}")
        time.sleep(2**attempt)
    raise AssertionError("unreachable")


def graphql(query: str, **variables) -> dict:
    args = ["api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        flag = "-F" if isinstance(value, (int, bool)) else "-f"
        args += [flag, f"{key}={value}"]
    return json.loads(gh(*args))["data"]


def ensure_project(owner: str, repo: str, public: bool) -> dict:
    projects = json.loads(gh("project", "list", "--owner", owner, "--format", "json", "--limit", "100"))
    project = next((p for p in projects["projects"] if p["title"] == PROJECT_TITLE), None)
    if project is None:
        project = json.loads(gh("project", "create", "--owner", owner, "--title", PROJECT_TITLE, "--format", "json"))
        print(f"created project #{project['number']}")
    gh("project", "link", str(project["number"]), "--owner", owner, "--repo", f"{owner}/{repo}", check=False)
    gh("project", "edit", str(project["number"]), "--owner", owner,
       "--visibility", "PUBLIC" if public else "PRIVATE",
       "--description", "Product lifecycle: R&D, manufacturing, multi-channel sales, inventory and decommissioning",
       "--readme", "See ROADMAP.md in whatnick/tindie-store-manager for stages, fields and WIP limits.")
    return project


def fields(owner: str, number: int) -> dict:
    data = json.loads(gh("project", "field-list", str(number), "--owner", owner, "--format", "json", "--limit", "50"))
    return {f["name"]: f for f in data["fields"]}


def ensure_fields(owner: str, number: int, project_id: str) -> dict:
    existing = fields(owner, number)
    for name, options in SINGLE_SELECT.items():
        if name not in existing:
            gh("project", "field-create", str(number), "--owner", owner, "--name", name,
               "--data-type", "SINGLE_SELECT", "--single-select-options", ",".join(options))
    for names, kind in ((TEXT_FIELDS, "TEXT"), (NUMBER_FIELDS, "NUMBER"), (DATE_FIELDS, "DATE")):
        for name in names:
            if name not in existing:
                gh("project", "field-create", str(number), "--owner", owner, "--name", name, "--data-type", kind)

    status = fields(owner, number)["Status"]
    current = [o["name"] for o in status.get("options", [])]
    if current != [s[0] for s in STATUS]:
        options = ",".join(
            '{name:%s,color:%s,description:%s}' % (json.dumps(n), c, json.dumps(d)) for n, c, d in STATUS
        )
        graphql(
            "mutation($id:ID!){updateProjectV2Field(input:{fieldId:$id,singleSelectOptions:[%s]}){clientMutationId}}"
            % options,
            id=status["id"],
        )
        print("updated Status columns")
    return fields(owner, number)


def ensure_labels(full_repo: str) -> None:
    for name, (color, description) in LABELS.items():
        gh("label", "create", name, "-R", full_repo, "--color", color, "--description", description, "--force")


def items(owner: str, number: int) -> dict:
    data = json.loads(gh("project", "item-list", str(number), "--owner", owner, "--format", "json", "--limit", "500"))
    return {i["content"].get("title") or i.get("title"): i for i in data["items"]}


def set_field(project_id: str, item_id: str, field: dict, value) -> None:
    if value is None or value == "":
        return
    args = ["project", "item-edit", "--project-id", project_id, "--id", item_id, "--field-id", field["id"]]
    if "options" in field:
        option = next(o for o in field["options"] if o["name"] == value)
        args += ["--single-select-option-id", option["id"]]
    elif field["name"] in NUMBER_FIELDS:
        args += ["--number", str(value)]
    elif field["name"] in DATE_FIELDS:
        args += ["--date", str(value)]
    else:
        args += ["--text", str(value)]
    gh(*args)


def item_value(item: dict, field_name: str):
    return item.get(field_name[:1].lower() + field_name[1:])


def upsert(owner: str, number: int, project_id: str, existing: dict, field_map: dict,
           title: str, body: str, values: dict, issue_url: str | None = None) -> None:
    item = existing.get(title)
    if item is None:
        if issue_url:
            item = json.loads(gh("project", "item-add", str(number), "--owner", owner, "--url", issue_url, "--format", "json"))
        else:
            item = json.loads(gh("project", "item-create", str(number), "--owner", owner,
                                 "--title", title, "--body", body, "--format", "json"))
        existing[title] = item
        print(f"added: {title}")
    for name, value in values.items():
        if item_value(item, name) != value:
            set_field(project_id, item["id"], field_map[name], value)


def product_values(path: Path) -> tuple[str, str, dict]:
    p = yaml.safe_load(path.read_text(encoding="utf-8"))
    listed = p.get("tindie_product_id") is not None
    stock = int(p.get("stock") or 0)
    if p.get("listing_state") == "retired":
        status = "Decommission"
    elif not p.get("active", True):
        status = "Prototype"
    elif listed and stock > 0:
        status = "Listed"
    elif listed:
        status = "Sustaining"
    else:
        status = "Backlog"
    category = (p.get("category") or "").lower()
    inferred_line = "LED cosplay props" if any(k in p["sku"].lower() for k in ("lantern", "drum")) else (
        "Energy monitoring" if "energy" in category else "Contract and custom")
    lifecycle = p.get("lifecycle") or {}
    business_case = p.get("business_case") or {}
    sales = business_case.get("tindie_sales") or {}
    line = lifecycle.get("product_line") or inferred_line
    decision = business_case.get("decision")
    confidence = business_case.get("confidence")
    analysis_url = business_case.get("analysis_url")
    title = f"{p['name']} ({p['sku']})"
    body = (f"Product YAML: `products/{path.name}`\n\n"
            f"Design: {p.get('design_url') or 'n/a'}\nCode: {p.get('code_url') or 'n/a'}\n\n"
            f"Decision: {decision or 'not assessed'}\n"
            f"Analysis: {analysis_url or 'not linked'}\n\n"
            "Out-of-stock items in Sustaining need a reorder, revise or decommission decision.")
    values = {
        "Status": lifecycle.get("stage") or status,
        "Product line": line,
        "Interest area": lifecycle.get("interest_area") or "Electronics",
        "Channel": lifecycle.get("channel") or ("Tindie" if listed else "None"),
        "Decision": decision,
        "Approval state": business_case.get("approval_state"),
        "Evidence confidence": confidence,
        "SKU": p["sku"],
        "Stock": stock,
        "Version": lifecycle.get("version"),
        "Lifetime units": sales.get("lifetime_units"),
        "Last sale": sales.get("last_sale"),
        "Review date": lifecycle.get("review_date"),
        "Analysis URL": analysis_url,
    }
    return title, body, values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--owner", default="whatnick")
    parser.add_argument("--repo", default="tindie-store-manager")
    parser.add_argument("--public", action="store_true", help="make the project public (default private)")
    parser.add_argument("--supplier-orders", type=Path,
                        help="uncommitted JSON list of supplier orders to seed as draft items")
    parser.add_argument("--skip-products", action="store_true")
    args = parser.parse_args()
    full_repo = f"{args.owner}/{args.repo}"

    project = ensure_project(args.owner, args.repo, args.public)
    number, project_id = project["number"], project["id"]
    field_map = ensure_fields(args.owner, number, project_id)
    ensure_labels(full_repo)
    existing = items(args.owner, number)

    issues = json.loads(gh("issue", "list", "-R", full_repo, "--state", "all", "--label", "epic",
                           "--json", "title,url", "--limit", "100"))
    by_title = {i["title"]: i["url"] for i in issues}
    for title, labels, body in EPICS:
        url = by_title.get(title)
        if url is None:
            url = gh("issue", "create", "-R", full_repo, "--title", title, "--body",
                     body + f"\n\nSee [ROADMAP.md](https://github.com/{full_repo}/blob/main/ROADMAP.md).",
                     *sum((["--label", label] for label in labels), [])).strip()
        upsert(args.owner, number, project_id, existing, field_map, title, body,
               {"Status": "Backlog", "Interest area": "Business and operations"}, issue_url=url)

    if not args.skip_products:
        for path in sorted((ROOT / "products").glob("*.yaml")):
            title, body, values = product_values(path)
            upsert(args.owner, number, project_id, existing, field_map, title, body, values)

    for title, values in ITEM_OVERRIDES.items():
        item = existing.get(title)
        if item is None:
            continue
        for name, value in values.items():
            if item_value(item, name) != value:
                set_field(project_id, item["id"], field_map[name], value)

    if args.supplier_orders:
        for order in json.loads(args.supplier_orders.read_text(encoding="utf-8")):
            title = order["title"]
            body = order.get("body", "")
            values = {k: order.get(k) for k in
                      ("Status", "Product line", "Interest area", "Channel", "Version",
                       "Supplier ref", "Quantity", "Unit cost USD", "Target date")}
            upsert(args.owner, number, project_id, existing, field_map, title, body, values)

    print(f"project: {project['url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
