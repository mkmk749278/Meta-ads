/**
 * Shared scenery injected into every ad: ambient background, brand bar,
 * and the closing CTA + ASCI disclaimer card.
 *
 * Load this BEFORE runtime.js (both at the end of <body>): runtime.js
 * collects [data-in] elements on DOMContentLoaded, and everything added
 * here must exist by then.
 *
 * The end card starts at #stage[data-end-at] and runs to the end of the
 * ad. Every ad is 20s with the end card at 14.5s, so the disclaimer is on
 * screen for 5.5s — above the 5s ASCI minimum with margin for Meta's
 * encoder trimming a few frames.
 */
(function () {
  const stage = document.getElementById("stage");
  const endAt = +(stage.dataset.endAt || 14500);

  // Deterministic PRNG so every render is identical.
  let seed = 7;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);

  const L_SVG = '<svg viewBox="0 0 46 52"><path d="M0 0h16v38h30v14H0z" fill="#0b1020"/></svg>';
  window.LUMIN_L = L_SVG;
  window.TICK_SVG = '<svg viewBox="0 0 32 32"><path d="M6 17l7 7L27 9" stroke="#04140d" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  window.CROSS_SVG = '<svg viewBox="0 0 32 32"><path d="M9 9l14 14M23 9L9 23" stroke="#2a0710" stroke-width="5" stroke-linecap="round"/></svg>';

  // --- background candles -------------------------------------------------
  let candles = "";
  let price = 900;
  for (let i = 0; i < 26; i++) {
    const x = 20 + i * 41;
    const move = (rnd() - 0.42) * 90;
    const o = price, c = price - move;
    const hi = Math.min(o, c) - rnd() * 40, lo = Math.max(o, c) + rnd() * 40;
    const up = c < o;
    const col = up ? "#22e39b" : "#ff4d6d";
    candles += `<line x1="${x + 10}" x2="${x + 10}" y1="${hi}" y2="${lo}" stroke="${col}" stroke-width="3"/>` +
      `<rect x="${x}" y="${Math.min(o, c)}" width="20" height="${Math.max(6, Math.abs(o - c))}" fill="${col}" rx="3"/>`;
    price = c;
  }
  const bg = document.createElement("div");
  bg.innerHTML =
    `<svg class="bg-candles" viewBox="0 0 1080 1920" preserveAspectRatio="none">${candles}</svg>` +
    '<div class="grid-floor"></div>';
  for (let i = 0; i < 22; i++) {
    const p = document.createElement("div");
    p.className = "particle";
    p.style.left = `${Math.round(rnd() * 1060)}px`;
    p.style.top = `${Math.round(900 + rnd() * 1000)}px`;
    p.style.animationDuration = `${(5 + rnd() * 6).toFixed(2)}s`;
    p.style.animationDelay = `-${(rnd() * 8).toFixed(2)}s`;
    const s = 3 + rnd() * 6;
    p.style.width = p.style.height = `${s.toFixed(1)}px`;
    bg.appendChild(p);
  }
  // Lower third: an always-moving market line + a scrolling price tape.
  // Decorative only — nothing here is a claim, and it sits in the zone
  // Reels covers with its caption, so no message may depend on it.
  let pts = [], y = 250;
  for (let i = 0; i <= 36; i++) { y = Math.max(90, Math.min(360, y + (rnd() - 0.47) * 70)); pts.push([i * 30, y]); }
  const line = pts.map((p, i) => (i ? "L" : "M") + p[0] + " " + p[1].toFixed(1)).join(" ");
  const last = pts[pts.length - 1];
  bg.insertAdjacentHTML("beforeend", `
    <svg class="deco-chart" viewBox="0 0 1080 420">
      <defs><linearGradient id="dg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#38d6ff" stop-opacity=".35"/><stop offset="1" stop-color="#38d6ff" stop-opacity="0"/></linearGradient></defs>
      <path class="area" d="${line} L1080 420 L0 420 Z" fill="url(#dg)"/>
      <path d="${line}" stroke="#38d6ff" stroke-width="5" fill="none" style="filter:drop-shadow(0 0 10px #38d6ff)"/>
      <circle class="glowdot" cx="${last[0] - 6}" cy="${last[1]}" r="12" fill="#fff" style="filter:drop-shadow(0 0 14px #38d6ff)"/>
    </svg>`);
  const tape = [["BTC", "u"], ["ETH", "d"], ["SOL", "u"], ["BNB", "u"], ["XRP", "d"], ["DOGE", "u"], ["AVAX", "d"], ["LINK", "u"], ["TON", "u"], ["ARB", "d"]]
    .map(([s, d]) => `<b>${s}USDT</b><span class="${d}">${d === "u" ? "▲" : "▼"}</span>`).join("");
  bg.insertAdjacentHTML("beforeend", `<div class="ticker"><div class="ticker-track">${tape}${tape}</div></div>`);
  stage.prepend(...bg.childNodes);

  // --- brand bar ------------------------------------------------------------
  const bar = document.createElement("div");
  bar.className = "brandbar";
  bar.dataset.out = "fade"; bar.dataset.until = String(endAt - 300);
  bar.innerHTML = `<div class="logo">${L_SVG}</div><div><div class="name">Lumin</div><div class="sub">Crypto Signals</div></div>`;
  stage.appendChild(bar);

  // --- end card -------------------------------------------------------------
  const end = document.createElement("div");
  end.innerHTML = `
    <div class="abs center-x" style="top:230px; width:100%; text-align:center" data-in="pop" data-at="${endAt}" data-dur="700">
      <div class="logo" style="width:150px;height:150px;border-radius:40px;margin:0 auto 30px">${L_SVG.replace('viewBox="0 0 46 52"', 'viewBox="0 0 46 52" style="width:74px;height:84px"')}</div>
      <div class="h2">Signals <span class="grad-green">FREE.</span></div>
      <div class="h2" style="margin-top:8px">Auto Trade <span class="grad">jab chaho.</span></div>
    </div>
    <div class="abs center-x" style="top:620px; text-align:center; width:100%" data-in="up" data-at="${endAt + 350}" data-dur="600">
      <div class="cta glow-pulse">Lumin try karo
        <svg width="40" height="40" viewBox="0 0 40 40"><path d="M8 20h24M22 10l10 10-10 10" stroke="#041022" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </div>
      <div class="body" style="margin-top:28px; color:#cfe3ff">app.luminapp.org &nbsp;·&nbsp; Google Play</div>
    </div>
    <div class="disclaimer" style="top:840px" data-in="fade" data-at="${endAt}" data-dur="400">
      <h4>RISK DISCLAIMER</h4>
      <p>Crypto products and NFTs are unregulated and can be highly risky. There may be no regulatory recourse for any loss from such transactions.</p>
      <small>Futures trading carries a high risk of loss. Signals are not financial advice. 18+ only.</small>
    </div>`;
  stage.append(...end.children);
})();
