# Product portfolio and lifecycle review - 2026-11-08

This review covers the private
[Store and Product Lifecycle project](https://github.com/users/whatnick/projects/1/views/2),
the 27 product YAMLs, all 32 pages of Tindie seller order history, active
supplier items, and the public Whatnick hardware repositories.

No product in **Retirement candidate** is approved for retirement by this
review. Those decisions remain proposed until the owner approves them.
Aggregated sales evidence contains no customer personal data.

## Executive sanity check

The lifecycle model and roadmap are directionally sound. The board now covers
R&D, manufacturing, listing, sustaining and decommissioning, and it keeps
payments and publication behind human gates. The main weakness is not the
process design; it is inconsistent evidence and item hygiene.

Observed board state before this review:

- 65 items and 23 fields.
- 9 items had no Status and 12 had no Interest area.
- Quote/Revision WIP was 14 against the documented limit of 4.
- The Kanban view exists as a board layout, but has no saved filter or explicit
  grouping field in the API response.
- Product cards largely recorded stock and channel only. They did not expose
  sales history, decision confidence, analysis links or approval state.
- Product versions are sometimes conflated. The legacy Lantern Ring listing
  and the unqualified v2 mechanical redesign should be separate lifecycle
  items. DrumLights was in Sustaining although its own analysis recommends a
  sourcing redesign and a new ESP32 version.
- The official Tindie V1 order endpoint returned `401` with the current API
  key. Sales below were therefore aggregated from the authenticated seller
  order history. Phase 2 should not assume the V1 import works until access is
  revalidated.

This review adds normalized lifecycle and business-case metadata to every
product YAML and exposes it through project fields: Decision, Evidence
confidence, Approval state, Lifetime units, Last sale, Review date and Analysis
URL.

After synchronization, the board has 66 items and 30 fields, with no item
missing Status or Interest area. R&D is 1/3 and Prototype is 1/2, but the
combined Quote and Revision queue remains 16 items against the documented WIP
limit of 4. Ten mono-ring colour quotes are one coordinated manufacturing
batch; even counting that set once leaves nine effective Quote/Revision work
items. This is now the primary board-hygiene problem: stale or blocked quotes
should be closed or moved to Backlog, and no more than four efforts should be
selected for the next purchasing batch. Owner approval is tracked in
[issue #15](https://github.com/whatnick/tindie-store-manager/issues/15).

## Normalized decision rules

| Decision | Meaning |
| --- | --- |
| **Invest** | Current demand, strategic role or manufacturing progress supports active work. |
| **Sustain** | Keep available or supported; do not start a redesign without new evidence. |
| **Revise** | Preserve the product concept but resolve sourcing, safety, documentation or architecture issues. |
| **Consolidate** | Merge overlapping products or move customers to one maintained family. |
| **Retirement candidate** | Prepare evidence and migration guidance; owner approval is required before changing a listing. |
| **Retired** | Owner-approved retirement already recorded; preserve designs and order history. |

Confidence is **High** when sales, stock and technical evidence agree;
**Medium** when platform status, cost or replacement evidence still needs
verification; and **Low** when the decision is mostly assumption.

## Portfolio decisions

| Product | Stock | Lifetime units | Last Tindie sale | Decision | Rationale |
| --- | ---: | ---: | --- | --- | --- |
| 3-phase AC Synthesizer | 0 | 3 | 2022-01-30 | Revise | Low historical volume, but v0.4 has a current manufacturing package and quote. |
| ADE7763 Breakout | 2 | 48 | 2026-03-17 | Invest | Recent demand and an open PCBA quote justify replenishment. |
| ADE7816 Breakout | 0 | 1 | 2021-03-21 | Sustain | Very low demand, but no authoritative evidence of discontinuation was found. Keep low priority until ADI status is confirmed. |
| ADE9000 Breakout | 10 | 0 | Never | Invest | New, high-value portfolio product with active Elecrow listing and advertising; too new for sales history to be meaningful. |
| ADS1115 CT/Grove module | 0 | 17 | 2017-04-16 | Retired | Existing retirement is technically supported: multiplexed 860 SPS ADC is a poor fit for phase-coherent multi-channel energy waveforms. |
| ATM90E26 Breakout | 0 | 152 | 2021-10-19 | Sustain | Strongest lifetime seller; zero stock is not retirement evidence. Review a small replenishment or common-family revision. |
| ATM90E26 FeatherWing | 0 | 59 | 2025-10-31 | Invest | Strong historical demand and recent sale. Prioritize a current BOM and small batch. |
| ATM90E36 devkit | 0 | 41 | 2021-02-02 | Revise | Proven demand, but consolidate the old devkit and newer three-phase form factors around one maintained design. |
| CS5464 Breakout | 0 | 0 | Never | **Retirement candidate** | Cirrus marks the IC discontinued; there are no recorded sales or stock, and CS5490 provides active but non-drop-in portfolio coverage. |
| CS5490 Breakout | 10 | 13 | 2021-08-02 | Sustain | Stock exists; keep listed while measuring current demand before another run. |
| CTVT PMOD | 0 | 0 | Never | Invest | New prototype with a production package and companion DSP; evaluate the first batch and calibration workflow. |
| DrumLights | 0 | 0 | Never | Revise | Business case supports a niche product, but sourcing defects and the ESP32 fleet-node redesign must be completed first. |
| Energy Monitor FeatherWing | 0 | 20 | 2017-02-03 | Consolidate | Historical demand exists, but the platform is stale and overlaps newer PMOD and metering-IC products. |
| Gamepad PMOD | 8 | 0 | Never | Invest | New small-stock market test; review after the first sales window. |
| iCE40 Feather | 0 | 2 | 2021-04-02 | Sustain | Low sales and no stock, but Lattice still presents iCE40 UltraPlus as a current related family; retirement is not justified by lifecycle evidence. |
| Lantern Rings | 8 | 2 | 2026-09-26 | Revise | Recent sales and manufacturing activity support the family, but v2 has safety, fit and licensing gates. Split legacy and v2 lifecycle items. |
| MCP39F511 Breakout | 0 | 11 | 2025-10-29 | Invest | Recent demand and a current PCBA payment item support replenishment. |
| MCP39F521 Breakout | 0 local | 4 | 2022-10-05 | Sustain | Tindie history understates current demand: Elecrow has recent sales and partner stock. |
| NodeMCU Energy Monitor PCB/Kit | 0 | 59 | 2018-02-27 | Retired | Retirement is reasonable despite strong historical sales: no recent demand and the family is superseded by maintained designs. |
| NodeMCU Energy Monitor SMD | 0 | 47 | 2017-10-24 | Retired | Same family decision as the PCB/kit; retain sources and customer records. |
| Onion Feather | 0 | 1 | 2020-12-07 | **Retirement candidate** | One sale, no stock and dependence on a niche host platform; verify current Omega2 demand before approval. |
| ATM90E36 Three-phase FeatherWing | 0 | 16 | 2019-12-01 | Consolidate | Preserve customer value but merge with the maintained ATM90E36/STPM three-phase roadmap. |
| V9203 FeatherWing | 0 | 0 | Never | Consolidate | No sales and single-vendor risk, but current V9203 documentation appears to exist. Review it inside the V93XX family rather than retiring it in isolation. |
| V9360 Breakout | 3 | 0 | Never | Invest | New stocked product with Elecrow channel coverage; collect a first sales window. |
| V9381 Breakout | 5 | 0 | Never | Invest | New stocked product with current firmware/design repositories. |
| Wemos D1 Mini Power Shield | 0 | 4 | 2019-02-06 | **Retirement candidate** | Low sales, no stock and no linked maintained design repository. |
| Xadow SD | 0 | 5 | 2017-01-24 | Retired | Original Xadow platform lifecycle evidence supports the existing retirement. |

## Proposed retirements awaiting approval

Approve or reject each candidate separately:

1. **CS5464 Breakout** - strongest case. Cirrus marks the
   [CS5464 discontinued](https://www.cirrus.com/products/cs5464), while the
   maintained [CS5490 is active](https://www.cirrus.com/products/cs5490).
   The replacement is not drop-in and needs migration guidance.
2. **Onion Feather** - commercial retirement candidate, not confirmed platform
   EOL. Onion still publishes
   [Omega2 documentation](https://docs.onion.io/omega2-docs/) and points to
   current OpenWrt 23.05 documentation. Approve only after checking module
   availability and whether the adapter has ongoing customer value.
3. **Wemos D1 Mini Power Shield** - low-value, low-volume accessory with no
   maintained design repository linked. Confirm current D1 Mini mechanical
   compatibility before deciding between a revision and retirement.

Approval should trigger a separate change that marks the listing retired,
publishes a sourced notice, preserves design files and order history, and
verifies the live seller status. Rejection should change the Decision to
Sustain or Revise and identify the next evidence or production action.

ADE7816 and iCE40 were reviewed but are **not** retirement candidates:
authoritative discontinuation evidence was not found for ADE7816, and Lattice
only identifies the iCE40 LM series as discontinued on its
[iCE40 family page](https://www.latticesemi.com/en/Products/FPGAandCPLD/iCE40).
V9203 is a consolidation review because Vangotech lifecycle status could not
be verified.

## Existing retirement verification

The four already-retired catalogue entries are defensible:

- ADS1115 CT/Grove: technical mismatch for coherent energy waveform capture.
- NodeMCU PCB/kit and SMD: strong historical sales but no demand since
  2017-2018, with maintained alternatives available.
- Xadow SD: original platform migration/end-of-life evidence is documented.

Their remaining live Tindie tasks are operational completion issues, not new
retirement decisions.

## Manufacturing and roadmap corrections

1. Reconcile 14 Quote items against the WIP limit of 4. Close cancelled or
   superseded quotes, and group colour variants under a parent manufacturing
   run where supplier handling permits.
2. Separate product versions. Create distinct lifecycle items for legacy
   Lantern Rings and v2, and for DrumLights Nano shield and ESP32 fleet node.
3. Move DrumLights feature issues onto the board with explicit Status and
   Interest area.
4. Add supplier quote age and last supplier update to the manufacturing view.
5. Treat zero stock as a decision trigger, not a retirement rule.
6. Revalidate Tindie order API access before implementing the Phase 2 importer.

## Repository analysis coverage

Only DrumLights and Lantern Ring currently contain full business/market
analysis. The remaining hardware repositories mostly contain design files,
BOMs or manufacturing outputs without demand, competition, pricing, TCO or
lifecycle decisions. Use
[`business-analysis-template.md`](business-analysis-template.md) for all new
or revised hardware and the central product metadata for portfolio-level
triage. The detailed repository census is in
[`hardware-repository-inventory.md`](hardware-repository-inventory.md).
