#!/usr/bin/env python3
"""Assemble the inner pages around the exact header and footer used by
index.html, so every page ships byte-identical navigation and footer markup.

index.html is the source of truth for the shared shell: edit it there, then
re-run this script and the other five pages pick the change up.

Run:  python tools/build_pages.py
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAGMENTS = os.path.join(ROOT, "tools", "pages")

HEAD_MARK = "<!-- ============================ HEADER ============================ -->"
FOOT_MARK = "<!-- ============================ FOOTER ============================ -->"

PAGES = {
    "about-history.html": {
        "title": "Our History — Pu Nha Hotpot 9999",
        "description": "How Pu Nha Hotpot 9999 grew from a six-table family stall on Street 310 "
                       "in 2012 into a five-branch all-you-can-eat hotpot chain across Cambodia.",
        "active": ["about-history.html"],
        "fragment": "about-history.main.html",
    },
    "locations.html": {
        "title": "Locations & Opening Hours — Pu Nha Hotpot 9999",
        "description": "All five Pu Nha Hotpot 9999 branches in Cambodia: addresses, opening hours, "
                       "seating capacity, parking and Google Maps links for Phnom Penh and Siem Reap.",
        "active": ["locations.html"],
        "fragment": "locations.main.html",
    },
    "franchising-faq.html": {
        "title": "Franchise FAQs — Pu Nha Hotpot 9999",
        "description": "Frequently asked questions about franchising with Pu Nha Hotpot 9999: cost, "
                       "royalty fees, space, training, support and contract length.",
        "active": ["franchising-faq.html"],
        "fragment": "franchising-faq.main.html",
    },
    "franchising-requirements.html": {
        "title": "Franchise Requirements — Pu Nha Hotpot 9999",
        "description": "Investment packages, floor area, staff numbers and operating standards for "
                       "opening a Pu Nha Hotpot 9999 franchise in Cambodia, plus the application steps.",
        "active": ["franchising-requirements.html"],
        "fragment": "franchising-requirements.main.html",
    },
    "contact.html": {
        "title": "Contacts — Pu Nha Hotpot 9999",
        "description": "Phone numbers, email addresses, social media and opening hours for "
                       "Pu Nha Hotpot 9999, plus a contact form for groups, franchising and feedback.",
        "active": ["contact.html"],
        "fragment": "contact.main.html",
    },
}


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def slice_between(text, start_mark, end_mark):
    start = text.index(start_mark)
    end = text.index(end_mark, start) + len(end_mark)
    return text[start:end]


def main():
    index = read(os.path.join(ROOT, "index.html"))
    header = slice_between(index, HEAD_MARK, "</header>")
    footer = slice_between(index, FOOT_MARK, "</footer>")

    # the shell is stored without any active-page state; each page adds its own
    header_clean = header.replace(' aria-current="page"', "")
    assert 'aria-current="page"' not in header_clean
    # the header CTA scrolls to the booking form; on inner pages that form lives on index
    header_inner = header_clean.replace('href="#booking"', 'href="index.html#booking"')

    for filename, meta in PAGES.items():
        page_header = header_inner if filename != "index.html" else header_clean
        for href in meta["active"]:
            page_header = page_header.replace('href="%s"' % href, 'href="%s" aria-current="page"' % href)
            if 'href="%s" aria-current' % href not in page_header:
                raise SystemExit("could not mark %s active in %s" % (href, filename))

        body = read(os.path.join(FRAGMENTS, meta["fragment"])).rstrip() + "\n"
        doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{meta['title']}</title>
  <meta name="description" content="{meta['description']}">
  <meta name="theme-color" content="#8E0A1D">
  <link rel="icon" href="assets/logos/favicon.png" type="image/png">
  <link rel="icon" href="assets/logos/favicon.ico" sizes="any">
  <link rel="apple-touch-icon" href="assets/logos/apple-touch-icon.png">
  <link rel="stylesheet" href="style.css">
</head>
<body id="top">
<a class="skip-link" href="#main">Skip to main content</a>

{page_header}

<main id="main">

{body}
</main>

{footer}

<button class="to-top" id="to-top" type="button" aria-label="Back to top">↑</button>
<script src="js/main.js"></script>
</body>
</html>
"""
        out = os.path.join(ROOT, filename)
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(doc)
        print("wrote", filename, len(doc), "chars")

    # record what the shell looked like, so the verifier can detect drift
    with open(os.path.join(ROOT, "tools", "pages", "shell.json"), "w", encoding="utf-8") as fh:
        json.dump({"header": header_clean, "header_inner": header_inner, "footer": footer}, fh, indent=1)
    print("shell recorded for the verifier")


if __name__ == "__main__":
    main()
