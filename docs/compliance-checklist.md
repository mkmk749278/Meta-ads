# Compliance checklist

Run every new creative through this before it spends a rupee. The app is live
with real users' capital behind it; an ad that over-promises is a trust problem
first and a policy problem second.

The mechanical part — disclaimer verbatim and legible ≥ 5s, end-card timings
in step with the soundtrack, 18+, the safe-zone top, and the banned claim words
in the ads, landing page and `ad-copy.md` — runs on every PR
(`python tools/check_compliance.py`, `.github/workflows/compliance.yml`). The
rest of this list needs a human.

## Hard rules (every ad, every landing-page change)

- [ ] **ASCI crypto disclaimer, verbatim:** "Crypto products and NFTs are unregulated and can be highly risky. There may be no regulatory recourse for any loss from such transactions." Video: on screen ≥ 5s, legible, inside the safe zone. Current ad: 5.5s (12.5–18s), y 866–1265.
- [ ] **No performance claims:** no profit, no %, no win rate, no "₹X/day", no track-record totals. The public track record overstates by ~25 bps/trade (entry drift, engine audit 2026-09-24) — never quote it.
- [ ] **No "safe", "guaranteed", "risk-free", "sure-shot"**, and no implication that crypto solves money problems.
- [ ] **Prices shown are illustrations** and labelled `ILLUSTRATION`; LONG geometry is coherent (stop < entry < target).
- [ ] **No exchange logos.** "Binance" appears as plain text only (nominative: "your Binance account"). Landing footer states non-affiliation.
- [ ] **No competitor named.**
- [ ] **18+** on every creative and the landing page; target 21+ in Ads Manager.
- [ ] Hinglish copy avoids Meta "personal attributes" phrasing (no "are you in debt / losing money").

## Claim → source (where each claim in the ads is substantiated)

| Claim in ads | Source |
|---|---|
| Engine scans 24/7, 75+ pairs, every 15s | `360-v2/OWNER_BRIEF.md` §3.1 |
| "Aap so rahe the. Trade lag gaya." (Auto Trade places the order while the user is away, 3 AM shown) | Owner Brief B1/B16 (Auto = hands-free); engine scans 24/7 (§3.1). The ad shows the trade being placed and never says it won. Auto Trade is the paid tier and needs a connected key, so the end card says "jab chaho" and never calls it free |
| Notification "Entry ✓ Stop-loss ✓ Target ✓" | Same as "Stop-loss on every trade" below, including its audit caveat |
| Signal "seconds mein" after the setup | `360-v2/ACTIVE_CONTEXT.md` (entry-drift section: order goes out seconds after the candle close) |
| One exit: target = 100% close | Owner Brief §3.2 (TP1-full default, B17) |
| Target set with fees in mind | Owner Brief B7, B11 |
| Stop-loss on every trade | Owner Brief B12 + naked-position hard limit. ⚠ Audit 2026-09-24 item 1 (an engine-initiated close can strand a position) is a latent exception — fix before scaling Auto spend |
| Withdrawal-permission keys auto-rejected | Owner Brief B18 |
| Funds stay in the user's account (non-custodial) | Owner Brief B16, B18 |
| "Live signals 3 din FREE" (end card, landing) | Owner decision 2026-09-25 (360-v2 `src/api/signal_access.py`, OWNER_BRIEF B1/B16): every account gets 3 days of live signals from sign-up; closed signals always free. True before and after the paywall start, so the ad needs no re-render when it is switched on. **Never** write "Signals FREE" again — live signals are paid after 3 days |
| "Number nahi. Form nahi. Seedha app mein." (`unlock-live`) | lumin-app #165 (2026-09-25): guest mode — one welcome screen, anonymous sign-in, no phone number to browse. Phone number is asked only at sign-up |
| Live signal shown masked, "Sign up free to see signal" (`unlock-live`) | lumin-app #166 + 360-v2 `signal_access.py`: live levels withheld from guests; the button copy is the app's own |
| "Sign up karo. 3 din saare live signals FREE." (`unlock-live`) | Same row as "Live signals 3 din FREE". The ad never states a price, so it stays true before and after `signals_paywall_start` |
| Lumin reads Trend / Volume / Structure / Market regime (`chaos-clarity`) | `360-v2` scoring: SMC structure dimension, volume inputs, regime classifier (`src/regime.py`), EMA trend. Named as what is read, never as an edge |
| "Har trade ka record. Jeet bhi. Haar bhi." (`chaos-clarity`) | Owner Brief B3, B9; app Track record shows every closed signal. The on-screen list is 3 TP / 3 SL on purpose — no implied win rate |
| "20 indicators. 0 clarity." | A description of a cluttered chart, not of the viewer (Meta personal attributes) and not a claim about any product |
| Signals plan / Assist = one tap / Auto = hands-free | Owner Brief B16 (2026-09-25 revision) |
| Every result recorded, wins and losses | Owner Brief B3, B9; app Track record |
| Paper mode | app onboarding ("Paper mode — prove it first") |

## Not verified here — owner to confirm

- **Meta crypto-ads eligibility** for the advertiser account (Meta requires prior approval / licensing evidence for some crypto categories; check Business Settings → the ad account's policy status).
- Whether ASCI expects the disclaimer **also spoken** in audio-visual ads, and in the ad's own language (ads are Hinglish, disclaimer is English verbatim).
- Terms of Service do not yet cover the live USDT payment rail (audit 2026-09-24 §3.6).
