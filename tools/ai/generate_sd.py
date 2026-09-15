#!/usr/bin/env python3
"""Generate the site's photographs locally with Stable Diffusion 1.5
(Realistic Vision) through diffusers — CPU inference, no comfy needed.

Two passes per image: a 30-step text-to-image render, then an img2img pass at
1.5x with low strength that adds detail instead of changing the picture.  Every
image has a fixed seed, so `--force` reproduces the identical file.

    tools/ai/.venv/Scripts/python.exe tools/ai/generate_sd.py            # all missing
    tools/ai/.venv/Scripts/python.exe tools/ai/generate_sd.py hero-hotpot.jpg
"""
import argparse
import json
import os
import sys
import time

# the checkpoint and VAE are on disk; only the tiny pipeline config comes from
# the Hub on first run (a few KB), then it is cached for offline use
os.environ.setdefault("HF_HOME", os.path.join(os.path.expanduser("~"), ".cache", "hf-punha"))

import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler, AutoencoderKL

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONF = os.path.join(ROOT, "tools", "ai", "prompts.json")
OUT = os.path.join(ROOT, "tools", "imgwork", "ai")
WEIGHTS = os.path.join(os.path.expanduser("~"), "dev", "comfy", "models")


def load_pipeline(ckpt_path, vae_path, threads):
    torch.set_num_threads(threads)
    vae = None
    if vae_path and os.path.exists(vae_path):
        vae = AutoencoderKL.from_single_file(vae_path, torch_dtype=torch.float32)
    pipe = StableDiffusionPipeline.from_single_file(
        ckpt_path, torch_dtype=torch.float32, safety_checker=None,
        requires_safety_checker=False, vae=vae,
    )
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(
        pipe.scheduler.config, use_karras_sigmas=True, algorithm_type="dpmsolver++")
    pipe.set_progress_bar_config(disable=True)
    return pipe


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--steps", type=int, default=None)
    ap.add_argument("--hires-steps", type=int, default=22)
    ap.add_argument("--no-hires", action="store_true")
    ap.add_argument("--threads", type=int, default=os.cpu_count() or 8)
    ap.add_argument("--seed-base", type=int, default=77410)
    ap.add_argument("--only-missing", action="store_true")
    args = ap.parse_args()

    conf = json.load(open(CONF, encoding="utf-8"))
    model = conf["model"]
    ckpt = os.path.join(WEIGHTS, "checkpoints", model["checkpoint"])
    vae = os.path.join(WEIGHTS, "vae", model.get("vae", ""))
    if not os.path.exists(ckpt):
        sys.exit("checkpoint not found: %s (still downloading?)" % ckpt)
    os.makedirs(OUT, exist_ok=True)

    print("loading %s (threads=%d)…" % (os.path.basename(ckpt), args.threads), flush=True)
    t0 = time.time()
    pipe = load_pipeline(ckpt, vae, args.threads)
    print("pipeline ready in %.1fs" % (time.time() - t0), flush=True)

    names = args.names or list(conf["images"].keys())
    steps = args.steps or model.get("steps", 30)
    cfg = model.get("cfg", 6.5)
    order = list(conf["images"])
    done, failed = [], []
    for name in names:
        spec = conf["images"][name]
        dest = os.path.join(OUT, name)
        if os.path.exists(dest) and not args.force:
            print("skip   %-26s (exists)" % name, flush=True)
            continue
        w, h = spec["size"]
        style = conf["interior_style"] if ("interior" in spec["prompt"] or "restaurant" in spec["prompt"]) else conf["style_suffix"]
        prompt = spec["prompt"] + style
        seed = spec.get("seed", args.seed_base + order.index(name) * 7)
        gen = torch.Generator(device="cpu").manual_seed(seed)
        try:
            t0 = time.time()
            image = pipe(prompt, negative_prompt=conf["negative_prompt"], width=w, height=h,
                         num_inference_steps=steps, guidance_scale=cfg, generator=gen).images[0]
            if not args.no_hires and model.get('hires', False):
                big = (int(w * 1.5) // 8 * 8, int(h * 1.5) // 8 * 8)
                image = pipe(prompt, negative_prompt=conf["negative_prompt"],
                             image=image.resize(big), strength=0.42,
                             num_inference_steps=args.hires_steps, guidance_scale=cfg,
                             generator=gen).images[0]
            image.save(dest)
            print("ok     %-26s %5.1fs  %dx%d  seed=%d" % (name, time.time() - t0, image.width, image.height, seed), flush=True)
            done.append(name)
        except Exception as exc:
            print("FAIL   %-26s %s: %s" % (name, type(exc).__name__, str(exc)[:150]), flush=True)
            failed.append(name)
    print("\ngenerated %d, failed %d -> %s" % (len(done), len(failed), OUT))
    if failed:
        print("failed:", ", ".join(failed))


if __name__ == "__main__":
    main()
