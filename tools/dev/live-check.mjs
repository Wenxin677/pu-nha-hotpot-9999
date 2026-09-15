// verify the deployed site, not the working copy
import puppeteer from 'puppeteer-core';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..', '..');
const BASE = 'https://wenxin677.github.io/pu-nha-hotpot-9999/';
const PAGES = ['index.html', 'about-history.html', 'locations.html',
               'franchising-faq.html', 'franchising-requirements.html', 'contact.html'];

const browser = await puppeteer.launch({ executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', headless: 'new' });
const problems = [];
for (const file of PAGES) {
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push('pageerror ' + e.message));
  page.on('response', (r) => { if (r.status() >= 400 && r.url().startsWith(BASE)) errs.push(r.status() + ' ' + r.url()); });
  await page.setViewport({ width: 1280, height: 900 });
  await page.goto(BASE + file, { waitUntil: 'load', timeout: 60000 });
  // force lazy images to load, then wait until every one has actually finished
  await page.evaluate(async () => {
    document.querySelectorAll('img[loading="lazy"]').forEach((i) => { i.loading = 'eager'; });
    const imgs = [...document.images];
    await Promise.all(imgs.map((i) => (i.complete && i.naturalWidth)
      ? Promise.resolve()
      : new Promise((res) => { i.addEventListener('load', res, { once: true }); i.addEventListener('error', res, { once: true }); })));
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise((r) => setTimeout(r, 400));
    window.scrollTo(0, 0);
  });
  try { await page.waitForFunction(() => [...document.images].every((i) => i.complete), { timeout: 45000 }); }
  catch { /* reported below as broken images */ }
  const facts = await page.evaluate(() => ({
    title: document.title,
    broken: [...document.images].filter((i) => !i.complete || i.naturalWidth === 0).map((i) => i.currentSrc || i.src),
    fontOK: document.fonts.check('700 16px "Baloo 2"'),
    h1: document.querySelector('h1')?.textContent.trim().slice(0, 46),
  }));
  if (facts.broken.length) problems.push(`${file}: broken images ${facts.broken.join(', ')}`);
  if (!facts.fontOK) problems.push(`${file}: webfont did not load`);
  if (errs.length) problems.push(`${file}: ${errs.slice(0, 3).join(' | ')}`);
  console.log(`${file}: "${facts.title.slice(0, 44)}" h1="${facts.h1}" font=${facts.fontOK} problems=${errs.length + facts.broken.length}`);
  await page.close();
}
await browser.close();
console.log('\n--- live site problems ---');
console.log(problems.length ? problems.join('\n') : 'none');
