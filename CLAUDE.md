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
- **Exception (owner, 2026-09-26):** the API-connect awareness/guide videos
  (`api-connect-reel`, `api-connect-guide`) are **English only**.
- **No exchange logos**; "Binance" as plain text only.
- **Safe zone:** words between y≈285 and y≈1300 on the 1080×1920 canvas.
- **The ASCI disclaimer end card is ≥5s** (currently 5.5s: 12.5s → 18s). Keep
  `data-end-at`, `data-duration` and the `#soundtrack` cue list's `music_until` / `end`
  in step if the ad's length changes.
- **Frame 0 is the thumbnail** (owner, 2026-09-25: the cover earns the click). It must
  read fully composed with no motion; check `out/*_4x5.jpg` too, because Feed crops to
  y 285–1635 and anything above 285 (the brand bar) is cut there.
- **One ad per hook, and every ad answers a test.** `hero-auto-trade` (outcome),
  `unlock-live` (curiosity), `chaos-clarity` (pain) differ only in the hook;
  offer and end card are shared. After the test, budget goes to the winner.
  A new ad needs a new hook to test, never just a new look.
- **No win-rate reading in pictures either.** A record shown on screen carries as
  many losses as wins (`chaos-clarity` shows 3 TP / 3 SL); a win-heavy list is a
  win-rate claim without the number.
- The soundtrack is synthesized (`tools/soundtrack.py`), so there is no music licence
  to track. Cuts and SFX sit on its 120 BPM grid; move them together.
- Re-render after any edit to `ads/` and commit the new `out/*.mp4` with the source.
- Run `python tools/check_compliance.py` before pushing (CI runs it on every PR). A
  failure names the rule; fix the creative, never loosen the rule to get green.
- Every change ships via PR; merging to `main` deploys `site/` to GitHub Pages.
