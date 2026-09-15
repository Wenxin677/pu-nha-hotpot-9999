"""Benchmark thread count and bfloat16 autocast for CPU diffusion speed."""
import os, sys, time

os.environ.setdefault("HF_HOME", os.path.join(os.path.expanduser("~"), ".cache", "hf-punha"))
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler, AutoencoderKL

WEIGHTS = os.path.join(os.path.expanduser("~"), "dev", "comfy", "models")
CKPT = os.path.join(WEIGHTS, "checkpoints", "Realistic_Vision_V5.1_fp16-no-ema.safetensors")
VAE = os.path.join(WEIGHTS, "vae", "vae-ft-mse-840000-ema-pruned.safetensors")

PROMPT = ("chopsticks lifting a thin slice of marbled raw beef over a bubbling divided hotpot, "
          "steam rising, dark wooden table, professional food photography, sharp focus, 8k uhd")
NEG = "worst quality, low quality, blurry, watermark, text, cartoon, illustration, 3d render, plastic"


def bench(threads, dtype_name, steps=8, size=(832, 512), label=""):
    torch.set_num_threads(threads)
    vae = AutoencoderKL.from_single_file(VAE, torch_dtype=torch.float32)
    pipe = StableDiffusionPipeline.from_single_file(CKPT, torch_dtype=torch.float32,
                                                    safety_checker=None, requires_safety_checker=False, vae=vae)
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True,
                                                             algorithm_type="dpmsolver++")
    pipe.set_progress_bar_config(disable=True)
    dt = torch.bfloat16 if dtype_name == "bf16" else torch.float32
    gen = torch.Generator(device="cpu").manual_seed(1234)
    t0 = time.time()
    with torch.no_grad():
        if dtype_name == "bf16":
            with torch.autocast("cpu", dtype=torch.bfloat16):
                pipe(PROMPT, negative_prompt=NEG, width=size[0], height=size[1],
                     num_inference_steps=steps, guidance_scale=6.5, generator=gen)
        else:
            pipe(PROMPT, negative_prompt=NEG, width=size[0], height=size[1],
                 num_inference_steps=steps, guidance_scale=6.5, generator=gen)
    secs = time.time() - t0
    print("%-22s threads=%2d %-5s %2d steps -> %5.1fs (%.2f s/step)" % (label, threads, dtype_name, steps, secs, secs / steps), flush=True)
    del pipe
    return secs / steps


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "threads"):
        bench(32, "fp32", label="threads sweep")
        bench(24, "fp32", label="threads sweep")
        bench(16, "fp32", label="threads sweep")
    if which in ("all", "bf16"):
        bench(24, "bf16", label="dtype sweep")
        bench(16, "bf16", label="dtype sweep")
