#!/usr/bin/env python3
"""Hand-authored flat SVG illustrations in the brand palette: decorative bands
and menu icons.  Towers are generated course-by-course (narrowing tiers with
overhanging cornice lips plus a lotus-bud finial) so they read as Khmer temple
spires rather than plain cones.

Run:  python tools/make_illustrations.py   (validates every file as XML)
"""
import os
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "ill")
os.makedirs(OUT, exist_ok=True)

RED, RED_D, RED_L = "#C8102E", "#8E0A1D", "#E8798C"
GOLD, GOLD_L, GOLD_D = "#F4B400", "#FFD24A", "#C98A12"
CREAM, WHITE, CHAR = "#FFF6E8", "#FFFDF7", "#3A2A22"
GREEN = "#4E9B4A"
BROWN, BROWN_D, BROWN_L = "#D8A863", "#8C6134", "#EBCB95"


def svg(name, w, h, body, title):
    doc = ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           'viewBox="0 0 %d %d" role="img" aria-hidden="true" focusable="false">' % (w, h))
    doc += "<title>%s</title>" % title + body + "</svg>"
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(doc)
    ET.fromstring(doc)                     # a malformed asset must fail here, not in the browser
    if "%s" in doc:
        raise SystemExit("unsubstituted placeholder in " + name)


# ------------------------------------------------------- temple generator ----
def tower(cx, base_y, height, width, fill, tiers=5, cornice=True):
    """Khmer-style spire: narrowing tiers, each with an overhanging lip,
    crowned by a lotus-bud finial."""
    parts, y, tw = [], base_y, width
    tier_h = height * 0.72 / tiers
    for i in range(tiers):
        nw = tw * (0.80 if i < tiers - 1 else 0.55)
        parts.append('<path d="M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZ" fill="%s"/>'
                     % (cx - tw / 2, y, cx + tw / 2, y, cx + nw / 2, y - tier_h, cx - nw / 2, y - tier_h, fill))
        if cornice:
            lip = tw * 0.10
            parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="1.2" fill="%s"/>'
                         % (cx - nw / 2 - lip, y - tier_h - 2.6, nw + lip * 2, 5.2, fill))
        y -= tier_h
        tw = nw
    bud = height * 0.28
    parts.append('<path d="M%.1f %.1fC%.1f %.1f %.1f %.1f %.1f %.1fC%.1f %.1f %.1f %.1f %.1f %.1fZ" fill="%s"/>'
                 % (cx - tw / 2, y, cx - tw / 2 - 2.5, y - bud * 0.55, cx - tw * 0.18, y - bud * 0.86, cx, y - bud,
                    cx + tw * 0.18, y - bud * 0.86, cx + tw / 2 + 2.5, y - bud * 0.55, cx + tw / 2, y, fill))
    return "".join(parts)


def skyline(w, h, towers, ground=RED_D, back=None):
    """towers: list of (cx, base_y, height, width, fill)"""
    out = []
    if back:
        out.append('<g opacity=".70">' + "".join(tower(*t, tiers=4) for t in back) + '</g>')
    out.append("".join(tower(*t, tiers=5) for t in towers))
    out.append('<rect x="0" y="%d" width="%d" height="%d" fill="%s"/>' % (h - 10, w, 10, ground))
    return "".join(out)


# ------------------------------------------------------------------ icons ----
svg("icon-pot.svg", 64, 64, (
    '<g fill="none" stroke="%s" stroke-width="4.2" stroke-linecap="round" opacity=".95">'
    '<path d="M20 16c-5-6 5-9 0-14"/><path d="M32 12c-5-6 5-9 0-14"/><path d="M44 16c-5-6 5-9 0-14"/></g>' % GOLD
    + '<path d="M9 30h46v11a10 10 0 0 1-10 10H19a10 10 0 0 1-10-10z" fill="%s" stroke="%s" stroke-width="3"/>' % (CREAM, RED_D)
    + '<path d="M32 31v20" stroke="%s" stroke-width="3"/>' % RED_D
    + '<rect x="4" y="25" width="56" height="8" rx="4" fill="%s"/>' % RED
    + '<path d="M14 36c4 4 14 4 18 0M32 36c4 4 14 4 18 0" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % GOLD
    + '<circle cx="24" cy="43" r="3" fill="%s"/><circle cx="42" cy="44" r="3" fill="%s"/>' % (GREEN, RED)
), "Divided hotpot")

