#!/usr/bin/env python3
"""Regenerate CREDITS.md from the asset manifest and the generation prompts.

Run after tools/make_images.py so credits.json describes the files that shipped:
  python tools/ai/write_credits.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CREDITS = os.path.join(ROOT, "tools", "imgwork", "credits.json")
PROMPTS = os.path.join(ROOT, "tools", "ai", "prompts.json")

USAGE = {
    "hero-hotpot.jpg": "Home — hero background",
    "about-table.jpg": "Home — about section",
    "broth-signature.jpg": "Home — menu card: Signature broths",
    "beef-slices.jpg": "Home — menu card: Premium meats",
    "seafood-platter.jpg": "Home — menu card: Ocean fresh",
    "mushrooms.jpg": "Home — menu card: Garden & mushrooms",
    "noodles.jpg": "Home — menu card: Handmade noodles",
    "dumplings.jpg": "Home — menu card: Dumplings & balls",
    "fish-balls.jpg": "Home — menu card: Skewers & grill",
    "sauces.jpg": "Home — menu card: Sauce bar & sides",
    "dumplings-basket.jpg": "Home — menu card: Sweets & drinks",
    "hotpot-divided.jpg": "About Us — founding story",
    "dimsum.jpg": "About Us — gallery",
    "potstickers.jpg": "About Us — gallery",
    "noodle-bowl.jpg": "About Us — gallery",
    "greens.jpg": "About Us — gallery",
    "hotpot-topdown.jpg": "About Us — gallery",
    "fish-dish.jpg": "About Us — gallery",
    "prawns.jpg": "About Us — gallery",
    "story-bowl.jpg": "About Us — gallery",
    "branch-bkk1.jpg": "Locations — BKK1 flagship",
    "branch-toulkork.jpg": "Locations — Toul Kork",
    "branch-siemreap.jpg": "Locations — Toul Svay Prey",
    "branch-aeon.jpg": "Locations — Sen Sok (Aeon Mall 2)",
    "branch-battambang.jpg": "Locations — Siem Reap",
    "interior-warm.jpg": "Locations — events card",
    "hotpot-spread.jpg": "Franchising FAQs — product band",
    "interior-modern.jpg": "Franchising Requirements — branch format",
}


def main():
    credits = json.load(open(CREDITS, encoding="utf-8"))
    conf = json.load(open(PROMPTS, encoding="utf-8"))
    model = conf.get("model", {})
    order = list(conf["images"])
    seed_base = model.get("seed_base", 77410)

    L = []
    L.append("# Credits and licences")
    L.append("")
    L.append("## Photographs — generated for this project")
    L.append("")
    L.append("Every photograph on this site was generated locally for this project with")
    L.append("**Stable Diffusion 1.5** (Realistic Vision V5.1 checkpoint + `vae-ft-mse-840000`)")
    L.append("through the `diffusers` library on CPU. That means the images are original work")
    L.append("with no third-party licence attached, no watermark and no stock-photo model release")
    L.append("to worry about — and every one of them can be reproduced exactly.")
    L.append("")
    L.append("How to reproduce any file:")
    L.append("")
    L.append("```bash")
    L.append("python tools/ai/generate_sd.py <file-name.jpg> --force   # e.g. hero-hotpot.jpg")
    L.append("python tools/make_images.py                                # re-cut the web assets")
    L.append("```")
    L.append("")
    L.append("Generation settings: %d steps, CFG %.1f, DPMSolverMultistep (Karras), seed for each" %
             (model.get("steps", 20), model.get("cfg", 6.5)))
    L.append("file = `%d + 7 x index` in the table below." % seed_base)
    L.append("")
    L.append("| File | Used on | Prompt (subject) | Seed |")
    L.append("| --- | --- | --- | --- |")
    for name in order:
        if name not in conf["images"]:
            continue
        spec = conf["images"][name]
        seed = seed_base + order.index(name) * 7
        prompt = spec["prompt"]
        L.append("| `%s` | %s | %s | %d |" % (name, USAGE.get(name, "—"), prompt, seed))
    L.append("")
    L.append("The exact negative prompt, the shared style suffix and the per-file sizes live in")
    L.append("`tools/ai/prompts.json`, which is the single source of truth for the whole set.")
    L.append("")
    L.append("## Illustrations, logo and audio")
    L.append("")
    L.append("* `assets/logos/*` — derived from the team's own mascot artwork")
    L.append("  (`tools/artwork/logo-source.jpg`) by `tools/make_images.py`: the circular badge is")
    L.append("  cut out with a supersampled mask, then exported as PNG and ICO at several sizes.")
    L.append("* `assets/ill/*.svg` — original flat SVG artwork drawn for this project by")
    L.append("  `tools/make_illustrations.py` (steam, flame and chilli motifs, an Angkor-style spire")
    L.append("  skyline, a tiered temple icon, the hotpot, beef, shrimp, mushroom, noodle, dumpling,")
    L.append("  sauce, dessert, lantern and flame menu icons, gold trim and scalloped bands, and the")
    L.append("  tileable hotpot pattern behind the menu and franchising sections).")
    L.append("* `assets/audio/kitchen-ambience.wav` — synthesised from scratch by `tools/make_audio.py`")
    L.append("  using only the Python standard library (room hum, bubbling blips and steam noise).")
    L.append("")
    L.append("## Embedded third-party content")
    L.append("")
    L.append("* YouTube video on `about-history.html`: *How to Hot Pot: The Ultimate Beginner's Guide!*")
    L.append("  by Midnight Kitchen, embedded through `youtube-nocookie.com`.")
    L.append("* Google Maps iframes on `locations.html` and `contact.html`.")
    L.append("* The web fonts Baloo 2 and Inter load from Google Fonts through the `@import` in")
    L.append("  `style.css`, with system fallbacks so the pages still read offline.")
    L.append("")
    L.append("## About the business details")
    L.append("")
    L.append("Pu Nha Hotpot 9999 is the restaurant described in the team's INFO 250 project")
    L.append("proposal. Phone numbers, street addresses, franchise figures and guest reviews are")
    L.append("the illustrative ones written for this coursework, and the branch photographs are")
    L.append("generated interiors rather than photographs of a real location.")
    open(os.path.join(ROOT, "CREDITS.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("CREDITS.md written:", len(L), "lines;", len(order), "generated images documented")


if __name__ == "__main__":
    main()
