#!/usr/bin/env python3
"""Build all image assets for the Pu Nha Hotpot 9999 site.

Sources live in tools/imgwork/cand* (downloaded from Wikimedia Commons /
Flickr via Openverse, both CC / public-domain friendly) and tools/artwork
(her logo).  Every output is written to assets/img or assets/logos with a
fixed aspect ratio so the CSS grid never has to guess.

Run:  python tools/make_images.py
"""
import json
import os
import re

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "tools", "imgwork")
ART = os.path.join(ROOT, "tools", "artwork")
OUT_IMG = os.path.join(ROOT, "assets", "img")
OUT_LOGO = os.path.join(ROOT, "assets", "logos")
os.makedirs(OUT_IMG, exist_ok=True)
os.makedirs(OUT_LOGO, exist_ok=True)

# ---------------------------------------------------------------- photos ----
# key -> (source folder, source file, out name, out size, credit)
PHOTOS = {
    "hero":        ("cand4", "beef_hotpot_04.jpg",   "hero-hotpot.jpg",    (1600, 1000),
                    "Tajima Beef Shabu-Shabu Hot Pot - Flickr/CC BY"),
    "broth":       ("cand",  "hotpot_broth_05.jpg",  "broth-signature.jpg", (900, 620),
                    "Hot pot, Wikimedia Commons - CC BY-SA"),
    "beef":        ("cand4", "beef_hotpot_05.jpg",   "beef-slices.jpg",    (900, 620),
                    "Wagyu beef for shabu-shabu, Wikimedia Commons - CC BY-SA"),
    "seafood":     ("cand",  "seafood_00.jpg",       "seafood-platter.jpg", (900, 620),
                    "Seafood platter, Wikimedia Commons - CC BY-SA"),
    "mushroom":    ("cand4", "enoki_plate_06.jpg",   "mushrooms.jpg",      (900, 620),
                    "Mushroom plate, Wikimedia Commons - CC BY-SA"),
    "noodles":     ("cand",  "noodles_05.jpg",       "noodles.jpg",        (900, 620),
                    "Noodle hot pot, Wikimedia Commons - CC BY-SA"),
    "dumplings":   ("cand",  "dumplings_tofu_00.jpg", "dumplings.jpg",     (900, 620),
                    "Dumpling plate, Wikimedia Commons - CC BY-SA"),
    "fishballs":   ("cand3", "02_fishballs.jpg",     "fish-balls.jpg",     (900, 620),
                    "Beef tendon & fish balls, Flickr/CC BY-SA"),
    "sauces":      ("cand",  "dining_table_03.jpg",  "sauces.jpg",         (900, 620),
                    "Condiment set, Wikimedia Commons - CC BY-SA"),
    "prawns":      ("cand",  "seafood_03.jpg",       "prawns.jpg",         (900, 620),
                    "Prawns with dipping sauce, Wikimedia Commons - CC BY-SA"),
    "dumplingbasket": ("cand3", "03_dumplings.jpg",  "dumplings-basket.jpg", (900, 620),
                    "Steamed dumplings, Flickr/CC BY-SA"),
    "about":       ("cand",  "dining_table_08.jpg",  "about-table.jpg",    (1200, 800),
                    "Hot pot table spread, Wikimedia Commons - CC BY-SA"),
    "spread":      ("cand",  "hotpot_broth_03.jpg",  "hotpot-spread.jpg",  (1200, 800),
                    "Hot pot spread, Wikimedia Commons - CC BY-SA"),
    "topdown":     ("cand",  "hotpot_broth_06.jpg",  "hotpot-topdown.jpg", (1200, 900),
                    "Hot pot from above, Wikimedia Commons - CC BY-SA"),
    "divided":     ("cand",  "hotpot_broth_00.jpg",  "hotpot-divided.jpg", (1200, 800),
                    "Divided hot pot, Wikimedia Commons - CC BY-SA"),
    "fishdish":    ("cand",  "seafood_02.jpg",       "fish-dish.jpg",      (1200, 800),
                    "Plated fish, Wikimedia Commons - CC BY-SA"),
    "noodlebowl":  ("cand",  "noodles_01.jpg",       "noodle-bowl.jpg",    (1200, 800),
                    "Udon noodle bowl, Wikimedia Commons - CC BY-SA"),
    "banmian":     ("cand3", "04_banmian.jpg",       "story-bowl.jpg",     (1200, 800),
                    "Ban mian with braised beef, Flickr/CC BY-SA"),
    "greens":      ("cand3", "06_greens2.jpg",       "greens.jpg",         (1200, 800),
                    "Fresh greens platter, Flickr/CC BY-SA"),
    "potstickers": ("cand",  "dumplings_tofu_01.jpg", "potstickers.jpg",   (1200, 800),
                    "Pan-fried dumplings, Wikimedia Commons - CC BY-SA"),
    "dimsum":      ("cand2", "unsplash_09.jpg",      "dimsum.jpg",         (1200, 800),
                    "Bamboo steamer, Unsplash"),
    "interior1":   ("cand",  "restaurant_int_02.jpg", "branch-bkk1.jpg",   (1100, 730),
                    "Restaurant interior, Wikimedia Commons - CC BY-SA"),
    "interior2":   ("cand",  "restaurant_int_06.jpg", "branch-toulkork.jpg", (1100, 730),
                    "Restaurant interior, Wikimedia Commons - CC BY-SA"),
    "interior3":   ("cand",  "restaurant_int_07.jpg", "branch-siemreap.jpg", (1100, 730),
                    "Restaurant interior, Wikimedia Commons - CC BY-SA"),
    "interior4":   ("cand",  "restaurant_int_08.jpg", "branch-aeon.jpg",   (1100, 730),
                    "Restaurant interior, Wikimedia Commons - CC BY-SA"),
    "interior5":   ("cand",  "restaurant_int_09.jpg", "branch-battambang.jpg", (1100, 730),
                    "Restaurant interior, Wikimedia Commons - CC BY-SA"),
    "interior6":   ("cand2", "unsplash_02.jpg",      "interior-modern.jpg", (1100, 730),
                    "Modern restaurant interior, Unsplash"),
    "interior7":   ("cand2", "unsplash_07.jpg",      "interior-warm.jpg",  (1100, 730),
                    "Warm restaurant interior, Unsplash"),
}


