/**
 * Real-browser verification for the Pu Nha Hotpot 9999 site.
 *
 * 1. loads every page from disk (file://) and screenshots it at phone,
 *    tablet and desktop widths,
 * 2. drives the interactive parts — mobile menu, dropdowns, form validation,
 *    FAQ accordion — and asserts what actually happened,
 * 3. reports console errors and failed requests.
 *
 * Run:  node tools/dev/browser-check.mjs
 */
import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..', '..');
const SHOTS = path.join(ROOT, 'tools', 'imgwork', 'shots');
fs.mkdirSync(SHOTS, { recursive: true });

const CHROME = ['C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe']
  .find((p) => fs.existsSync(p));

const PAGES = ['index.html', 'about-history.html', 'locations.html',
               'franchising-faq.html', 'franchising-requirements.html', 'contact.html'];
const WIDTHS = [{ name: 'desktop', w: 1280, h: 900 },
                { name: 'tablet', w: 900, h: 900 },
                { name: 'phone', w: 512, h: 900 }];

const errors = [];
const results = [];
const shot = (p) => pathToFileURL(path.join(ROOT, p)).href;

const browser = await puppeteer.launch({ executablePath: CHROME, headless: 'new', args: ['--allow-file-access-from-files'] });

for (const file of PAGES) {
  const page = await browser.newPage();
  const pageErrors = [];
  page.on('pageerror', (e) => pageErrors.push('pageerror: ' + e.message));
  page.on('requestfailed', (r) => {
    const url = r.url();
    // only our own files matter; the YouTube embed phones home and may be blocked
    if (url.startsWith('file://')) pageErrors.push('requestfailed: ' + url.slice(0, 90));
  });

  await page.setViewport({ width: 1280, height: 900 });
  await page.goto(shot(file), { waitUntil: 'load', timeout: 60000 });
  await page.evaluate(() => new Promise((r) => setTimeout(r, 700)));

  // lazy images are "not loaded" until scrolled into view: force them, then settle
  await page.evaluate(async () => {
    document.querySelectorAll('img[loading="lazy"]').forEach((i) => { i.loading = 'eager'; });
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise((r) => setTimeout(r, 900));
    window.scrollTo(0, 0);
    await new Promise((r) => setTimeout(r, 300));
  });

  // ---------- layout facts that only a real browser knows
  const facts = await page.evaluate(() => {
    const h = document.querySelector('h1');
    const cards = document.querySelectorAll('.card, .branch, .contact-card');
    const wide = document.documentElement.scrollWidth > document.documentElement.clientWidth + 1;
    return {
      title: document.title,
      h1: h ? h.textContent.trim().slice(0, 60) : null,
      docHeight: document.documentElement.scrollHeight,
      overflowX: wide,
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
      images: [...document.images].filter((i) => !i.complete || i.naturalWidth === 0).map((i) => i.currentSrc || i.src),
      fontLoaded: document.fonts ? document.fonts.check('700 16px "Baloo 2"') : null,
      visibleCards: [...cards].filter((c) => c.getBoundingClientRect().height > 40).length,
      skipLink: !!document.querySelector('.skip-link'),
      toTop: !!document.querySelector('#to-top'),
      menuVisible: (() => {
        const m = document.querySelector('.menu');
        return m ? getComputedStyle(m).display : null;
      })(),
      cssVarsApplied: getComputedStyle(document.documentElement).getPropertyValue('--red').trim(),
    };
  });

  if (facts.overflowX) errors.push(`${file}: horizontal overflow (scrollWidth ${facts.scrollWidth} > clientWidth ${facts.clientWidth})`);
  if (facts.images.length) errors.push(`${file}: broken images -> ${facts.images.join(', ')}`);
  if (!facts.cssVarsApplied) errors.push(`${file}: design tokens not applied`);
  if (pageErrors.length) errors.push(`${file}: ${pageErrors.join(' | ')}`);

  results.push({ file, ...facts, errors: pageErrors.length });

  // ---------- viewport screenshots (never full-page: a sticky header mispaints there)
  const stem = file.replace('.html', '');
  await page.setViewport({ width: 1280, height: 900 });
  const total = await page.evaluate(() => document.documentElement.scrollHeight);
  const offsets = [];
  for (let y = 0; y < total - 900; y += 880) { offsets.push(y); }
  offsets.push(Math.max(0, total - 900));                 // always include the very bottom
  for (let t = 0; t < offsets.length; t += 1) {
    await page.evaluate((y) => window.scrollTo(0, y), offsets[t]);
    await page.evaluate(() => new Promise((r) => setTimeout(r, 320)));
    await page.screenshot({ path: path.join(SHOTS, `${stem}-desk${t + 1}.png`) });
  }
  await page.evaluate(() => window.scrollTo(0, 0));
  for (const size of WIDTHS.filter((s) => s.name !== 'desktop')) {
    await page.setViewport({ width: size.w, height: size.h });
    await page.evaluate(() => new Promise((r) => setTimeout(r, 300)));
    await page.screenshot({ path: path.join(SHOTS, `${stem}-${size.name}.png`) });
  }

  // ---------- behaviour: mobile menu
  await page.setViewport({ width: 480, height: 900 });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.evaluate(() => new Promise((r) => setTimeout(r, 250)));
  const burger = await page.$('.nav__burger');
  const menuBefore = await page.$eval('.menu', (m) => getComputedStyle(m).display);
  if (burger) {
    await burger.click();
    await page.evaluate(() => new Promise((r) => setTimeout(r, 350)));
  }
  const menuAfter = await page.$eval('.menu', (m) => getComputedStyle(m).display);
  if (menuBefore !== 'none') errors.push(`${file}: mobile menu was already open at 480px (${menuBefore})`);
  if (menuAfter === 'none') errors.push(`${file}: burger did not open the mobile menu`);
  await page.screenshot({ path: path.join(SHOTS, `${file.replace('.html', '')}-menu-open.png`), fullPage: false });

  // ---------- behaviour: dropdown
  await page.setViewport({ width: 1280, height: 900 });
  await page.evaluate(() => { document.querySelector('.nav__toggle').checked = false; });
  const drop = await page.$('.drop');
  if (drop) {
    const panelBefore = await page.$eval('.drop .drop__panel', (p) => p.getBoundingClientRect().height);
    await drop.hover();
    await page.evaluate(() => new Promise((r) => setTimeout(r, 400)));
    const panelAfter = await page.$eval('.drop', (d) => d.open);
    if (!panelAfter) errors.push(`${file}: dropdown did not open on hover`);
    if (panelBefore > 2) errors.push(`${file}: dropdown panel visible while closed`);
  }

  // ---------- behaviour: forms
  if (file === 'index.html' || file === 'contact.html') {
    const formId = file === 'index.html' ? '#booking-form' : '#message-form';
    const statusId = file === 'index.html' ? '#booking-status' : '#message-status';
    await page.$eval(`${formId} input[type="submit"], ${formId} button[type="submit"]`, (b) => b.click());
    await page.evaluate(() => new Promise((r) => setTimeout(r, 300)));
    const emptyState = await page.evaluate((id) => {
      const s = document.querySelector(id);
      const bad = [...document.querySelectorAll('[aria-invalid="true"]')].map((el) => el.id || el.name);
      return { visible: s && getComputedStyle(s).display !== 'none', text: s ? s.textContent.trim().slice(0, 60) : '', bad: bad.length, badFields: bad };
    }, statusId);
    if (!emptyState.visible || emptyState.bad === 0) {
      errors.push(`${file}: submitting the empty form did not raise field errors (invalid=${emptyState.bad} ${emptyState.badFields})`);
    }

    // fill it properly and submit again
    await page.evaluate((id) => {
      const form = document.querySelector(id);
      const set = (sel, val) => { const el = form.querySelector(sel); if (el) { el.value = val; el.dispatchEvent(new Event('input', { bubbles: true })); } };
      set('input[type="text"]', 'Sok Panha');
      set('input[type="email"]', 'panha@example.com');
      set('input[type="tel"]', '+855 12 345 678');
      set('input[type="number"]', '4');
      set('select', form.querySelector('select option:nth-child(2)') ? form.querySelector('select').options[1].value : '');
      set('textarea', 'Table for four near the buffet line, one vegan broth, please.');
      form.querySelectorAll('input[type="checkbox"]').forEach((c) => { c.checked = true; });
    }, formId);
    await page.$eval(`${formId} input[type="submit"], ${formId} button[type="submit"]`, (b) => b.click());
    await page.evaluate(() => new Promise((r) => setTimeout(r, 300)));
    const okState = await page.evaluate((id) => {
      const s = document.querySelector(id);
      const bad = [...document.querySelectorAll('[aria-invalid="true"]')].map((el) => el.id || el.name);
      return { visible: s && getComputedStyle(s).display !== 'none', cls: s ? s.className : '',
               text: s ? s.textContent.trim().slice(0, 90) : '', badFields: bad };
    }, statusId);
    if (!okState.visible || !okState.cls.includes('ok')) {
      errors.push(`${file}: a complete ${formId} submission was not accepted (${JSON.stringify(okState).slice(0, 120)})`);
    } else {
      results.push({ file, formSuccess: okState.text });
    }
    await page.screenshot({ path: path.join(SHOTS, `${file.replace('.html', '')}-form.png`), fullPage: false });
  }

  // ---------- behaviour: FAQ accordion (one open at a time)
  if (file === 'franchising-faq.html') {
    const state = await page.evaluate(async () => {
      const items = [...document.querySelectorAll('.faq details')];
      items[2].open = true;
      await new Promise((r) => setTimeout(r, 250));
      return { open: items.filter((i) => i.open).length, total: items.length };
    });
    if (state.open !== 1) errors.push(`${file}: FAQ accordion left ${state.open} items open (expected 1 of ${state.total})`);
    results.push({ file, accordion: state });
  }

  await page.close();
}

await browser.close();

console.log('--- page facts ---');
for (const r of results) {
  if (r.h1) console.log(`${r.file}: h1="${r.h1}" height=${r.docHeight} cards=${r.visibleCards} fontLoaded=${r.fontLoaded} menu=${r.menuVisible}`);
  else if (r.formSuccess) console.log(`${r.file}: form success -> ${r.formSuccess}`);
  else if (r.accordion) console.log(`${r.file}: accordion ${JSON.stringify(r.accordion)}`);
}
console.log('\n--- problems ---');
if (errors.length) { errors.forEach((e) => console.log('FAIL ' + e)); process.exitCode = 1; }
else console.log('none');
console.log('\nscreenshots:', SHOTS);
