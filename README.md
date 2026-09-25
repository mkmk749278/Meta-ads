# Lumin — Meta ads

Paid-social creative and landing page for **Lumin** (consumer app of the
360 Crypto Eye signal engine). Nothing here touches the app or the engine;
`lumin-app` and `360-v2` are read-only context.

| Path | What |
|---|---|
| `out/hero-auto-trade.mp4` | The ad — 1080×1920, 30fps, 18s, H.264 + AAC soundtrack (−14 LUFS), ready to upload |
| `out/hero-auto-trade.jpg` | 9:16 cover (= frame 0) — Reels / Stories thumbnail |
| `out/hero-auto-trade_4x5.jpg` | 4:5 cover (y 285–1635 crop) — Feed thumbnail |
| `ads/<name>/index.html` | Source of each ad — an HTML animation, open it in a browser to preview |
| `ads/_shared/` | Design system (`base.css`), deterministic timeline (`runtime.js`) |
| `tools/render.py` | HTML → MP4 renderer (+ covers) |
| `tools/soundtrack.py` | Synthesizes the score + SFX from the ad's `#soundtrack` cue list — no samples, nothing to license |
| `site/` | Landing page, deployed to GitHub Pages by `.github/workflows/pages.yml` |
| `docs/ad-copy.md` | Hinglish primary text / headline / description per ad |
| `docs/campaign-plan.md` | Campaign structure, targeting, what to measure |
| `docs/compliance-checklist.md` | Rules every creative passes + where each claim comes from |

## The ad

**One ad, `hero-auto-trade`** (owner, 2026-09-25: the three older ads read like
slide decks; one strong ad is enough, and the cover is what earns the click).
The three older ads are in git history before this change.

**Frame 0 is the thumbnail.** It is fully composed with no motion needed: *"Aap so rahe
the. Trade lag gaya."* over a phone lock screen at 3:12 AM with the Auto Trade
notification (entry ✓ stop-loss ✓ target ✓). Reels shows frame 0 before autoplay,
so the cover and the hook are the same picture.

| Time | Beat |
|---|---|
| 0–2.5s | **Hook**: 3 AM, phone buzzes, Auto Trade placed the trade |
| 2.5–5s | **"Kaise?"**: engine scans 24/7, 75+ pairs, every 15s, locks on a setup |
| 5–8.5s | **Signal**: entry / stop / target, then *1 Entry · 1 Stop · 1 Exit* on the beat |
| 8.5–12.5s | **Auto Trade**: toggle ON, your Binance account, orders placed, withdrawal keys rejected |
| 12.5–18s | CTA + ASCI disclaimer (5.5s) |

Cuts land on a 120 BPM grid; the camera pushes in and bumps on each kick; each
cut flashes. The soundtrack is synthesized from the cue list at the top of the ad's HTML.

## Edit and re-render

```bash
pip install playwright imageio-ffmpeg     # Chromium: python -m playwright install chromium
pip install numpy                         # soundtrack synthesis
open ads/hero-auto-trade/index.html       # live preview, loops (silent: the score is added at render)
python tools/render.py ads/hero-auto-trade --stills 0,6600,11800   # QA frames → out/stills/
python tools/render.py ads/hero-auto-trade   # MP4 + both covers → out/  (~1.5 min)
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