def cover(src, dst, size):
    """Centre-crop to the target aspect ratio, then resize."""
    im = Image.open(src).convert("RGB")
    tw, th = size
    target = tw / th
    w, h = im.size
    if w / h > target:                      # too wide -> trim sides
        nw = int(h * target)
        im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:                                   # too tall -> trim top/bottom
        nh = int(w / target)
        top = max(0, int((h - nh) * 0.42))  # bias up: food usually sits high
        im = im.crop((0, top, w, top + nh))
    return im.resize(size, Image.LANCZOS)


def build_photos():
    credits, made = [], 0
    for key, (folder, src_name, out_name, size, credit) in PHOTOS.items():
        src = os.path.join(WORK, folder, src_name)
        if not os.path.exists(src):
            print("MISSING", key, src)
            continue
        dst = os.path.join(OUT_IMG, out_name)
        im = cover(src, dst, size)
        im.save(dst, "JPEG", quality=82, optimize=True, progressive=True)
        credits.append({"key": key, "file": "assets/img/" + out_name, "credit": credit,
                        "source": src_name})
        made += 1
    print("photos written:", made)
    return credits


# ------------------------------------------------------------------ logo ----
def build_logos():
    """The artwork is a circular badge on a flat white square: cut the circle
    out with a 4x supersampled mask, then export every size the site uses."""
    src = os.path.join(ART, "logo-source.jpg")
    im = Image.open(src).convert("RGB")
    w, h = im.size
    px = im.load()

    # find the badge: bounding box of pixels that are not near-white
    def not_bg(p):
        r, g, b = p[:3]
        return not (r > 238 and g > 238 and b > 238)

    xs, ys = [], []
    step = max(1, w // 500)                 # sample for speed
    for y in range(0, h, step):
        for x in range(0, w, step):
            if not_bg(px[x, y]):
                xs.append(x); ys.append(y)
    if not xs:                               # empty? nothing to cut
        raise SystemExit("no badge found in artwork")
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    r = min(x1 - x0, y1 - y0) / 2.0 * 0.995   # a hair inside the true edge

    SS = 4
    big = im.resize((w * SS, h * SS), Image.LANCZOS)
    # circular alpha mask, supersampled then downscaled => clean antialiased edge
    mask_ss = Image.new("L", (w * SS, h * SS), 0)
    mpx = mask_ss.load()
    rr = (r * SS) ** 2
    for y in range(int((cy - r) * SS) - 2, int((cy + r) * SS) + 3):
        if y < 0 or y >= h * SS:
            continue
        dy = y - cy * SS
        span = int((max(0.0, rr - dy * dy)) ** 0.5)
        for x in range(int(cx * SS) - span, int(cx * SS) + span + 1):
            if 0 <= x < w * SS:
                dx = x - cx * SS
                if dx * dx + dy * dy <= rr:
                    mpx[x, y] = 255
    mask = mask_ss.resize((w, h), Image.LANCZOS)
    badge = big.convert("RGBA").resize((w, h), Image.LANCZOS)
    badge.putalpha(mask)

    # crop to the badge square, then export
    pad = 2
    box = (max(0, int(cx - r) - pad), max(0, int(cy - r) - pad),
           min(w, int(cx + r) + pad), min(h, int(cy + r) + pad))
    sq = badge.crop(box)

    def save(size, name, bg=None):
        out = sq.resize((size, size), Image.LANCZOS)
        if bg:                               # iOS masks the icon itself
            flat = Image.new("RGBA", (size, size), bg)
            flat.alpha_composite(out)
            out = flat
        out.save(os.path.join(OUT_LOGO, name))

    hero = sq.resize((512, 512), Image.LANCZOS)
    hero.quantize(colors=256, method=Image.FASTOCTREE).save(os.path.join(OUT_LOGO, "logo.png"), optimize=True)
    save(96, "logo-96.png")
    save(64, "favicon.png")
    save(180, "apple-touch-icon.png", bg=(255, 250, 244, 255))

    # multi-size .ico
    ico = sq.resize((64, 64), Image.LANCZOS)
    ico.save(os.path.join(OUT_LOGO, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])

    # ---- assertions: corners transparent, centre opaque
    check = Image.open(os.path.join(OUT_LOGO, "logo.png")).convert("RGBA")
    a = check.split()[3]
    for pt in [(0, 0), (511, 0), (0, 511), (511, 511)]:
        assert a.getpixel(pt) == 0, f"corner {pt} not transparent: {a.getpixel(pt)}"
    for pt in [(256, 256), (200, 256), (256, 200)]:
        assert a.getpixel(pt) == 255, f"centre {pt} not opaque: {a.getpixel(pt)}"
    print("logos written, mask assertions passed (r=%.1fpx, centre %.1f,%.1f)" % (r, cx, cy))


if __name__ == "__main__":
    credits = build_photos()
    build_logos()
    with open(os.path.join(ROOT, "tools", "imgwork", "credits.json"), "w", encoding="utf-8") as f:
        json.dump(credits, f, indent=1)
    print("done")