svg("icon-beef.svg", 64, 64, (
    "".join(
        '<g transform="rotate(%d 34 30)">'
        '<rect x="6" y="%d" width="54" height="14" rx="7" fill="%s" stroke="%s" stroke-width="2"/>'
        '<path d="M8 %d.5h50a7 7 0 0 1 0 3.4H8A7 7 0 0 1 8 %d.5z" fill="%s"/>'
        '<path d="M16 %d.5c7-3.4 13 3.4 20 0 5-2.4 12 2.4 18 0" fill="none" stroke="%s" stroke-width="2.4" stroke-linecap="round"/>'
        '</g>' % (rot, y, body, RED_D, y, y, WHITE, y + 5, WHITE)
        for rot, y, body in [(24, 40, RED_L), (6, 22, RED_L), (-14, 32, RED)]
    )
), "Sliced marbled beef")

svg("icon-shrimp.svg", 64, 64, (
    '<path d="M47 17c-15-6-28 2-28 15 0 9 7 15 16 15" fill="none" stroke="%s" stroke-width="12" stroke-linecap="round"/>' % RED
    + '<path d="M24 28l9-1M22 36l10 1M24 44l9 2" stroke="%s" stroke-width="2.6" stroke-linecap="round"/>' % RED_D
    + '<path d="M47 17l6-6 1 7 8-2-5 6z" fill="%s" stroke="%s" stroke-width="1.6"/>' % (RED_L, RED_D)
    + '<path d="M20 46c-2 3-5 5-8 6M20 46c-3 1-6 1-9 0" stroke="%s" stroke-width="2.2" stroke-linecap="round" fill="none"/>' % CHAR
    + '<circle cx="25" cy="43" r="2.4" fill="%s"/>' % CHAR
), "Shrimp")

svg("icon-mushroom.svg", 64, 64, (
    '<path d="M40 44l1 12a4 4 0 0 0 8 0l1-12z" fill="%s" stroke="%s" stroke-width="2.4"/>' % (CREAM, BROWN_D)
    + '<path d="M32 42c0-11 8-19 19-19s19 8 19 19z" fill="%s" stroke="%s" stroke-width="2.4"/>' % (BROWN, BROWN_D)
    + '<path d="M12 52l1-13a5 5 0 0 1 5-5c3 0 5 2 5 5l1 13z" fill="%s" stroke="%s" stroke-width="2.6"/>' % (CREAM, BROWN_D)
    + '<path d="M4 34c0-14 10-24 24-24s24 10 24 24c0 2-2 3-4 3H8c-2 0-4-1-4-3z" fill="%s" stroke="%s" stroke-width="2.8"/>' % (BROWN, BROWN_D)
    + '<path d="M10 30c4-9 11-14 18-14 6 0 11 3 15 8" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round" opacity=".8"/>' % BROWN_L
    + '<path d="M8 36c8 3 40 3 48 0" fill="none" stroke="%s" stroke-width="2.4" stroke-linecap="round" opacity=".55"/>' % BROWN_D
), "Mushroom")

svg("icon-noodle.svg", 64, 64, (
    '<path d="M12 26h40v10a12 12 0 0 1-12 12H24a12 12 0 0 1-12-12z" fill="%s" stroke="%s" stroke-width="3"/>' % (CREAM, RED_D)
    + '<rect x="8" y="22" width="48" height="7" rx="3.5" fill="%s"/>' % RED
    + '<g fill="none" stroke="%s" stroke-width="3" stroke-linecap="round">'
      '<path d="M20 20c2-5 8-5 10 0s8 5 10 0"/><path d="M18 14c3-5 9-4 11 1s8 4 11-1"/></g>' % GOLD
    + '<path d="M44 8l14 14M50 6l12 12" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % CHAR
), "Noodles")

