#!/usr/bin/env python3
"""Mechanical checks behind docs/compliance-checklist.md — run in CI.

The checklist is a list a human ticks before a creative spends money. Most of
it needs judgement; the part below does not, and a human ticking it by eye is
exactly how a 4.5s disclaimer or a stray "%" ships. So these run on every PR:

Per ad (ads/<name>/index.html):
  * the ASCI disclaimer is present VERBATIM, in the end card;
  * it is fully legible for >= 5s — from the end of its fade-in to the end of
    the video, with nothing taking it off screen early;
  * the four numbers that must move together do (CLAUDE.md): the stage's
    `data-end-at`, the disclaimer's `data-at`, the soundtrack's
    `music_until` = end-at, and its `end` = `data-duration`;
  * the disclaimer box starts inside the safe zone (y >= 285, < 1300);
  * "18+" is on screen.
Every ad, the landing page and the ad copy:
  * no performance claim: profit, win rate, returns, a percentage other than
    the sanctioned exit rule ("100% close"), "₹X/day";
  * no "safe", "guaranteed" (a disclaimer's "do not guarantee" is fine),
    "risk-free", "sure-shot";
  * never a bare "Signals FREE" — it is "Live signals 3 din FREE", because
    live signals are paid after the 3 days (checklist, claim table).

Only visible text is scanned — comments, <style> and <script> are stripped —
so a rule written down in a comment does not trip its own check.

    python tools/check_compliance.py            # check the repo
    python tools/check_compliance.py --self-test  # prove each rule still fires
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ASCI = (
    "Crypto products and NFTs are unregulated and can be highly risky. "
    "There may be no regulatory recourse for any loss from such transactions."
)
MIN_DISCLAIMER_MS = 5000
SAFE_TOP, SAFE_BOTTOM = 285, 1300

#: The one percentage the claim table sanctions: the exit rule (Owner Brief §3.2).
ALLOWED_PERCENT = re.compile(r"\b100\s*%\s*(close|exit)\b", re.I)
NEGATED_GUARANTEE = re.compile(r"\b(do|does|can) ?not guarantee|\bno guarantee", re.I)

FORBIDDEN: list[tuple[str, re.Pattern[str]]] = [
    ("profit claim", re.compile(r"\bprofit\w*|\bmunafa\b|\bkamai\b|\bkamao\b", re.I)),
    ("win-rate claim", re.compile(r"\b(win|hit|success)[\s-]?rate\b|\baccuracy\b", re.I)),
    ("returns claim", re.compile(r"\breturns?\b", re.I)),
    ("money-per-period claim", re.compile(
        r"₹\s*[\d,]+(\.\d+)?\s*(/|per|a|ek)\s*(day|din|week|hafta|month|mahina)\b", re.I)),
    ("'safe'", re.compile(r"\bsafe\b", re.I)),
    ("'risk-free'", re.compile(r"\brisk[\s-]?free\b", re.I)),
    ("'sure-shot'", re.compile(r"\bsure[\s-]?shot\b", re.I)),
]


def visible_text(markup: str) -> str:
    s = re.sub(r"<!--.*?-->", " ", markup, flags=re.S)
    s = re.sub(r"<(script|style)\b.*?</\1\s*>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def claim_problems(text: str) -> list[str]:
    out = []
    for label, pat in FORBIDDEN:
        for m in pat.finditer(text):
            out.append(f"{label}: …{text[max(0, m.start() - 30):m.end() + 30]}…")
    for m in re.finditer(r"\d+(?:\.\d+)?\s*%", text):
        if not ALLOWED_PERCENT.match(text, m.start()):
            out.append(f"percentage: …{text[max(0, m.start() - 30):m.end() + 30]}…")
    for m in re.finditer(r"\bguarant\w*", text, re.I):
        window = text[max(0, m.start() - 20):m.end()]
        if not NEGATED_GUARANTEE.search(window):
            out.append(f"'guaranteed': …{text[max(0, m.start() - 30):m.end() + 30]}…")
    for m in re.finditer(r"\bsignals\s+free\b", text, re.I):
        before = text[max(0, m.start() - 25):m.start()].lower()
        if "live" not in before or "3 din" not in before:
            out.append("bare 'Signals FREE' — write 'Live signals 3 din FREE': "
                       f"…{text[max(0, m.start() - 30):m.end() + 10]}…")
    return out


def _attr(tag: str, name: str) -> str | None:
    m = re.search(rf'\b{re.escape(name)}="([^"]*)"', tag)
    return m.group(1) if m else None


def ad_problems(markup: str) -> list[str]:
    problems: list[str] = []
    root = re.search(r"<html\b[^>]*>", markup)
    duration = _attr(root.group(0), "data-duration") if root else None
    stage = re.search(r'<div\b[^>]*\bid="stage"[^>]*>', markup)
    end_at = _attr(stage.group(0), "data-end-at") if stage else None
    if duration is None or end_at is None:
        return ["missing <html data-duration> or #stage data-end-at"]
    duration_ms, end_at_ms = int(duration), int(end_at)

    cues_m = re.search(r'<script[^>]*id="soundtrack"[^>]*>(.*?)</script>', markup, re.S)
    if not cues_m:
        problems.append("no #soundtrack cue list")
    else:
        cues = json.loads(cues_m.group(1))
        if cues.get("music_until") != end_at_ms:
            problems.append(f"soundtrack music_until {cues.get('music_until')} != data-end-at {end_at_ms}")
        if cues.get("end") != duration_ms:
            problems.append(f"soundtrack end {cues.get('end')} != data-duration {duration_ms}")

    disc = re.search(r'<div\b[^>]*\bclass="[^"]*\bdisclaimer\b[^"]*"[^>]*>(.*?)</div>', markup, re.S)
    if not disc:
        problems.append("no .disclaimer element")
    else:
        tag = disc.group(0)[: disc.group(0).index(">") + 1]
        if ASCI not in visible_text(disc.group(1)):
            problems.append("ASCI disclaimer is not verbatim in the .disclaimer element")
        at = int(_attr(tag, "data-at") or -1)
        fade = int(_attr(tag, "data-dur") or 0)
        until = _attr(tag, "data-until")
        if at != end_at_ms:
            problems.append(f"disclaimer data-at {at} != data-end-at {end_at_ms}")
        off = int(until) if until else duration_ms
        legible = min(off, duration_ms) - (at + fade)
        if legible < MIN_DISCLAIMER_MS:
            problems.append(f"disclaimer legible for {legible}ms (< {MIN_DISCLAIMER_MS}ms)")
        top = re.search(r"top:\s*(\d+)px", _attr(tag, "style") or "")
        if top and not SAFE_TOP <= int(top.group(1)) < SAFE_BOTTOM:
            problems.append(f"disclaimer top {top.group(1)}px outside the safe zone")

    text = visible_text(markup)
    if "18+" not in text:
        problems.append("no '18+' on screen")
    problems += claim_problems(text)
    return problems


def ad_copy_lines(md: str) -> str:
    """The copy itself: blockquotes and Headline/Description lines — not the
    prose explaining the rules, which names every forbidden word."""
    keep = [ln[1:].strip() for ln in md.splitlines() if ln.startswith(">")]
    keep += [ln for ln in md.splitlines()
             if re.match(r"\*\*(Headline|Description):\*\*", ln)]
    return " ".join(keep)


def check_repo(root: Path = ROOT) -> list[str]:
    problems: list[str] = []
    ads = sorted(p for p in (root / "ads").glob("*/index.html")
                 if not p.parent.name.startswith("_"))
    if not ads:
        problems.append("no ads found — the checker is looking in the wrong place")
    for ad in ads:
        problems += [f"{ad.relative_to(root)}: {p}" for p in ad_problems(ad.read_text())]
    site = root / "site" / "index.html"
    if site.exists():
        text = visible_text(site.read_text())
        if ASCI not in text:
            problems.append("site/index.html: ASCI disclaimer is not verbatim")
        if "18+" not in text:
            problems.append("site/index.html: no '18+'")
        problems += [f"site/index.html: {p}" for p in claim_problems(text)]
    copy = root / "docs" / "ad-copy.md"
    if copy.exists():
        lines = ad_copy_lines(copy.read_text())
        if not lines:
            problems.append("docs/ad-copy.md: found no copy lines to check")
        problems += [f"docs/ad-copy.md: {p}" for p in claim_problems(lines)]
    return problems


def self_test() -> list[str]:
    """Every rule must still fire on a violation, or a quietly broken regex
    reads as a clean repo."""
    ok_ad = (
        '<html data-duration="18000"><script type="application/json" id="soundtrack">'
        '{"music_until": 12500, "end": 18000}</script>'
        '<div id="stage" data-end-at="12500">'
        '<div class="disclaimer" style="top:865px" data-in="fade" data-at="12500" data-dur="300">'
        f"<p>{ASCI}</p><small>18+ only.</small></div></div></html>"
    )
    failures = []

    def expect(name: str, got: list[str], want_clean: bool) -> None:
        if want_clean and got:
            failures.append(f"{name}: expected clean, got {got}")
        if not want_clean and not got:
            failures.append(f"{name}: expected a violation, got none")

    expect("clean ad", ad_problems(ok_ad), True)
    expect("short disclaimer", ad_problems(ok_ad.replace('data-duration="18000"', 'data-duration="17000"')
                                            .replace('"end": 18000', '"end": 17000')), False)
    expect("music out of step", ad_problems(ok_ad.replace('"music_until": 12500', '"music_until": 12000')), False)
    expect("paraphrased ASCI", ad_problems(ok_ad.replace("highly risky", "risky")), False)
    expect("disclaimer outside safe zone", ad_problems(ok_ad.replace("top:865px", "top:120px")), False)
    expect("no 18+", ad_problems(ok_ad.replace("18+ only.", "")), False)
    for bad in ["Profit every day", "72% win rate", "Returns guaranteed", "₹500/day",
                "Totally safe", "risk-free", "sure-shot calls", "Signals FREE", "+12.5% last week",
                "Paisa kamao"]:
        expect(bad, claim_problems(bad), False)
    for good in ["Target pe 100% close.", "Live signals 3 din FREE.",
                 "3 din saare live signals FREE", "Past results do not guarantee future results.",
                 "<!-- no profit, no win rate -->"]:
        expect(good, claim_problems(visible_text(good)), True)
    return failures


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        failures = self_test()
        print("\n".join(failures) or "self-test: every rule fires, every allowance holds")
        return 1 if failures else 0
    problems = check_repo()
    if problems:
        print("Compliance check FAILED (docs/compliance-checklist.md):")
        print("\n".join(f"  - {p}" for p in problems))
        return 1
    print("Compliance check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
