# Campaign plan

## What went wrong with the first campaign (23–24 Sep 2026)

| Metric | Value | Reading |
|---|---|---|
| Spend | ₹293.70 | |
| Impressions / reach | 5,371 / 4,072 | |
| Link clicks | 862 | **16% CTR** — ~10x normal; cheap accidental taps (check Placement breakdown for Audience Network) |
| Cost per click | ~₹0.34 | too cheap to be intent |
| App installs (Meta) | 0 | **unmeasurable**: the app has no Meta SDK/attribution, so Meta cannot see an install whatever happens |

An App Promotion campaign for a Play app also delivers only to Android, so it
never reached iPhone users at all.

## New structure

Everything goes to the landing page (`site/`, GitHub Pages), which routes by
device: iPhone → web app + Add-to-Home-Screen steps; Android → Play Store with
UTMs in `referrer`. That gives a measurable funnel **without touching the app**:

| Step | Where you read it |
|---|---|
| Landing page view | Ads Manager (needs the Pixel ID in `site/config.js`) |
| CTA click (`Lead`, `content_name` = `webapp` / `play`) | Ads Manager / Events Manager |
| Android install from the ad | Play Console → Acquisition → **Tracked channels (UTM)** |
| New sign-ups | engine user count (ops), day over day |

### Campaign 1 — iPhone → web app
- Objective: **Traffic → Landing page views** until the Pixel has ~50 `Lead` events, then switch the optimisation to **Leads** (website, `Lead` event).
- Ad set: India · 21–45 · **iOS devices only** · Advantage+ placements **minus Audience Network**.
- URL: `https://mkmk749278.github.io/Meta-ads/?utm_source=meta&utm_medium=paid&utm_campaign=ios_web&utm_content={{ad.name}}`
- Budget: ₹250/day.

### Campaign 2 — Android → Play
- Objective: **Traffic → Landing page views** (not App Promotion — Meta cannot see installs).
- Ad set: India · 21–45 · **Android only** · minus Audience Network.
- URL: same page with `utm_campaign=android_play`.
- Budget: ₹250/day.

Both campaigns: **three ads in each ad set**, one per hook, so Meta splits
delivery and the hook is the only thing that differs:

| Ad name (`utm_content`) | File | Hook |
|---|---|---|
| `hero_3am_auto` | `out/hero-auto-trade.mp4` | Outcome: "Aap so rahe the. Trade lag gaya." |
| `b_unlock_live` | `out/unlock-live.mp4` | Curiosity: "Ye signal abhi LIVE hai." |
| `c_chaos_clarity` | `out/chaos-clarity.mp4` | Pain: "20 indicators. 0 clarity." |

In Ads Manager set each ad's cover to its `out/<ad>.jpg` for Reels/Stories and
`out/<ad>_4x5.jpg` for Feed. Frame 0 is the same picture, so autoplay starts on
the cover rather than cutting away from it.

**Picking the winner.** After ~₹1,500 per ad set (or 7 days), compare the three on
**hook rate** first (3-second plays ÷ impressions), then **cost per `Lead`**.
Move the budget to the best one and pause the others; keep the loser's source,
since a hook that loses on Android can win on iPhone. Don't judge on CTR alone:
the first campaign's 16% CTR was accidental taps.

## Reading the first 5–7 days

- **CTR above ~6% with few `Lead` events** → still accidental taps; check placements again.
- **Landing views fine, `Lead` rate under ~10%** → the landing page, not the ad, is the leak.
- **`Lead` fine, few sign-ups** → the in-app funnel is the leak. Since 2026-09-25 a visitor enters on one welcome screen with no phone number and sees live signals masked; sign-up is asked only on "Sign up free to see signal". Compare guests opened vs accounts created in ops before changing the ads.
- **Hook rate** (3-second video plays ÷ impressions) is the read on the cover and the first 2.5s. Under ~25% means the hook, not the offer, is the problem.
- **Hold rate** (ThruPlays ÷ 3-second plays): if people drop before 12.5s they never see the CTA.
- Judge the ad by **cost per `Lead`**, never by clicks.

## Before you spend

1. Paste the Pixel ID into `site/config.js` (Events Manager → Data sources).
2. Repo Settings → Pages → Source: **GitHub Actions**; merge to `main` → the page deploys.
3. Optional custom domain: Settings → Pages → Custom domain `get.luminapp.org`, then a Cloudflare DNS **CNAME** `get` → `mkmk749278.github.io` (DNS only / grey cloud until the certificate issues).
4. Confirm the account's crypto-advertising eligibility in Meta Business Settings (see `compliance-checklist.md`).
5. Upload the three `out/*.mp4`. Each carries its own synthesized soundtrack (−14 LUFS, beat-synced). **Don't** add library music over it, or the SFX and cuts drift off the beat.
