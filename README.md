# Lumin — Meta ads

Paid-social creative and landing page for **Lumin** (consumer app of the
360 Crypto Eye signal engine). Nothing here touches the app or the engine;
`lumin-app` and `360-v2` are read-only context.

| Path | What |
|---|---|
| `out/*.mp4` | Rendered ads — 1080×1920, 30fps, 20s, H.264, ready to upload |
| `out/*.jpg` | Poster frames (thumbnails) |
| `ads/<name>/index.html` | Source of each ad — an HTML animation, open it in a browser to preview |
| `ads/_shared/` | Design system (`base.css`), scenery + end card (`shared.js`), deterministic timeline (`runtime.js`) |
| `tools/render.py` | HTML → MP4 renderer |
| `site/` | Landing page, deployed to GitHub Pages by `.github/workflows/pages.yml` |
| `docs/ad-copy.md` | Hinglish primary text / headline / description per ad |
| `docs/campaign-plan.md` | Campaign structure, targeting, what to measure |
| `docs/compliance-checklist.md` | Rules every creative passes + where each claim comes from |

## The three ads

1. **01-signal-in-seconds**: "Signal aaya move ke BAAD?" → engine scans 24/7 → crystal-clear signal → Auto Trade places entry/stop/target on Binance → exit is clear either way.
2. **02-clear-exit**: "TP1, TP2, TP3… exit kab karein?" → 1 entry, 1 stop, 1 exit → the plan drawn → win bhi, loss bhi.
3. **03-auto-trade**: "Signal aaya… aap busy the?" → Step 1 API (withdrawal keys rejected) → Step 2 Auto ON → Step 3 Lumin handles it → Free / Assist / Auto.

Each ends with the CTA and the ASCI risk disclaimer on screen for 5.5s.

## Edit and re-render

```bash
pip install playwright imageio-ffmpeg     # Chromium: python -m playwright install chromium
open ads/02-clear-exit/index.html          # live preview, loops
python tools/render.py ads/02-clear-exit --stills 3000,8000   # QA frames → out/stills/
python tools/render.py ads/*/              # all MP4s → out/  (~2 min per ad)
```

Animation is declarative: `data-in="up" data-at="1200" data-dur="600"` enters
an element at 1.2s; `data-out="fade" data-until="5000"` exits it. Keep words
between y≈285 and y≈1300 (Reels caption + 4:5 feed crop), see `base.css`.

## Landing page

`site/config.js` holds the Meta Pixel ID (empty = no tracking). The page sends
iPhone users to the web app with Add-to-Home-Screen steps, Android users to
Google Play with UTMs in `referrer`, and warns Instagram/Facebook in-app
browser users to open Safari/Chrome. Enable once: Settings → Pages → Source:
GitHub Actions.
