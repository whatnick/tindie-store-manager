# Hardware repository analysis inventory

Reviewed **2026-11-08** across public, owned, non-archived Whatnick
repositories. The scan found roughly 60 repositories containing electronic or
mechanical hardware. It used repository descriptions and filenames, so unusual
or undocumented hardware may still require manual classification.

## Analysis maturity

### Full business or market analysis

- `whatnick/DrumLights` - sourcing defects, BOM cost at quantity, platform
  options, market sizing, competition, TCO, pricing and next steps.
- `whatnick/lantern_ring` - unit-cost scenarios, price tests, reachable market,
  competitors, event economics, safety, licensing and launch gates.
- `whatnick/tindie-store-manager` - portfolio lifecycle, sales evidence,
  retirement decisions and channel/manufacturing roadmap.
- The legacy DIN rail repositories are assessed together in
  [`din-rail-open-nilm-platform.md`](din-rail-open-nilm-platform.md) as a
  modular open NILM development platform.

### Manufacturing or sourcing evidence, but no complete business case

- `whatnick/ctvt-pmod`
- `whatnick/Tph_Synth_Featherwing`
- `whatnick/STPM3x_Breakout`
- `whatnick/ADE9000_Breakout`
- `whatnick/V93XX_Breakout`
- `whatnick/MCP39xx_Breakout`
- `whatnick/MCP39F511_Breakout`
- `whatnick/MCP39F521_Breakout`
- `whatnick/ATM90E36_Breakout_KiCAD`
- `whatnick/atm90e26_breakout_kicad`
- `whatnick/ATM90E26_Featherwing_KiCAD`
- `whatnick/V9261F_Breakout`
- `whatnick/V9203_Devkit`
- `whatnick/CS5464_Breakout`
- `whatnick/CS5490_Breakout`
- `whatnick/ade7763_breakout_kicad`
- `whatnick/ADE7816_Breakout`
- `whatnick/din_meter_atm90e26`
- `whatnick/din_power_atm90e26`
- `whatnick/Onion_Feather`
- `whatnick/ADS1115_Emon_Featherwing`

These repositories should adopt the normalized template when a product is
selected for investment, revision or replenishment. Do not spend analysis time
on every dormant repository before triage; first use sales and strategic fit.

### Legacy or unassessed physical hardware

The following repositories contain physical designs but have no normalized
business case and are not represented clearly as current product versions:

- `NodeMCU_Emon`, `ADS1115_Grove_Emon`, `hearthstone_brooch`
- `Micro_TV_B_Gone_KiCAD`, `sperm_whale`
- `din_meter_ade7816`, `din_meter_atm90e36`
- `din_isolated_SPI`, `din_isolated_SPI_onion`, `din_power_relays`
- `ATM90E26_Breakout`, `ATM90E26_Featherwing`
- `ATM90E3X_Featherwing`, `ATM90E36_Breakout`
- `ATM90E36_SPI_DIN_Wemos`, `ESP8266_Single_Phase`
- `IotaWatt_Kicad`, `SSD1306_Short_Oled`
- `NodeMCU_Sensor_Project`, `pcix1proto`, `CameraTrigger_PCB`
- `Grove_Pulse_Counter`, `ADE7763_Breakout`
- `Xadow_Multiserial`, `Onion_Omega_Games`, `LazyLazy_Susan`
- `DS1682_Breakout_Qwiic_Grove`, `USB_BigRed_Button`

The legacy list is an **inventory**, not a retirement list. Repositories may
remain useful as references even when no product is sold. Add a board product
or portfolio item only when there is a commercial, support, manufacturing or
explicit archival decision.

## Standard adoption sequence

1. Link each active product YAML to its design and firmware repositories.
2. Record sales actuals, stock, current unit cost and latest manufacturing
   evidence.
3. Run critical-part and platform lifecycle checks.
4. Add competition, reachable-market and TCO analysis only for products being
   invested in or revised.
5. Record a Decision and Evidence confidence on the lifecycle board.
6. Require owner approval before changing any candidate to Retired.
