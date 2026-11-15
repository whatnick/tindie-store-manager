# Elecrow production pipeline

This repository tracks the commercial lifecycle; detailed PCB design and
supplier interaction techniques live in the canonical
[`whatnick-energy-monitor-elecrow-ordering`](https://github.com/whatnick/whatnick-energy-monitor-skills/tree/main/whatnick-energy-monitor-elecrow-ordering)
skill.

## Privacy boundary

Public repository and GitHub Project records may contain:

- supplier reference, project name, quantity, status, and check date;
- non-sensitive quote totals and effective unit cost;
- hashes and repository links for Gerber, BOM, CPL, instructions, and quote
  workbooks;
- technical release holds, substitutions, first-article requirements, and QA
  results.

Do not commit account profiles/cookies, credentials, addresses, phone numbers,
email addresses, personal names, payment data, signed download URLs, raw
account HTML, screenshots of account dashboards, or unredacted supplier chats.
Convert chats into technical decisions and unresolved release holds.

## Lifecycle handoff

| Manufacturing evidence | Project status | Required exit evidence |
| --- | --- | --- |
| Package validated, RFQ submitted | Quote | Complete component pricing and verified quote workbook |
| Quote technically accepted | Payment | Explicit human payment approval |
| Paid or manufacturing started | Production | Supplier completion/shipping evidence |
| Delivered | Receive and QA | Inspection, functional test, calibration and yield |
| QA passed and stock reconciled | Listed / Sustaining | Purchasable listing, price and channel stock |

Advertising remains downstream of stock: a listing must be public,
purchasable, and in stock before an ad can run.

## Current board snapshot

These are the active supplier items recorded in Project 1. They are planning
evidence, not a live Elecrow account read.

| Supplier reference | Job | Stage | Quantity | Unit cost |
| --- | --- | --- | ---: | ---: |
| `20261010041126` | CTVT PMOD PCBA | Production | 10 | $21.43 |
| `20261012051480` | Blue/Hope mono ring PCBA | Production | 10 | $9.97 |
| `20261012059982` | White/Life mono ring PCBA | Production | 10 | $9.56 |
| `61028108228-30` | Ring programmer fence/anvil/probe bare PCBs | Production | 20 | $3.44 |
| `20261012044534` | MCP39F511 PCBA | Payment | 20 | $13.62 |
| `R20261028117530` | MCP39F511 diagnostic PCBA | Quote | 1 | $373.35 |
| `20261012042661` | ADE7763 PCBA | Quote | 20 | $7.82 |
| `20261010034448` | STPM33 Breakout PCBA | Quote | 10 | $15.11 |
| `20261005239301` | STPM32 Breakout PCBA | Quote | 10 | $16.10 |
| `20261107105421` | Tph Synth FeatherWing v0.4 PCBA | Quote | 10 | $33.34 |
| `R20260314221625` | V9381 Breakout diagnostic PCBA | Quote | 1 | $76.04 |
| `20261012058559` | Infrared mono ring PCBA | Quote | 10 | $12.26 |
| `20261012055651` | Pink mono ring PCBA | Quote | 10 | $10.81 |
| `20261012059577` | Indigo mono ring PCBA | Quote | 10 | $16.85 |
| `20261012052441` | Green mono ring PCBA | Quote | 10 | $9.63 |
| `20261012058228` | Yellow mono ring PCBA | Quote | 10 | $11.11 |
| `20261012056372` | Orange mono ring PCBA | Quote | 10 | $11.45 |
| `20261012051013` | Red mono ring PCBA | Quote | 10 | $10.83 |
| `20261012054201` | UV mono ring PCBA | Quote | 10 | $20.81 |

Previously identified duplicate submissions `20261012055567`,
`20261012056773`, and `20261012047382` remain cancellation evidence rather
than active production candidates.

## Production economics

The multiplier below is catalog price divided by the quoted manufacturing unit
cost. It is a screening metric, not gross margin: marketplace fees, inbound and
outbound shipping, tax, assembly/QA labour, failures, support, and discounts
still need allowance.

| Product/job | Catalog price | Quoted unit cost | Multiplier | Interpretation |
| --- | ---: | ---: | ---: | --- |
| ADE7763 x20 | $25.00 | $7.82 | 3.20x | Best open replenishment economics and strongest proven demand |
| CTVT PMOD x10 | $54.95 | $21.43 | 2.56x | Plausible research-board margin if QA/yield are good |
| MCP39F511 x20 | $25.00 | $13.62 | 1.84x | Marginal after fees and fulfilment; verify landed cost |
| Tph Synth x10 | $50.00 | $33.34 | 1.50x | Insufficient while technical and quote holds remain |
| White/Life ring x10 | $10.00 | $9.56 | 1.05x | Reprice, bundle, or change channel before listing new stock |
| Blue/Hope ring x10 | $10.00 | $9.97 | 1.00x | Reprice, bundle, or change channel before listing new stock |
| V9381 x1 | $30.00 | $76.04 | 0.39x | Diagnostic/obsolete quote, not production economics |

## Current prioritization

The current board and the latest PII-free authenticated audit support this
order:

1. **Finish and QA production already in flight:** CTVT PMOD, mono-ring
   Blue/Hope and White/Life, and the ring programmer bare PCBs. These consume
   no new quote WIP; prepare receiving, inspection, functional-test, and stock
   reconciliation now. Do not list the rings at the current catalog price:
   their manufacturing cost alone consumes essentially all revenue.
2. **MCP39F511 x20:** first payment decision. It is out of stock, has recent
   sales, and is already at Payment. Verify that supplier reference
   `20261012044534` has no unresolved substitutions or file changes; do not use
   the economically irrelevant one-board quote. Release only if landed-cost
   review supports a higher selling price or a lower-cost build.
3. **ADE7763 x20:** next quote to release. It has the strongest demonstrated
   demand in the open quote queue and a low quoted effective cost. Confirm the
   final workbook and first-article conditions before payment. If both final
   quotes are simultaneously ready, prioritize ADE7763 ahead of MCP39F511 on
   return on cash and demand evidence.
4. **Tph Synth FeatherWing x10:** hold at Quote until component-price
   reconciliation, resistor-hole fit, potentiometer seating, substitutions,
   and first-article approval are resolved.
5. **STPM32/STPM33 x10:** keep as research/developer batches until named pilot
   users, firmware/test readiness, and a receiving plan justify production.
6. **Remaining mono-ring colours:** wait for QA and sell-through evidence from
   Blue/Hope and White/Life before releasing eight more variants. If released,
   combine tooling/freight without merging exact LED BOMs or colour
   instructions.
7. **Old one-board MCP39F511 and V9381 quotes:** close or cancel after live
   account verification; they do not represent intended production economics.

This ranking is a release recommendation, not payment or cancellation
authorization. Live Elecrow status must be refreshed in an authenticated
task browser before acting.
