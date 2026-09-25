#!/usr/bin/env python3
"""Render an HTML ad (ads/<name>/index.html) to a 1080x1920 H.264 MP4.

Every ad is a pure function of time (see ads/_shared/runtime.js), so this
script seeks headless Chromium to each frame, screenshots it, and pipes the
frames into ffmpeg. Same input, same pixels, every run.

    pip install playwright imageio-ffmpeg
    python tools/render.py ads/hero-auto-trade           # -> out/hero-auto-trade.mp4 + covers
    python tools/render.py ads/*/ --fps 30
    python tools/render.py ads/hero-auto-trade --stills 0,6600   # QA PNGs only

Chromium: uses $CHROMIUM_PATH, else /opt/pw-browsers (the Claude Code cloud
image), else Playwright's own download.
"""
from __future__ import annotations

import argparse
import glob
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import soundtrack  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H = 1080, 1920


def chromium_path() -> str | None:
    if os.environ.get("CHROMIUM_PATH"):
        return os.environ["CHROMIUM_PATH"]
    hits = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))
    return hits[-1] if hits else None


def ffmpeg_path() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    import imageio_ffmpeg  # noqa: PLC0415

    return imageio_ffmpeg.get_ffmpeg_exe()


def open_ad(p, ad_dir: pathlib.Path):
    browser = p.chromium.launch(executable_path=chromium_path(), args=["--force-color-profile=srgb"])
    page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    page.goto((ad_dir / "index.html").as_uri() + "?render")
    page.wait_for_function("window.__adReady === true")
    page.evaluate("document.fonts.ready")
    duration = page.evaluate("window.Ad.duration")
    return browser, page, duration


def render_video(ad_dir: pathlib.Path, fps: int, out: pathlib.Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser, page, duration = open_ad(p, ad_dir)
        frames = int(round(duration / 1000 * fps))
        # An ad with a #soundtrack cue list gets its synthesized score,
        # loudness-normalised to -14 LUFS (what Reels/Feed normalise to anyway).
        # Otherwise a silent stereo track: some placements treat audio-less
        # uploads as "no sound" creatives.
        wav = pathlib.Path(tempfile.gettempdir()) / f"{ad_dir.name}.wav"
        if soundtrack.render(ad_dir, wav):
            audio = ["-i", str(wav)]
            afilter = ["-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000"]
        else:
            audio = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
            afilter = []
        cmd = [
            ffmpeg_path(), "-y", "-loglevel", "error",
            "-f", "image2pipe", "-vcodec", "mjpeg", "-framerate", str(fps), "-i", "-",
            *audio,
            "-map", "0:v", "-map", "1:a", "-shortest", *afilter,
            "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
            "-profile:v", "high", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", str(out),
        ]
        enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(frames):
            page.evaluate("t => window.Ad.seek(t)", i * 1000 / fps)
            enc.stdin.write(page.screenshot(type="jpeg", quality=95))
            if i % fps == 0:
                print(f"\r{ad_dir.name}: {i / fps:5.1f}s / {duration / 1000:.1f}s", end="", flush=True)
        enc.stdin.close()
        if enc.wait() != 0:
            sys.exit(f"ffmpeg failed for {ad_dir.name}")
        # Poster frame for the Meta thumbnail picker and the landing page.
        page.evaluate("t => window.Ad.seek(t)", float(page.evaluate("document.getElementById('stage').dataset.poster ?? 7000")))
        page.screenshot(path=str(out.with_suffix(".jpg")), type="jpeg", quality=90)
        # Feed placements crop 9:16 to 4:5 (y 285-1635); ship that cover too so
        # the thumbnail picked in Ads Manager is the one the feed actually shows.
        page.screenshot(path=str(out.with_name(out.stem + "_4x5.jpg")), type="jpeg", quality=90,
                        clip={"x": 0, "y": 285, "width": W, "height": 1350})
        browser.close()
    print(f"\r{ad_dir.name}: wrote {out.relative_to(ROOT)} ({out.stat().st_size / 1e6:.1f} MB)")


def render_stills(ad_dir: pathlib.Path, times: list[int], out_dir: pathlib.Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser, page, _ = open_ad(p, ad_dir)
        for t in times:
            page.evaluate("t => window.Ad.seek(t)", t)
            page.screenshot(path=str(out_dir / f"{ad_dir.name}_{t:05d}.png"))
        browser.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("ads", nargs="+", type=pathlib.Path)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--stills", help="comma-separated ms; writes PNGs to out/stills instead of a video")
    a = ap.parse_args()
    for ad in a.ads:
        ad = ad.resolve()
        if a.stills:
            render_stills(ad, [int(x) for x in a.stills.split(",")], ROOT / "out" / "stills")
        else:
            render_video(ad, a.fps, ROOT / "out" / f"{ad.name}.mp4")


if __name__ == "__main__":
    main()
