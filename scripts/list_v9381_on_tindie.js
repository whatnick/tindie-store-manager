/**
 * list_v9381_on_tindie.js
 *
 * Playwright script to create the V9381 Breakout listing on Tindie.
 *
 * Prerequisites:
 *   npm install playwright
 *   npx playwright install chromium
 *
 * Usage:
 *   TINDIE_USER=whatnick TINDIE_PASS=<your_password> node scripts/list_v9381_on_tindie.js
 *
 * The script will:
 *   1. Log in to Tindie
 *   2. Navigate to /products/create/
 *   3. Fill in all fields from the V9381 YAML
 *   4. Pause for your review before submitting
 *   5. Print the new product URL so you can update v9381-breakout.yaml
 */

const { chromium } = require('playwright');
const path = require('path');

// ── Product data (from products/v9381-breakout.yaml) ──────────────────────────
const PRODUCT = {
  name: 'V9381 Breakout',
  category: 'iot-home',          // Tindie category value closest to Energy Monitor
  price: '30.00',
  quantity: '0',
  description: `Breadboard-compatible breakout for the Vangotech V9381 single-phase energy \
monitoring ASIC — the upgraded sibling of the V9360, adding SPI alongside \
UART for ~10x faster data acquisition. The SPI interface supports clock \
speeds up to 10 MHz in FourWire and ThreeWire modes, enabling rapid waveform \
capture (~200 ms) and on-board FFT with ESP-DSP.

UART multi-drop addressing (A0/A1 pins) allows up to 4 V9381 devices on a \
shared half-duplex bus. Onboard 3.3 V LDO for 5 V USB compatibility.

Open-hardware KiCad design files and an Arduino library with SPI/UART \
waveform capture, FFT, and dirty-mode examples (ESP32-S3) are available \
on GitHub.

## What's in the box
- 1x V9381 Breakout PCB (assembled)
- 2x 1x10 pin headers (unsoldered)

## Specifications
- Chip: Vangotech V9381
- Supply: 3.3–5 V (onboard LDO)
- Interfaces: UART (half-duplex, 8O1) + SPI (FourWire / ThreeWire)
- UART baud: 1200–19200 bps (auto-baud)
- SPI clock: 400 kHz–10 MHz
- Multi-drop: up to 4 devices (A0/A1 address pins)
- PCB size: 38.1 × 27.9 mm

## Resources
- Schematic & PCB: https://github.com/whatnick/V93XX_Breakout
- Arduino library: https://github.com/whatnick/V93XX_Arduino`,
  tags: ['energy-monitor', 'energy-ic', 'breakout', 'uart', 'spi', 'open-source', 'open-hardware'],
  openHardware: true,
  openSource: true,
};

// ── Config ────────────────────────────────────────────────────────────────────
const TINDIE_USER = process.env.TINDIE_USER;
const TINDIE_PASS = process.env.TINDIE_PASS;

if (!TINDIE_USER || !TINDIE_PASS) {
  console.error('Error: Set TINDIE_USER and TINDIE_PASS environment variables.');
  process.exit(1);
}

// ── Main ──────────────────────────────────────────────────────────────────────
(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 80 });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  // 1. Log in
  console.log('Logging in to Tindie...');
  await page.goto('https://www.tindie.com/accounts/login/');
  await page.fill('input[name="login"]', TINDIE_USER);
  await page.fill('input[name="password"]', TINDIE_PASS);
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard/**', { timeout: 15000 });
  console.log('Logged in ✓');

  // 2. Navigate to create product form
  console.log('Navigating to product create form...');
  await page.goto('https://www.tindie.com/products/create/');
  await page.waitForLoadState('networkidle');

  // 3. Fill in product name
  console.log('Filling product name...');
  await page.fill('input[name="title"], input[id*="title"], input[placeholder*="name" i]', PRODUCT.name);

  // 4. Category — select from dropdown
  const categorySelect = page.locator('select[name="category"], select[id*="category"]');
  if (await categorySelect.count()) {
    await categorySelect.selectOption({ value: PRODUCT.category });
    console.log('Category set ✓');
  } else {
    console.warn('⚠ Could not find category dropdown — set manually.');
  }

  // 5. Price
  await page.fill('input[name="unit_price"], input[id*="price"]', PRODUCT.price);
  console.log('Price set ✓');

  // 6. Quantity / stock
  const qtyField = page.locator('input[name="quantity"], input[id*="quantity"], input[id*="stock"]');
  if (await qtyField.count()) {
    await qtyField.fill(PRODUCT.quantity);
    console.log('Quantity set ✓');
  }

  // 7. Description — try common rich-text and plain textarea selectors
  const descTextarea = page.locator('textarea[name="description"], textarea[id*="description"]');
  const descIframe   = page.frameLocator('iframe.ql-editor, iframe[id*="description"]');

  if (await descTextarea.count()) {
    await descTextarea.fill(PRODUCT.description);
    console.log('Description set (textarea) ✓');
  } else {
    // Try contenteditable inside an iframe (e.g. Quill / TinyMCE)
    try {
      const editorFrame = page.frameLocator('iframe').first();
      const body = editorFrame.locator('body');
      await body.click();
      await body.fill(PRODUCT.description);
      console.log('Description set (iframe editor) ✓');
    } catch {
      console.warn('⚠ Could not fill description automatically — paste it manually.');
    }
  }

  // 8. Open-hardware / open-source checkboxes
  for (const selector of ['input[name="open_hardware"]', 'input[id*="open_hardware"]']) {
    const cb = page.locator(selector);
    if (await cb.count() && PRODUCT.openHardware) {
      await cb.check();
      console.log('Open hardware checked ✓');
      break;
    }
  }
  for (const selector of ['input[name="open_code"]', 'input[id*="open_code"]']) {
    const cb = page.locator(selector);
    if (await cb.count() && PRODUCT.openSource) {
      await cb.check();
      console.log('Open source checked ✓');
      break;
    }
  }

  // 9. Tags — enter one at a time if there is a tag input
  const tagInput = page.locator('input[name*="tag"], input[id*="tag"], input[placeholder*="tag" i]');
  if (await tagInput.count()) {
    for (const tag of PRODUCT.tags) {
      await tagInput.fill(tag);
      await page.keyboard.press('Enter');
      await page.waitForTimeout(300);
    }
    console.log('Tags entered ✓');
  } else {
    console.warn('⚠ No tag input found — add tags manually:', PRODUCT.tags.join(', '));
  }

  // 10. Pause for review before submitting
  console.log('\n✅ Form filled. Review the page in the browser window.');
  console.log('   Add a product image, then press ENTER here to submit, or Ctrl+C to cancel.\n');
  await new Promise(resolve => process.stdin.once('data', resolve));

  // 11. Submit
  const submitBtn = page.locator('button[type="submit"], input[type="submit"]').last();
  await submitBtn.click();
  console.log('Submitted — waiting for redirect...');

  await page.waitForURL(/\/products\/whatnick\//, { timeout: 20000 });
  const newUrl = page.url();
  console.log('\n🎉 Product listed successfully!');
  console.log('   URL:', newUrl);

  // Extract product ID from URL for YAML update
  const idMatch = newUrl.match(/\/products\/whatnick\/[^/]+\/(\d+)/);
  if (idMatch) {
    console.log('\n   Update your YAML:');
    console.log(`   tindie_product_id: "${idMatch[1]}"`);
    console.log('   File: products/v9381-breakout.yaml');
  }

  await browser.close();
})();