svg("icon-dumpling.svg", 64, 64, (
    '<path d="M4 50h56v4a8 8 0 0 1-8 8H12a8 8 0 0 1-8-8z" fill="%s" stroke="%s" stroke-width="2.2"/>' % (GOLD_L, GOLD_D)
    + '<path d="M11 46l-7 4 8 3zM53 46l7 4-8 3z" fill="%s"/>' % GOLD
    + '<path d="M8 50c0-18 11-30 24-30s24 12 24 30z" fill="%s" stroke="%s" stroke-width="2.6"/>' % (WHITE, GOLD_D)
    + '<g stroke="%s" stroke-width="2.4" fill="none" stroke-linecap="round">'
      '<path d="M15 40c3-8 9-13 17-15M32 25c8 2 14 7 17 15"/>'
      '<path d="M22 32c2 5 3 9 3 14M42 32c-2 5-3 9-3 14M32 25v21"/></g>' % GOLD_D
    + '<path d="M12 44c6 5 34 5 40 0" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % GOLD
    + '<g stroke="%s" stroke-width="1.8" fill="none" opacity=".7">'
      '<path d="M18 40c2-6 6-10 12-12M46 40c-2-6-6-10-12-12"/></g>' % GOLD
), "Gyoza dumplings")

svg("icon-sauce.svg", 64, 64, (
    '<path d="M34 6h14v9a5 5 0 0 1 3 4.6v6a5 5 0 0 1-5 5H36a5 5 0 0 1-5-5v-6a5 5 0 0 1 3-4.6z" fill="#4A2C18" stroke="#2E1A0C" stroke-width="2"/>'
    + '<rect x="38" y="1.5" width="7" height="5" rx="2" fill="#2E1A0C"/>'
    + '<rect x="36" y="12" width="12" height="7" fill="%s" opacity=".85"/>' % CREAM
    + '<path d="M40 31c0 5 0 8-3 11" stroke="#4A2C18" stroke-width="3.6" fill="none" stroke-linecap="round"/>'
    + '<path d="M6 44h34v4a9 9 0 0 1-9 9H15a9 9 0 0 1-9-9z" fill="%s" stroke="%s" stroke-width="2.6"/>' % (CREAM, RED_D)
    + '<rect x="3" y="40" width="40" height="6" rx="3" fill="%s"/>' % RED
    + '<path d="M10 45c6 4 20 4 26 0" fill="none" stroke="#4A2C18" stroke-width="4.4" stroke-linecap="round"/>'
    + '<circle cx="17" cy="47" r="3" fill="%s"/>' % RED
    + '<circle cx="26" cy="48" r="2.4" fill="%s"/>' % GREEN
), "Sauce bottle and dipping dish")

svg("icon-sweet.svg", 64, 64, (
    '<path d="M14 36h36l-3 17a7 7 0 0 1-7 6H24a7 7 0 0 1-7-6z" fill="%s" stroke="%s" stroke-width="2.6"/>' % (CREAM, RED_D)
    + '<path d="M17 43h30" stroke="%s" stroke-width="3"/>' % GOLD
    + '<path d="M16 34c0-7 7-12 16-12s16 5 16 12z" fill="%s" stroke="%s" stroke-width="2.4"/>' % (WHITE, GOLD_D)
    + '<path d="M32 24c-6 0-10 2-12 5 4-1 8-1 12 1 4-2 8-2 12-1-2-3-6-5-12-5z" fill="%s" opacity=".85"/>' % CREAM
    + '<path d="M32 22c-4 0-7-3-7-6 0-2 1-3 3-3-1-3 2-6 5-5 3-1 6 2 5 5 2 0 3 1 3 3 0 3-3 6-7 6z" fill="%s" stroke="%s" stroke-width="2"/>' % (RED, RED_D)
    + '<path d="M32 8c1-3 3-4 6-4-1 3-3 5-6 5z" fill="%s"/>' % GREEN
    + '<circle cx="30" cy="14" r="1.3" fill="%s"/><circle cx="35" cy="16" r="1.3" fill="%s"/>' % (WHITE, WHITE)
), "Sweet with strawberry")

svg("icon-flame.svg", 64, 64, (
    '<path d="M32 5c3 9 12 12 15 22 4 13-4 24-15 24S13 40 17 27c3-9 12-13 15-22z" fill="%s"/>' % RED
    + '<path d="M32 20c2 6 8 8 9 15 1 8-3 14-9 14s-10-6-9-14c1-7 7-9 9-15z" fill="%s"/>' % GOLD_L
    + '<path d="M32 32c1 3 4 5 4 9 0 4-2 7-4 7s-4-3-4-7c0-4 3-6 4-9z" fill="%s"/>' % CREAM
), "Flame")

