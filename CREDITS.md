# Credits and licences

## Photographs — generated for this project

Every photograph on this site was generated locally for this project with
**Stable Diffusion 1.5** (Realistic Vision V5.1 checkpoint + `vae-ft-mse-840000`)
through the `diffusers` library on CPU. That means the images are original work
with no third-party licence attached, no watermark and no stock-photo model release
to worry about — and every one of them can be reproduced exactly.

How to reproduce any file:

```bash
python tools/ai/generate_sd.py <file-name.jpg> --force   # e.g. hero-hotpot.jpg
python tools/make_images.py                                # re-cut the web assets
```

Generation settings: 20 steps, CFG 6.5, DPMSolverMultistep (Karras), seed for each
file = `77410 + 7 x index` in the table below.

| File | Used on | Prompt (subject) | Seed |
| --- | --- | --- | --- |
| `hero-hotpot.jpg` | Home — hero background | hotpot restaurant table from the side, steaming pot in the centre, plates of raw beef and green vegetables around it, chopsticks, warm evening light | 77410 |
| `broth-signature.jpg` | Home — menu card: Signature broths | dark red spicy hotpot broth in a black bowl, chilli oil floating on the surface, dried red chillies and sichuan peppercorns, steam, close up | 77417 |
| `beef-slices.jpg` | Home — menu card: Premium meats | raw marbled beef steaks on a wooden board, deep red meat with white fat marbling, butcher shop display, sharp focus | 77424 |
| `seafood-platter.jpg` | Home — menu card: Ocean fresh | raw prawns, squid and salmon on crushed ice with lime, seafood platter | 77431 |
| `mushrooms.jpg` | Home — menu card: Garden & mushrooms | enoki and shiitake mushrooms with fresh greens on a plate | 77438 |
| `noodles.jpg` | Home — menu card: Handmade noodles | bowl of handmade noodles with broth and spring onion, chopsticks | 77445 |
| `dumplings.jpg` | Home — menu card: Dumplings & balls | steamed dumplings on a plate with chilli dipping sauce | 77452 |
| `fish-balls.jpg` | Home — menu card: Skewers & grill | white fish balls and green vegetables in a bowl of clear soup with a spoon, steam | 77459 |
| `sauces.jpg` | Home — menu card: Sauce bar & sides | small bowls of dipping sauces, sesame, chilli oil and garlic, herbs and lime | 77466 |
| `dumplings-basket.jpg` | Home — menu card: Sweets & drinks | bamboo steamer basket with steamed dumplings, steam, dark table | 77473 |
| `about-table.jpg` | Home — about section | hotpot restaurant table set with a pot of broth, plates of raw beef, mushrooms and green vegetables, top view, no people | 77480 |
| `hotpot-divided.jpg` | About Us — founding story | hotpot on a restaurant table with small plates of fish, tofu and green vegetables around it, warm light, side view | 77487 |
| `hotpot-topdown.jpg` | About Us — gallery | table seen from above, hotpot in the middle cooking meatballs, greens and noodles, small plates arranged around it | 77494 |
| `hotpot-spread.jpg` | Franchising FAQs — product band | wide view of a restaurant table with two bubbling hotpots and many plates of sliced meat, seafood and vegetables | 77501 |
| `dimsum.jpg` | About Us — gallery | plate of steamed dim sum dumplings with dipping sauce on a restaurant table, warm light | 77508 |
| `potstickers.jpg` | About Us — gallery | pan fried potstickers on a teal plate with soy dipping sauce | 77515 |
| `noodle-bowl.jpg` | About Us — gallery | bowl of noodle soup with sliced beef, fish cake and spring onion | 77522 |
| `story-bowl.jpg` | About Us — gallery | bowl of thick noodles with braised beef, greens and soft egg | 77529 |
| `greens.jpg` | About Us — gallery | plate of napa cabbage, morning glory, radish and tofu skin | 77536 |
| `fish-dish.jpg` | About Us — gallery | steamed fish fillet with ginger, spring onion and soy sauce on a white plate | 77543 |
| `prawns.jpg` | About Us — gallery | grilled prawns with lime and chilli dipping sauce on a plate | 77550 |
| `branch-bkk1.jpg` | Locations — BKK1 flagship | busy modern hotpot restaurant interior at night, wooden tables, red lanterns, warm lamps | 77557 |
| `branch-toulkork.jpg` | Locations — Toul Kork | family hotpot restaurant interior, long shared tables, warm lighting, plants | 77564 |
| `branch-aeon.jpg` | Locations — Sen Sok (Aeon Mall 2) | hotpot restaurant dining room inside a modern shopping mall, booth seating, wooden tables, warm lights, no signage | 77571 |
| `interior-warm.jpg` | Locations — events card | private dining room set for a group, round table with hotpot cooker, red and gold decor | 77578 |
| `interior-modern.jpg` | Franchising Requirements — branch format | contemporary asian restaurant interior, open kitchen, wooden counters, daytime | 77585 |
| `branch-toulsvayprey.jpg` | — | hotpot restaurant interior with rattan chairs, wooden floor, hanging lanterns | 77592 |
| `branch-siemreap.jpg` | Locations — Toul Svay Prey | minimal hotpot restaurant interior, wicker chairs, large windows, wooden tables | 77599 |

The exact negative prompt, the shared style suffix and the per-file sizes live in
`tools/ai/prompts.json`, which is the single source of truth for the whole set.

## Illustrations, logo and audio

* `assets/logos/*` — derived from the team's own mascot artwork
  (`tools/artwork/logo-source.jpg`) by `tools/make_images.py`: the circular badge is
  cut out with a supersampled mask, then exported as PNG and ICO at several sizes.
* `assets/ill/*.svg` — original flat SVG artwork drawn for this project by
  `tools/make_illustrations.py` (steam, flame and chilli motifs, an Angkor-style spire
  skyline, a tiered temple icon, the hotpot, beef, shrimp, mushroom, noodle, dumpling,
  sauce, dessert, lantern and flame menu icons, gold trim and scalloped bands, and the
  tileable hotpot pattern behind the menu and franchising sections).
* `assets/audio/kitchen-ambience.wav` — synthesised from scratch by `tools/make_audio.py`
  using only the Python standard library (room hum, bubbling blips and steam noise).

## Embedded third-party content

* YouTube video on `about-history.html`: *How to Hot Pot: The Ultimate Beginner's Guide!*
  by Midnight Kitchen, embedded through `youtube-nocookie.com`.
* Google Maps iframes on `locations.html` and `contact.html`.
* The web fonts Baloo 2 and Inter load from Google Fonts through the `@import` in
  `style.css`, with system fallbacks so the pages still read offline.

## About the business details

Pu Nha Hotpot 9999 is the restaurant described in the team's INFO 250 project
proposal. Phone numbers, street addresses, franchise figures and guest reviews are
the illustrative ones written for this coursework, and the branch photographs are
generated interiors rather than photographs of a real location.
