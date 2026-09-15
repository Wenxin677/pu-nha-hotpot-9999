// element-level screenshots: tables, forms and the footer, at their own size
import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..', '..');
const OUT = path.join(ROOT, 'tools', 'imgwork', 'shots');
fs.mkdirSync(OUT, { recursive: true });

const browser = await puppeteer.launch({
  executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  headless: 'new',
});
const page = await browser.newPage();
await page.setViewport({ width: 1280, height: 1000 });

const jobs = [
  ['franchising-requirements.html', '.table-wrap', 'el-investment-table.png', 0],
  ['franchising-requirements.html', '.table-wrap', 'el-standards-table.png', 1],
  ['locations.html', '.table-wrap', 'el-branch-table.png', 0],
  ['contact.html', '.table-wrap', 'el-hours-table.png', 0],
  ['index.html', '#booking-form', 'el-booking-form.png', 0],
  ['index.html', '.site-footer .socials', 'el-socials.png', 0],
  ['about-history.html', '.timeline', 'el-timeline.png', 0],
  ['franchising-faq.html', '.faq', 'el-faq.png', 0],
];

for (const [file, selector, name, index] of jobs) {
  await page.goto(pathToFileURL(path.join(ROOT, file)).href, { waitUntil: 'load' });
  await page.evaluate(() => new Promise((r) => setTimeout(r, 500)));
  const handle = await page.evaluateHandle((sel, i) => document.querySelectorAll(sel)[i], selector, index);
  const el = handle.asElement();
  if (!el) { console.log('missing', selector, 'in', file); continue; }
  await el.screenshot({ path: path.join(OUT, name) });
  console.log('shot', name);
}

await browser.close();