svg("icon-chili.svg", 64, 64, (
    '<path d="M40 16c6 8 6 20-2 28-7 7-18 8-26 4 8-2 12-6 16-13 4-8 6-14 12-19z" fill="%s" stroke="%s" stroke-width="2.4"/>' % (RED, RED_D)
    + '<path d="M38 14c3-6 10-8 16-6-3 6-9 9-16 6z" fill="%s"/>' % GREEN
), "Chilli")

svg("icon-lantern.svg", 64, 64, (
    '<path d="M32 2v8" stroke="%s" stroke-width="3"/>' % CHAR
    + '<rect x="24" y="8" width="16" height="5" rx="2" fill="%s"/>' % GOLD
    + '<ellipse cx="32" cy="30" rx="20" ry="17" fill="%s" stroke="%s" stroke-width="2.6"/>' % (RED, RED_D)
    + '<path d="M32 13v34M12 30h40" stroke="%s" stroke-width="2" opacity=".55"/>' % GOLD
    + '<rect x="24" y="46" width="16" height="5" rx="2" fill="%s"/>' % GOLD
    + '<path d="M32 51v9" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % GOLD
), "Lantern")

# -------------------------------------------------------------- dividers ----
def steam_wave(x, y, w, fill, op=1.0):
    """The classic steam glyph: a wavy ribbon."""
    return ('<path d="M%d %dc4-4 8 4 12 0s8 4 12 0v%d c-4 4-8-4-12 0s-8 4-12 0z" fill="%s" opacity="%s"/>'
            % (x, y, w // 2, fill, op))


svg("divider-gold.svg", 1200, 30, (
    '<path d="M0 15h494" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % GOLD
    + '<path d="M706 15h494" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % GOLD
    + '<g transform="translate(600 15)"><path d="M-34 0l11-10 9 10-9 10z" fill="%s"/>'
      '<circle r="9" fill="%s" stroke="%s" stroke-width="2"/>'
      '<path d="M34 0l-11-10-9 10 9 10z" fill="%s"/></g>' % (RED, GOLD_L, RED_D, RED)
), "Gold trim divider")

svg("pattern-hotpot.svg", 160, 160, (
    '<defs><g id="pot">'
    '<path d="M-15 0h30v9a10 10 0 0 1-10 10h-10a10 10 0 0 1-10-10z" fill="%s"/>'
    '<rect x="-19" y="-4" width="38" height="6" rx="3" fill="%s"/>'
    '<g fill="none" stroke="%s" stroke-width="2.6" stroke-linecap="round">'
    '<path d="M-6 -9c-4-5 4-7 0-12"/><path d="M6 -9c-4-5 4-7 0-12"/></g></g></defs>' % (RED, GOLD, RED)
    + '<g opacity=".32">'
    + "".join('<use xlink:href="#pot" x="%d" y="%d"/>' % (x, y) for x in (40, 120) for y in (46, 126))
    + "".join('<circle cx="%d" cy="%d" r="3.2" fill="%s"/>' % (x, y, GOLD) for x in (80, 160) for y in (86, 166))
    + '</g>'
), "Tileable hotpot motif pattern")

svg("stroke-wave.svg", 1200, 48, (
    "".join('<path d="M%d 48V30A26 26 0 0 1 %d 30V48z" fill="%s"/>'
            % (x, x + 52, RED if (x // 52) % 2 else GOLD) for x in range(0, 1248, 52))
    + '<rect x="0" y="42" width="1248" height="6" fill="%s"/>' % GOLD_D
), "Scalloped band")

svg("spires-scene.svg", 1200, 240, (
    skyline(1200, 240,
            towers=[(600, 216, 190, 96, RED), (452, 216, 128, 66, RED), (748, 216, 128, 66, RED),
                    (318, 216, 92, 48, RED), (882, 216, 92, 48, RED)],
            back=[(180, 222, 118, 60, GOLD), (1010, 222, 104, 54, GOLD), (60, 226, 76, 40, GOLD),
                  (1140, 226, 82, 42, GOLD)],
            ground=RED_D)
), "Angkor-style temple skyline")

if __name__ == "__main__":
    names = sorted(f for f in os.listdir(OUT) if f.endswith(".svg"))
    print("illustrations written and XML-validated:", len(names))
    for n in names:
        print("  ", n, os.path.getsize(os.path.join(OUT, n)), "bytes")
