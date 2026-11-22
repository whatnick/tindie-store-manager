# Elecrow supplier portfolio review

This file contains only Whatnick-specific supplier state, economics, release
holds, and prioritization. Reusable submission, audit, privacy, authority,
evidence-schema, and lifecycle procedures live only in the canonical
[`whatnick-energy-monitor-elecrow-ordering`](https://github.com/whatnick/whatnick-energy-monitor-skills/tree/main/whatnick-energy-monitor-elecrow-ordering)
skill.

## Current board snapshot

These are the active supplier items recorded in Project 1. They are planning
evidence, not a live Elecrow account read.

| Supplier reference | Job | Stage | Quantity | Unit cost |
| --- | --- | --- | ---: | ---: |
| `20261010041126` | CTVT PMOD PCBA | Production | 10 | $21.43 |
| `20261012051480` | Blue/Hope mono ring PCBA | Production | 10 | $9.97 |
| `20261012059982` | White/Life mono ring PCBA | Production | 10 | $9.56 |
| `61028108228-30` | Ring programmer fence/anvil/probe bare PCBs | Production | 20 | $3.44 |
| `61028108223-25` | Earlier ring programmer fence/anvil/probe submissions | Cancellation requested | 20 | — |
| `20261012044534` | MCP39F511 PCBA, order `318930` | Production | 20 | $13.62 |
| `R20261028117530` | MCP39F511 diagnostic PCBA | Quote | 1 | $373.35 |
| `20261012042661` | ADE7763 PCBA | Quote | 20 | $7.82 |
| `20261010034448` | STPM33 Breakout PCBA, order `322536` | Production | 10 | $15.11 |
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

The owner subsequently confirmed that the MCP39F511 board in consolidated
order `318930` was sent to manufacture, superseding its earlier cancellation
hold. The account UI still labels supplier reference `20261012044534` Payment
Pending, so preserve that discrepancy and use the owner authorization as the
current project-management state. The earlier ring programmer submissions
`61028108223-25` remain cancellation-requested; do not conflate them with the
active ring batch `61028108228-30`.

## Marketplace stock and sell-through

The latest PII-free marketplace audit found two completed Elecrow sales of the
MCP39F521 board and **18 salable units remaining**. It is therefore the
best-selling Elecrow listing supported by completed-order evidence, but its
stock is not low enough to justify another batch.

Public catalog pages confirm only availability, not exact seller inventory:
ADE9000 is in stock at $84.95 and V9360 is in stock at $20.00. Their exact
Elecrow quantities require a separately authenticated marketplace-seller
inventory session. Do not substitute local or Tindie stock counts, original
production quantities, or a public `in stock` badge for that evidence.

The stock implication is to monitor MCP39F521 sell-through rather than
replenish it. After receiving and QA of current production, ADE7763 x20 remains
the strongest next demand-proven build; CTVT should complete first-article QA
before a follow-on batch.

## Marketplace price positioning

The authenticated Elecrow seller inventory on 2026-11-22 showed:

| Listed product | Price | Salable | Confirmed sales |
| --- | ---: | ---: | ---: |
| V9261F Breakout | $20.00 | 18 | 2 |
| V9360 Breakout | $20.00 | 19 | 1 |
| ATM90E26 Breakout | $25.00 | 40 | 40 |
| MCP39F521 Breakout | $29.95 | 18 | 2 |
| ATM90E36 devkit | $30.00 | 0 | 20 |
| ADE9000 Breakout | $84.95 | 7 | 1 |

Price MCP39F511 at **$29.95**. This matches the closest MCP39F5xx family
listing, remains below the three-phase and premium polyphase products, and
avoids presenting a currently manufactured board as a discounted alternative
to MCP39F521. At the $13.62 manufacturing cost and Elecrow's published 5%
seller fee, a $29.95 sale returns $28.45 before withdrawal charges and leaves
$14.83 contribution per board, or 49.5% of sale price, before tax, QA, support,
design-fault refunds, and other overhead. The previous $25 price left $10.13,
or 40.5%, and was too close to the low-cost ATM90E26 anchor for the smaller
20-board batch.

Do not copy MCP39F521's current 20-23% multi-unit discounts onto MCP39F511
without new cost evidence. If quantity breaks are needed after sell-through is
observed, use $27.95 for two and $26.95 for four; these retain approximately
46.3% and 44.5% contribution margins respectively before the same overheads.

## Production economics

The multiplier below is catalog price divided by the quoted manufacturing unit
cost. It is a screening metric, not gross margin: marketplace fees, inbound and
outbound shipping, tax, assembly/QA labour, failures, support, and discounts
still need allowance.

| Product/job | Catalog price | Quoted unit cost | Multiplier | Interpretation |
| --- | ---: | ---: | ---: | --- |
| ADE7763 x20 | $25.00 | $7.82 | 3.20x | Best open replenishment economics and strongest proven demand |
| CTVT PMOD x10 | $54.95 | $21.43 | 2.56x | Plausible research-board margin if QA/yield are good |
| MCP39F511 x20 | $29.95 | $13.62 | 2.20x | Family-aligned price with 49.5% contribution after Elecrow's 5% fee |
| Tph Synth x10 | $50.00 | $33.34 | 1.50x | Insufficient while technical and quote holds remain |
| White/Life ring x10 | $10.00 | $9.56 | 1.05x | Reprice, bundle, or change channel before listing new stock |
| Blue/Hope ring x10 | $10.00 | $9.97 | 1.00x | Reprice, bundle, or change channel before listing new stock |
| V9381 x1 | $30.00 | $76.04 | 0.39x | Diagnostic/obsolete quote, not production economics |

Supplier reference `20261107105421` quotes the Tph Synth batch at **$333.36
total for ten**, including freight, or **$33.336 per board**. The table rounds
that effective unit cost to $33.34.

## Current prioritization

The current board and the latest PII-free authenticated audit support this
order:

1. **Finish and QA production already in flight:** CTVT PMOD, STPM33,
   MCP39F511, and mono-ring Blue/Hope and White/Life. These consume no new
   quote WIP; prepare receiving, inspection, functional-test, firmware
   validation, and stock reconciliation now. Keep the STPM33 Elecrow
   marketplace entry in draft until accepted inventory exists. Do not list
   the rings at the current catalog price: their manufacturing cost alone
   consumes essentially all revenue.
2. **ADE7763 x20:** next quote to release. It has the strongest demonstrated
   demand in the open quote queue and a low quoted effective cost. Confirm the
   final workbook and first-article conditions before payment.
3. **MCP39F511 x20:** manufacturing is authorized. Track supplier reference
   `20261012044534` against order `318930` and reconcile Elecrow's stale
   Payment Pending display without reapplying the superseded cancellation.
4. **Tph Synth FeatherWing x10:** hold at Quote until component-price
   reconciliation, resistor-hole fit, potentiometer seating, substitutions,
   and first-article approval are resolved.
5. **STPM32 x10:** keep at Quote until named pilot users, firmware/test
   readiness, and a receiving plan justify production.
6. **Remaining mono-ring colours:** wait for QA and sell-through evidence from
   Blue/Hope and White/Life before releasing eight more variants. If released,
   combine tooling/freight without merging exact LED BOMs or colour
   instructions.
7. **Old one-board MCP39F511 and V9381 quotes:** close or cancel after live
   account verification; they do not represent intended production economics.

This ranking is a release recommendation, not payment or cancellation
authorization. Live Elecrow status must be refreshed in an authenticated
task browser before acting.
