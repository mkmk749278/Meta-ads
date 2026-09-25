# CLAUDE.md

Marketing repo for **Lumin** (consumer app of the 360 Crypto Eye engine). See
`README.md` for the layout and commands.

- **Read-only context:** `mkmk749278/lumin-app` and `mkmk749278/360-v2` explain the
  business (`360-v2/OWNER_BRIEF.md` first). Owner instruction: do not change code there
  from a marketing session.
- **Every ad claim must be traceable** to a row in `docs/compliance-checklist.md`. No
  profit, % returns, win rate or track-record totals — the public track record
  overstates real fills (engine audit 2026-09-24).
- **Creative style (owner, 2026-09-24):** Hinglish; designed, eye-catching neon UI in
  the style of the brand boards — **not** screenshots of the real app; animated MP4
  with a story flow; highlight clear signals, the single exit, speed and Auto Trade.
- **No exchange logos**; "Binance" as plain text only.
- **Safe zone:** words between y≈285 and y≈1300 on the 1080×1920 canvas.
- **The ASCI disclaimer end card is ≥5s** (currently 5.5s: 12.5s → 18s). Keep
  `data-end-at`, `data-duration` and the `#soundtrack` cue list's `music_until` / `end`
  in step if the ad's length changes.
- **Frame 0 is the thumbnail** (owner, 2026-09-25: the cover earns the click). It must
  read fully composed with no motion; check `out/*_4x5.jpg` too, because Feed crops to
  y 285–1635 and anything above 285 (the brand bar) is cut there.
- **One ad, not a set.** `hero-auto-trade` is the ad; the three older ones are in
  git history. Add a new ad only when there is a test it answers.
- The soundtrack is synthesized (`tools/soundtrack.py`), so there is no music licence
  to track. Cuts and SFX sit on its 120 BPM grid; move them together.
- Re-render after any edit to `ads/` and commit the new `out/*.mp4` with the source.
- Every change ships via PR; merging to `main` deploys `site/` to GitHub Pages.
