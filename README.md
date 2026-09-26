# Lumin — Meta ads

Paid-social creative and landing page for **Lumin** (consumer app of the
360 Crypto Eye signal engine). Nothing here touches the app or the engine;
`lumin-app` and `360-v2` are read-only context.

| Path | What |
|---|---|
| `out/<ad>.mp4` | The ads — 1080×1920, 30fps, 18s, H.264 + AAC soundtrack (−14 LUFS), ready to upload |
| `out/<ad>.jpg` | 9:16 cover (= frame 0) — Reels / Stories thumbnail |
| `out/<ad>_4x5.jpg` | 4:5 cover (y 285–1635 crop) — Feed thumbnail |
| `ads/<name>/index.html` | Source of each ad — an HTML animation, open it in a browser to preview |
| `ads/_shared/` | Design system (`base.css`), deterministic timeline (`runtime.js`), effects (`fx.js`: live candle chart, number decode, camera shake + RGB split, particle bursts) |
| `tools/render.py` | HTML → MP4 renderer (+ covers) |
| `tools/soundtrack.py` | Synthesizes the score + SFX from the ad's `#soundtrack` cue list — no samples, nothing to license |
| `site/` | Landing page, deployed to GitHub Pages by `.github/workflows/pages.yml` |
| `docs/ad-copy.md` | Hinglish primary text / headline / description per ad |
| `docs/campaign-plan.md` | Campaign structure, targeting, what to measure |
| `docs/compliance-checklist.md` | Rules every creative passes + where each claim comes from |
| `tools/check_compliance.py` | The checklist's mechanical rules, run on every PR (`--self-test` proves each rule still fires) |

## The ads — one per hook, run as an A/B/C test

Three ads, identical offer and end card, **different hooks** (owner, 2026-09-25:
"attract users, not basic"). Each one exists because it answers a test: which
opening stops the scroll for this audience. Frame 0 of each is its thumbnail and
is fully composed with no motion.

| Ad | Hook (frame 0) | Test | Story |
|---|---|---|---|
| `hero-auto-trade` | *"Aap so rahe the. Trade lag gaya."* — 3:12 AM lock screen | **Outcome** (Auto Trade while you sleep) | scan → signal → Auto Trade → CTA |
| `unlock-live` | *"Ye signal abhi LIVE hai."* — a live card, levels blurred under a padlock | **Curiosity** (the new masked-live funnel) | tap → lock bursts → levels decode → "Number nahi. Form nahi." → 3 din FREE |
| `chaos-clarity` | *"20 indicators. 0 clarity."* — a chart buried under overlays and scribbles | **Pain** (chart overload) | mess collapses into Lumin → Entry/Stop/Target draw in → wins *and* losses on the record |

`unlock-live` and `chaos-clarity` open on a pad and glitches only and **drop the
beat on the first cut** (`drums_from` in the cue list); every cut shakes the
camera and splits RGB. Only the winning hook should get budget after the test,
see `docs/campaign-plan.md`.

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
