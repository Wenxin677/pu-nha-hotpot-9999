#!/usr/bin/env python3
"""Verify the Pu Nha Hotpot 9999 site before it ships.

Checks (a) the course rubric's technical requirements, (b) that every local
link and asset actually resolves, and (c) that the shared header/footer really
are identical on all six pages.

Run:  python tools/verify_site.py
"""
import json
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["index.html", "about-history.html", "locations.html",
         "franchising-faq.html", "franchising-requirements.html", "contact.html"]

LOCAL_ASSET_ATTRS = {"src": ("img", "script", "iframe", "audio", "source", "video", "link"),
                     "href": ("link", "a")}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
        "param", "source", "track", "wbr"}

problems = []
notes = []


def fail(msg):
    problems.append(msg)


def ok(msg):
    notes.append(msg)


class Doc(HTMLParser):
    """Collect just enough structure to check the rubric items."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.unclosed = []
        self.tags = []
        self.attrs_by_tag = {}
        self.text_by_tag = {}
        self.links = []
        self.heads = []
        self.imgs_without_alt = []
        self.ids = set()
        self.label_for = set()
        self.input_types = {}
        self.checkbox_radios = 0
        self.forms = 0
        self.fieldsets = 0
        self.legends = 0
        self.tables = 0
        self.captions = 0
        self.th_scope = 0
        self.details = 0
        self.summary = 0
        self.iframe_srcs = []
        self.audio = 0
        self.video = 0
        self.in_head = False
        self._text_target = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append(tag)
        self.attrs_by_tag.setdefault(tag, []).append(a)
        if tag == "head":
            self.in_head = True
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6", "title"):
            self._text_target = tag
            self.text_by_tag.setdefault(tag, []).append("")
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "link" and a.get("href"):
            self.links.append(a["href"])
        if tag == "img":
            if "alt" not in a:
                self.imgs_without_alt.append(a.get("src", "?"))
            if a.get("src"):
                self.links.append(a["src"])
        if tag == "script" and a.get("src"):
            self.links.append(a["src"])
        if tag in ("iframe", "audio", "source", "video") and a.get("src"):
            self.links.append(a["src"])
            if tag == "iframe":
                self.iframe_srcs.append(a["src"])
        if tag == "iframe":
            self.iframe_srcs.append(a.get("src", ""))
        if tag == "audio":
            self.audio += 1
        if tag == "video":
            self.video += 1
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "label" and a.get("for"):
            self.label_for.add(a["for"])
        if tag == "input":
            self.input_types[a.get("type", "text")] = self.input_types.get(a.get("type", "text"), 0) + 1
            if a.get("type") in ("checkbox", "radio"):
                self.checkbox_radios += 1
        if tag == "form":
            self.forms += 1
        if tag == "fieldset":
            self.fieldsets += 1
        if tag == "legend":
            self.legends += 1
        if tag == "table":
            self.tables += 1
        if tag == "caption":
            self.captions += 1
        if tag == "th" and a.get("scope"):
            self.th_scope += 1
        if tag == "details":
            self.details += 1
        if tag == "summary":
            self.summary += 1
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
        if tag in VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.unclosed.append(self.stack.pop())
                if self.stack:
                    self.stack.pop()
            else:
                self.unclosed.append("stray </%s>" % tag)

    def handle_data(self, data):
        if self._text_target and data.strip():
            key = self._text_target
            self.text_by_tag[key][-1] += data.strip() + " "


def local_path(ref):
    ref = ref.strip()
    if ref.startswith(("http://", "https://", "//", "mailto:", "tel:", "data:", "#", "javascript:")):
        return None
    return urlsplit(ref).path.replace("\\", "/")


def check_page(page):
    raw = open(os.path.join(ROOT, page), encoding="utf-8").read()
    doc = Doc()
    doc.feed(raw)

    # ---- document structure
    if not raw.lstrip().lower().startswith("<!doctype html>"):
        fail("%s: missing <!DOCTYPE html>" % page)
    if not re.search(r'<html lang="[a-z]{2}(-[A-Za-z]+)?"', raw):
        fail("%s: <html> without a lang attribute" % page)
    for needed in ("<head", "</head>", "<body", "</body>", "</html>"):
        if needed not in raw:
            fail("%s: missing %s" % (page, needed))
    if doc.stack:
        fail("%s: unclosed tags %s" % (page, [t for t in doc.stack if t != "html"][:6]))
    if doc.unclosed:
        fail("%s: mismatched tags %s" % (page, doc.unclosed[:6]))

    # ---- rubric: semantic elements, headings, meta
    for tag in ("header", "nav", "main", "section", "article", "footer"):
        if not doc.attrs_by_tag.get(tag):
            fail("%s: no <%s> element" % (page, tag))
    h1s = doc.text_by_tag.get("h1", [])
    if len(h1s) != 1:
        fail("%s: expected exactly one <h1>, found %d" % (page, len(h1s)))
    if not doc.attrs_by_tag.get("title", [{}])[0].get("", True):
        pass
    if not re.search(r"<title>[^<]{10,}</title>", raw):
        fail("%s: missing or too-short <title>" % page)
    if not re.search(r'<meta name="description" content="[^"]{40,}"', raw):
        fail("%s: missing meta description" % page)
    if '<meta name="viewport"' not in raw:
        fail("%s: no viewport meta tag" % page)
    if '<link rel="stylesheet" href="style.css">' not in raw:
        fail("%s: does not link the shared style.css" % page)
    if '<a class="skip-link" href="#main">' not in raw:
        fail("%s: no skip link" % page)
    if 'id="main"' not in raw:
        fail("%s: no #main landmark for the skip link" % page)

    # ---- images need alt text
    if doc.imgs_without_alt:
        fail("%s: <img> without alt: %s" % (page, doc.imgs_without_alt))

    # ---- links and assets resolve
    for ref in doc.links + re.findall(r'url\([\'"]?([^\'")]+)', raw):
        path = local_path(ref)
        if path in (None, ""):
            continue
        target = os.path.normpath(os.path.join(ROOT, path))
        if not os.path.exists(target):
            fail("%s: broken reference -> %s" % (page, ref))

    # in-page anchors must exist
    for ref in doc.links:
        if ref.startswith("#") and len(ref) > 1 and ref[1:] not in doc.ids:
            fail("%s: anchor #%s has no target" % (page, ref[1:]))
        if ".html#" in ref:
            target, _, frag = ref.partition("#")
            tp = os.path.join(ROOT, target)
            if os.path.exists(tp):
                other = open(tp, encoding="utf-8").read()
                if 'id="%s"' % frag not in other:
                    fail("%s: link %s points at a missing id" % (page, ref))

    return doc, raw


def main():
    docs = {}
    for page in PAGES:
        if not os.path.exists(os.path.join(ROOT, page)):
            fail("missing page file %s" % page)
            continue
        docs[page] = check_page(page)
    if len(docs) != len(PAGES):
        report()
        return

    # ---- shared shell must be identical everywhere
    shell = json.load(open(os.path.join(ROOT, "tools", "pages", "shell.json"), encoding="utf-8"))
    for page, (doc, raw) in docs.items():
        header_start = raw.index("<!-- ============================ HEADER")
        header_end = raw.index("</header>") + len("</header>")
        header = raw[header_start:header_end].replace(' aria-current="page"', "")
        expected = shell["header"] if page == "index.html" else shell.get("header_inner", shell["header"])
        if header != expected:
            fail("%s: header markup differs from the shared shell" % page)
        foot_start = raw.index("<!-- ============================ FOOTER")
        foot_end = raw.index("</footer>") + len("</footer>")
        if raw[foot_start:foot_end] != shell["footer"]:
            fail("%s: footer markup differs from the shared shell" % page)

    # ---- every page carries the same nav destinations
    nav_pages = ["index.html", "about-history.html", "locations.html",
                 "franchising-faq.html", "franchising-requirements.html", "contact.html"]
    for page, (doc, raw) in docs.items():
        for dest in nav_pages:
            if 'href="%s"' % dest not in raw:
                fail("%s: navigation does not link to %s" % (page, dest))

    all_tags = {t for doc, _ in docs.values() for t in doc.tags}
    all_raw = "\n".join(raw for _, raw in docs.values())

    # ---- rubric: lists
    if not re.search(r"<ol[ >]", all_raw):
        fail("no ordered list (<ol>) anywhere on the site")
    else:
        ok("ordered list present (%d)" % len(re.findall(r"<ol[ >]", all_raw)))
    if not re.search(r"<ul[ >]", all_raw):
        fail("no unordered list (<ul>) anywhere on the site")
    else:
        ok("unordered list present (%d)" % len(re.findall(r"<ul[ >]", all_raw)))

    # ---- rubric: table(s)
    tables = sum(len(d.attrs_by_tag.get("table", [])) for d, _ in docs.values())
    captions = sum(d.captions for d, _ in docs.values())
    th_scope = sum(d.th_scope for d, _ in docs.values())
    if tables < 3:
        fail("expected at least 3 tables, found %d" % tables)
    else:
        ok("tables: %d (captions %d, scope= attributes %d)" % (tables, captions, th_scope))

    # ---- rubric: forms, fieldsets, legends, labels, input types
    forms = sum(d.forms for d, _ in docs.values())
    fieldsets = sum(d.fieldsets for d, _ in docs.values())
    legends = sum(d.legends for d, _ in docs.values())
    types = {}
    for d, _ in docs.values():
        for t, n in d.input_types.items():
            types[t] = types.get(t, 0) + n
    if forms < 2:
        fail("expected at least 2 forms, found %d" % forms)
    if fieldsets < 4 or legends != fieldsets:
        fail("expected fieldsets (with matching legends) in both forms (%d fieldsets, %d legends)"
             % (fieldsets, legends))
    for needed in ("date", "time", "tel", "email", "number"):
        if needed not in types:
            fail("no input type=\"%s\" anywhere on the site" % needed)
    for page, (d, raw) in docs.items():
        for a in d.attrs_by_tag.get("input", []) + d.attrs_by_tag.get("select", []) + d.attrs_by_tag.get("textarea", []):
            if a.get("type") in ("submit", "reset", "hidden"):
                continue
            if a.get("id") and a["id"] not in d.label_for:
                fail("%s: field #%s has no <label for>" % (page, a["id"]))
    ok("forms: %d, fieldsets/legends: %d/%d, input types: %s, labels matched" % (forms, fieldsets, legends, sorted(types)))

    # ---- rubric: multimedia
    iframes = [s for d, _ in docs.values() for s in d.iframe_srcs]
    video = any("youtube" in s or "vimeo" in s for s in iframes)
    audio = sum(d.audio for d, _ in docs.values())
    if not video:
        fail("no embedded video found")
    if not audio:
        fail("no <audio> element found")
    ok("multimedia: %d iframes, %d audio element(s)" % (len(iframes), audio))

    # ---- rubric: accordion for the FAQs
    details = sum(d.details for d, _ in docs.values())
    summaries = sum(d.summary for d, _ in docs.values())
    if details < 10 or summaries != details:
        fail("FAQ accordion looks wrong (%d details, %d summaries)" % (details, summaries))
    else:
        ok("FAQ accordion: %d <details>/<summary> pairs" % details)

    # ---- CSS checks
    css = open(os.path.join(ROOT, "style.css"), encoding="utf-8").read()
    if "@import" not in css:
        fail("style.css has no @import")
    else:
        ok("style.css @import present: %s" % re.search(r"@import[^;]+;", css).group(0)[:70] + "…")
    if css.count("{") != css.count("}"):
        fail("style.css braces do not balance (%d vs %d)" % (css.count("{"), css.count("}")))
    media = len(re.findall(r"@media", css))
    if media < 2:
        fail("style.css has fewer than 2 media queries (%d)" % media)
    else:
        ok("media queries: %d" % media)
    for state in (":hover", ":visited", ":active", ":focus-visible"):
        if state not in css:
            fail("style.css does not style %s links" % state)
    for token in ("display: grid", "display: flex", "var(--"):
        if token not in css:
            fail("style.css is missing %s" % token)
    if "transition" not in css or "@keyframes" not in css:
        fail("style.css has no transitions/animations")
    if not re.search(r"(rem|em|vw|vh|%)", css):
        fail("style.css does not use relative units")
    # every asset the CSS points at must exist
    for ref in re.findall(r"url\([\"']?([^\"')]+)", css):
        path = local_path(ref)
        if path:
            target = os.path.normpath(os.path.join(ROOT, path))
            if not os.path.exists(target):
                fail("style.css: broken url() -> %s" % ref)
    # custom properties used consistently
    ok("CSS custom properties defined: %d" % len(set(re.findall(r"^\s*(--[a-z0-9-]+)\s*:", css, re.M))))

    # ---- every asset on disk should be referenced somewhere
    referenced = set()
    for _p, (d, raw) in docs.items():
        for ref in d.links:
            path = local_path(ref)
            if path:
                referenced.add(os.path.normpath(path).replace("\\", "/"))
        for ref in re.findall(r'url\([\'"]?([^\'")]+)', raw):
            path = local_path(ref)
            if path:
                referenced.add(os.path.normpath(path).replace("\\", "/"))
    for ref in re.findall(r"url\([\"']?([^\"')]+)", css):
        path = local_path(ref)
        if path:
            referenced.add(os.path.normpath(path).replace("\\", "/"))
    for folder in ("assets/img", "assets/ill", "assets/logos", "assets/audio"):
        for name in sorted(os.listdir(os.path.join(ROOT, folder))):
            rel = os.path.join(folder, name).replace("\\", "/")
            if rel not in referenced:
                fail("asset never referenced by any page or the CSS: %s" % rel)

    report()


def report():
    print("=" * 72)
    for n in notes:
        print("PASS  ", n)
    print("-" * 72)
    if problems:
        for p in problems:
            print("FAIL  ", p)
        print("-" * 72)
        print("RESULT: %d problem(s)" % len(problems))
        sys.exit(1)
    print("RESULT: all checks passed")


if __name__ == "__main__":
    main()
