# Pu Nha Hotpot 9999 — website

A responsive, six-page website for **Pu Nha Hotpot 9999**, an all-you-can-eat hotpot
restaurant chain in Phnom Penh and Siem Reap, Cambodia.

Built for **INFO 250 — Web Development I (Fall 2026) Final Project**.

**Team:** Sok Panha · Soy Chungtak · So Kunpichethirak · Te Kimmeng

---

## Open the site

* Online: `https://wenxin677.github.io/pu-nha-hotpot-9999/`
* Offline: download the folder and open `index.html` in any browser — every page,
  image, icon, stylesheet and script uses relative paths, so the whole site works
  straight from disk with no server.

## Pages

| File | Section | What is on it |
| --- | --- | --- |
| `index.html` | Home | Hero, ticker, statistics, about, nine menu cards, how-it-works, booking form, reviews |
| `about-history.html` | About Us › History | Brand story, 2012–2026 timeline, embedded video and audio, photo gallery |
| `locations.html` | About Us › Locations | Five branch cards, branch comparison table, map, transport notes |
| `franchising-faq.html` | Franchising › FAQs | Fourteen-question accordion in three parts, plus a product photo band |
| `franchising-requirements.html` | Franchising › Requirements | Investment-package table, operating-standards table, application steps, support list |
| `contact.html` | Contacts | Contact cards, social links, contact form, opening-hours table, map |

Every page shares the same header (`Home · About Us ▾ · Franchising ▾ · Contacts · Book a table`)
and the same footer, assembled from one source so they can never drift apart.

## Folder structure

```
index.html  about-history.html  locations.html
franchising-faq.html  franchising-requirements.html  contact.html
style.css                  one external stylesheet for the whole site
js/main.js                 navigation, dropdowns, form validation, accordion, reveal
assets/img/                photographs (re-encoded, credited in CREDITS.md)
assets/ill/                original SVG illustrations (steam, flames, temples, menu icons)
assets/logos/              logo + favicon set generated from the mascot artwork
assets/audio/              generated ambience clip used by the history page
tools/                     build and verification scripts (not part of the site itself)
tools/pages/               page bodies that the assembler wraps in the shared shell
tools/dev/                 headless-browser checks (Puppeteer)
CREDITS.md                 every photo, its author and its licence
```

## Rebuild, verify, re-check

```bash
python tools/make_images.py          # photos + logo/favicon set from tools/imgwork and tools/artwork
python tools/make_illustrations.py   # original SVG illustrations (validates each file as XML)
python tools/make_audio.py           # the ambience clip (standard library only)
python tools/build_pages.py          # wraps tools/pages/*.main.html in the shared header/footer
python tools/verify_site.py          # links, assets, rubric checklist, shared-shell drift
cd tools/dev && node browser-check.mjs        # real-browser layout + behaviour tests
cd tools/dev && node element-shots.mjs        # close-up screenshots of tables, forms, footer
```

`verify_site.py` fails the build if any page is missing a rubric item, if a link or
asset stops resolving, or if a page's header/footer differs from the shared shell.

## Technical requirements covered

* HTML5 doctype, `lang`, one `<h1>` per page, semantic `header / nav / main / section / article / footer`
* One external stylesheet (`style.css`) with an `@import` for the Google Fonts pairing
  (Baloo 2 for display, Inter for text) and all type, colour, spacing and radius values
  held in CSS custom properties
* Ordered and unordered lists, four data tables (with `<caption>`, `<thead>`, `scope`
  attributes and zebra striping), two forms with `<fieldset>`/`<legend>` grouping and
  `date`, `time`, `tel`, `email`, `number`, radio and checkbox inputs
* An embedded YouTube video **and** an `<audio>` element (both on the history page)
* Layout built with CSS Grid (menu, branches, stats, forms) and Flexbox (nav, footer, buttons)
* Link states for `:link`, `:visited`, `:hover`, `:active` and `:focus-visible`
* Four media queries (1024 / 880 / 600 px plus `prefers-reduced-motion`); the navigation
  collapses into a pure-CSS mobile menu that JavaScript progressively enhances
* Relative units throughout (`rem`, `em`, `%`, `vw`, `clamp()`), plus transitions,
  keyframes, hover lifts and scroll-reveal animations for polish

## Notes

* The booking and contact forms are front-end demonstrations: they validate input and show a
  confirmation in the browser, but there is no server, so nothing is transmitted anywhere.
  The pages say so in plain language next to the buttons.
* Pu Nha Hotpot 9999 is the business described in the team's project proposal; phone numbers,
  addresses and franchise figures are the illustrative ones used for this coursework.
* Every photograph on the site was generated for this project with Stable Diffusion XL
  running locally (ComfyUI) — the exact prompt and seed for each image is recorded in
  `tools/ai/prompts.json` and `CREDITS.md`, so any picture can be regenerated. The mascot
  logo is the team's own artwork and was used to generate the favicon set; the illustrations
  in `assets/ill/`, the ambience clip and every other asset are original work done for this site.
