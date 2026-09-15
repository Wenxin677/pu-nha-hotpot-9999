#!/usr/bin/env python3
"""Generate the site's photographs locally with ComfyUI (SDXL).

Reads tools/ai/prompts.json, posts an SDXL txt2img graph to the ComfyUI API,
polls until each image is ready and downloads it to tools/imgwork/ai/.
Deterministic: every image has a fixed seed, so a regeneration reproduces the
same picture.

Usage
  python tools/ai/generate.py                     # everything that is missing
  python tools/ai/generate.py hero-hotpot.jpg     # one image (or several)
  python tools/ai/generate.py --force             # regenerate even if present
  python tools/ai/generate.py --host http://127.0.0.1:8188
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONF = os.path.join(ROOT, "tools", "ai", "prompts.json")
OUT = os.path.join(ROOT, "tools", "imgwork", "ai")


def graph(prompt, negative, ckpt, width, height, steps, cfg, seed, sampler, scheduler,
          vae=None, upscale_model=None, batch=1):
    """SD txt2img graph in API format, with an optional external VAE and a 4x
    upscale pass (both keep the final asset sharp when the site crops it)."""
    g = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage",
              "inputs": {"width": width, "height": height, "batch_size": batch}},
        "5": {"class_type": "KSampler",
              "inputs": {"seed": seed, "steps": steps, "cfg": cfg, "sampler_name": sampler,
                         "scheduler": scheduler, "denoise": 1.0,
                         "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
                         "latent_image": ["4", 0]}},
    }
    vae_ref = ["1", 2]
    if vae:
        g["8"] = {"class_type": "VAELoader", "inputs": {"vae_name": vae}}
        vae_ref = ["8", 0]
    g["6"] = {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": vae_ref}}
    image_ref = ["6", 0]
    if upscale_model:
        g["9"] = {"class_type": "UpscaleModelLoader", "inputs": {"model_name": upscale_model}}
        g["10"] = {"class_type": "ImageUpscaleWithModel",
                   "inputs": {"upscale_model": ["9", 0], "image": ["6", 0]}}
        image_ref = ["10", 0]
    g["7"] = {"class_type": "SaveImage",
              "inputs": {"filename_prefix": "punha", "images": image_ref}}
    return g


def post(host, path, payload):
    req = urllib.request.Request(host + path, data=json.dumps(payload).encode(),
                                headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def get(host, path, raw=False):
    with urllib.request.urlopen(host + path, timeout=120) as r:
        return r.read() if raw else json.loads(r.read().decode())


def wait_for(host, prompt_id, timeout=1800):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            hist = get(host, "/history/%s" % prompt_id)
        except urllib.error.HTTPError:
            hist = {}
        if prompt_id in hist:
            entry = hist[prompt_id]
            status = entry.get("status", {})
            if status.get("status_str") == "error" or not status.get("completed", True):
                raise RuntimeError("ComfyUI reported an error: %s" % json.dumps(status)[:400])
            return entry["outputs"]
        time.sleep(2)
    raise TimeoutError("timed out waiting for %s" % prompt_id)


def extract(host, outputs, dest):
    for node in outputs.values():
        for img in node.get("images", []):
            q = urllib.parse.urlencode({"filename": img["filename"],
                                        "subfolder": img.get("subfolder", ""),
                                        "type": img.get("type", "output")})
            data = get(host, "/view?" + q, raw=True)
            with open(dest, "wb") as fh:
                fh.write(data)
            return len(data)
    raise RuntimeError("no image in the ComfyUI response")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", help="image file names to build (default: all)")
    ap.add_argument("--host", default="http://127.0.0.1:8188")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--steps", type=int, default=None)
    ap.add_argument("--checkpoint", default=None)
    ap.add_argument("--seed-base", type=int, default=99990)
    ap.add_argument("--no-upscale", action="store_true", help="skip the 4x upscale pass")
    args = ap.parse_args()

    conf = json.load(open(CONF, encoding="utf-8"))
    model = conf.get("model", {})
    ckpt = args.checkpoint or model.get("checkpoint")
    steps = args.steps or model.get("steps", 28)
    cfg = model.get("cfg", 5.0)
    sampler = model.get("sampler", "dpmpp_2m")
    scheduler = model.get("scheduler", "karras")
    vae = model.get("vae")
    up_model = None if args.no_upscale else model.get("upscale_model")
    os.makedirs(OUT, exist_ok=True)

    # is the checkpoint actually installed?
    try:
        info = get(args.host, "/object_info/CheckpointLoaderSimple")
        have = info["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
    except Exception as exc:
        sys.exit("ComfyUI not reachable at %s (%s). Start it with: comfy launch --background"
                 % (args.host, exc))
    if ckpt not in have:
        sys.exit("checkpoint %r is not installed. Available: %s" % (ckpt, have))

    names = args.names or list(conf["images"].keys())
    done, failed = [], []
    for i, name in enumerate(names):
        spec = conf["images"][name]
        dest = os.path.join(OUT, name)
        if os.path.exists(dest) and not args.force:
            print("skip   %-26s (already generated)" % name)
            continue
        w, h = spec["size"]
        style = conf["interior_style"] if "interior" in spec["prompt"] or "restaurant" in spec["prompt"] else conf["style_suffix"]
        prompt = spec["prompt"] + style
        seed = args.seed_base + list(conf["images"]).index(name) * 7
        try:
            res = post(args.host, "/prompt", {"prompt": graph(prompt, conf["negative_prompt"], ckpt,
                                                              w, h, steps, cfg, seed, sampler, scheduler,
                                                              vae=vae, upscale_model=up_model),
                                              "client_id": "punha-site"})
            pid = res["prompt_id"]
            t0 = time.time()
            outputs = wait_for(args.host, pid)
            size = extract(args.host, outputs, dest)
            secs = time.time() - t0
            print("ok     %-26s %5.1fs  %3d KB  seed=%d" % (name, secs, size // 1024, seed))
            done.append(name)
        except Exception as exc:
            print("FAIL   %-26s %s: %s" % (name, type(exc).__name__, str(exc)[:160]))
            failed.append(name)
    print("\ngenerated %d, failed %d -> %s" % (len(done), len(failed), OUT))
    if failed:
        print("failed:", ", ".join(failed))


if __name__ == "__main__":
    main()
