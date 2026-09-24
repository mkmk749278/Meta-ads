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
- **The ASCI disclaimer end card is ≥5s** (currently 5.5s from 14.5s). Keep
  `data-end-at` and `data-duration` in step if an ad's length changes.
- Re-render after any edit to `ads/` and commit the new `out/*.mp4` with the source.
- Every change ships via PR; merging to `main` deploys `site/` to GitHub Pages.
