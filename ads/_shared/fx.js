/**
 * Shared effects for the ads. Everything is a pure function of time `t` (ms)
 * and a seed, like runtime.js, so a rendered frame is the frame the preview
 * shows. Load after runtime.js.
 *
 *   FX.rng(seed)                      deterministic 0..1 generator
 *   FX.icons()                        fills [data-logo] [data-logo-lg] [data-tick] [data-cross] [data-lock]
 *   FX.candles(canvas, opts)          -> { draw(t, o) }  live candlestick chart on a canvas
 *   FX.scramble(text, p, t, seed)     digits/letters decode left→right as p goes 0→1
 *   FX.camera(t, cfg)                 push-in per scene + kick bump + shake + flash + RGB split on cuts
 *   FX.burst(host, n, seed, colors)   -> { draw(t, t0, x, y) }  particle explosion
 */
(function () {
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));

  function rng(seed) {
    let s = seed % 2147483647 || 1;
    return () => ((s = (s * 16807) % 2147483647) / 2147483647);
  }

  const SVG = {
    logo: '<svg viewBox="0 0 46 52"><path d="M0 0h16v38h30v14H0z" fill="#0b1020"/></svg>',
    tick: '<svg viewBox="0 0 32 32"><path d="M6 17l7 7L27 9" stroke="#04140d" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    cross: '<svg viewBox="0 0 32 32"><path d="M9 9l14 14M23 9L9 23" stroke="#2a0710" stroke-width="5" stroke-linecap="round"/></svg>',
    // Padlock: the shackle is its own group so an ad can swing it open.
    lock: '<svg viewBox="0 0 120 150" overflow="visible"><g class="shackle"><path d="M28 70V44a32 32 0 0 1 64 0v26" stroke="currentColor" stroke-width="14" fill="none" stroke-linecap="round"/></g>' +
      '<rect x="8" y="64" width="104" height="82" rx="22" fill="currentColor"/><circle cx="60" cy="100" r="11" fill="#05081a"/><rect x="55" y="104" width="10" height="22" rx="5" fill="#05081a"/></svg>',
  };

  function icons() {
    const fill = (sel, html) => document.querySelectorAll(sel).forEach((el) => (el.innerHTML = html));
    fill("[data-logo]", SVG.logo);
    fill("[data-logo-lg]", SVG.logo.replace("viewBox", 'style="width:50px;height:58px" viewBox'));
    fill("[data-tick]", SVG.tick);
    fill("[data-cross]", SVG.cross);
    fill("[data-lock]", SVG.lock);
  }

  /**
   * A candlestick chart generated from a seed (mean-reverting random walk with
   * slow swings), so the same seed is the same market on every render.
   * draw(t, o): o.offset = candles scrolled (float, smooth), o.count = visible
   * candles, o.mas = [[period, color, width]], o.levels = [{price|rel, color,
   * label, p}], o.alpha, o.glow. The last visible candle breathes with t so the
   * chart reads as live even when the window is still.
   */
  function candles(canvas, opts = {}) {
    const ctx = canvas.getContext("2d");
    const W = canvas.width, H = canvas.height;
    const r = rng(opts.seed || 7);
    const N = opts.n || 600;
    const base = opts.base || 100;
    const vol = opts.vol || 0.9;
    const data = [];
    let p = base, drift = 0;
    for (let i = 0; i < N; i++) {
      if (i % 40 === 0) drift = (r() - 0.5) * vol * 0.5;
      const o = p;
      const c = o + drift + (r() - 0.5) * vol * 2 + (base - o) * 0.02;
      const hi = Math.max(o, c) + r() * vol * 0.9;
      const lo = Math.min(o, c) - r() * vol * 0.9;
      data.push({ o, c, hi, lo });
      p = c;
    }
    function ma(i, n) {
      let s = 0, k = 0;
      for (let j = Math.max(0, i - n + 1); j <= i; j++) { s += data[j].c; k++; }
      return s / k;
    }
    return {
      data,
      priceAt(i) { return data[Math.max(0, Math.min(N - 1, Math.floor(i)))].c; },
      draw(t, o = {}) {
        const count = o.count || 48;
        const off = o.offset || 0;
        const first = Math.floor(off);
        const frac = off - first;
        const pad = o.pad || 0.12;
        ctx.clearRect(0, 0, W, H);
        ctx.globalAlpha = o.alpha == null ? 1 : o.alpha;
        // Fixed vertical scale over a wide neighbourhood: autoscaling per frame
        // makes the whole chart jump when a candle scrolls out.
        let lo = Infinity, hi = -Infinity;
        for (let i = Math.max(0, first - 20); i < Math.min(N, first + count + 20); i++) {
          lo = Math.min(lo, data[i].lo); hi = Math.max(hi, data[i].hi);
        }
        if (o.range) { lo = o.range[0]; hi = o.range[1]; }
        const span = hi - lo || 1;
        const y = (v) => H - ((v - lo) / span) * H * (1 - 2 * pad) - H * pad;
        const cw = W / count;
        const x = (i) => (i - off) * cw + cw / 2;
        const live = first + count - 1;
        // grid
        if (o.grid !== false) {
          ctx.strokeStyle = "rgba(122,211,248,0.08)"; ctx.lineWidth = 2;
          for (let g = 1; g < 6; g++) { ctx.beginPath(); ctx.moveTo(0, (H * g) / 6); ctx.lineTo(W, (H * g) / 6); ctx.stroke(); }
        }
        // moving averages
        (o.mas || []).forEach(([n, color, w]) => {
          ctx.strokeStyle = color; ctx.lineWidth = w || 4; ctx.beginPath();
          for (let i = first; i <= Math.min(N - 1, live + 1); i++) {
            const X = x(i), Y = y(ma(i, n));
            i === first ? ctx.moveTo(X, Y) : ctx.lineTo(X, Y);
          }
          ctx.stroke();
        });
        // candles
        for (let i = first; i <= Math.min(N - 1, live + 1); i++) {
          const d = data[i];
          let c = d.c, h = d.hi, l = d.lo;
          if (i === live) {
            // breathing last candle
            const w = Math.sin(t / 170) * 0.35 + Math.sin(t / 61) * 0.18;
            c = d.o + (d.c - d.o) * (0.55 + 0.45 * frac) + w * vol;
            h = Math.max(h, c); l = Math.min(l, c);
          }
          const up = c >= d.o;
          const col = up ? (o.up || "#22e39b") : (o.down || "#ff4d6d");
          ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = Math.max(2, cw * 0.12);
          if (o.glow) { ctx.shadowColor = col; ctx.shadowBlur = o.glow; }
          ctx.beginPath(); ctx.moveTo(x(i), y(h)); ctx.lineTo(x(i), y(l)); ctx.stroke();
          const top = y(Math.max(c, d.o)), bh = Math.max(3, Math.abs(y(c) - y(d.o)));
          ctx.fillRect(x(i) - cw * 0.34, top, cw * 0.68, bh);
          ctx.shadowBlur = 0;
          if (i === live) this.lastY = y(c), this.lastX = x(i), this.lastPrice = c;
        }
        // horizontal levels, drawn left→right by p
        (o.levels || []).forEach((L) => {
          const p = clamp(L.p == null ? 1 : L.p);
          if (p <= 0) return;
          const Y = y(L.price);
          ctx.save();
          ctx.strokeStyle = L.color; ctx.lineWidth = 5; ctx.setLineDash([22, 14]);
          ctx.shadowColor = L.color; ctx.shadowBlur = 18;
          ctx.beginPath(); ctx.moveTo(0, Y); ctx.lineTo(W * p, Y); ctx.stroke();
          ctx.restore();
          L.y = Y;
        });
        ctx.globalAlpha = 1;
        return { y, x, lo, hi };
      },
    };
  }

  const GLYPHS = "0123456789";
  const LETTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ";
  /** Decode `text` left→right as p goes 0→1; undecoded chars flicker per 45ms. */
  function scramble(text, p, t, seed = 1) {
    const n = text.length;
    let out = "";
    const tick = Math.floor(t / 45);
    for (let i = 0; i < n; i++) {
      const ch = text[i];
      const revealAt = 0.15 + (0.85 * i) / Math.max(1, n);
      if (p >= revealAt || !/[0-9A-Z]/.test(ch)) { out += ch; continue; }
      const h = Math.abs(Math.sin((tick + 1) * 12.9898 + i * 78.233 + seed * 3.1) * 43758.5453) % 1;
      out += /[0-9]/.test(ch) ? GLYPHS[Math.floor(h * 10)] : LETTERS[Math.floor(h * LETTERS.length)];
    }
    return out;
  }

  /**
   * Camera for #cam: slow push inside each scene, bump on each kick, a shake
   * and an RGB split right after each cut, white flash overlay.
   * cfg: { cam, flash, cuts, beat, musicEnd, musicFrom, push, shake, split }
   * Returns the kick envelope (1 on the beat, decaying) for other visuals.
   */
  function camera(t, cfg) {
    const beat = cfg.beat || 500;
    const on = t >= (cfg.musicFrom || 0) && t < (cfg.musicEnd || Infinity);
    const kick = on ? Math.exp(-(t % beat) / 110) : 0;
    let sceneStart = 0;
    for (const c of cfg.cuts) if (t >= c) sceneStart = c;
    const drift = Math.min(1, (t - sceneStart) / 3000);
    const s = 1 + (cfg.push || 0.035) * drift + 0.012 * kick;
    let since = Infinity;
    for (const c of cfg.cuts) if (t >= c) since = t - c;
    const hit = since < 260 ? 1 - since / 260 : 0;
    const shake = (cfg.shake == null ? 14 : cfg.shake) * hit;
    const sx = Math.sin(t * 0.9) * shake, sy = Math.cos(t * 1.3) * shake * 0.7;
    cfg.cam.style.transform = `translate(${sx.toFixed(1)}px, ${sy.toFixed(1)}px) scale(${s.toFixed(4)})`;
    const split = (cfg.split == null ? 10 : cfg.split) * hit;
    cfg.cam.style.filter = split > 0.3
      ? `drop-shadow(${split.toFixed(1)}px 0 0 rgba(255,40,110,.75)) drop-shadow(${(-split).toFixed(1)}px 0 0 rgba(40,220,255,.75))`
      : "";
    if (cfg.flash) cfg.flash.style.opacity = (0.55 * Math.max(0, 1 - since / 170) * (since < 170 ? 1 : 0)).toFixed(3);
    return kick;
  }

  /** Particle explosion. draw(t, t0, x, y): nothing before t0, fades by t0+life. */
  function burst(host, n, seed, colors, life = 900) {
    const r = rng(seed);
    const ps = [];
    for (let i = 0; i < n; i++) {
      const el = document.createElement("i");
      const size = 6 + r() * 16;
      const col = colors[i % colors.length];
      el.style.cssText = `position:absolute; left:0; top:0; width:${size}px; height:${size}px; border-radius:${r() > 0.5 ? "50%" : "3px"};
        background:${col}; box-shadow:0 0 18px ${col}; opacity:0; pointer-events:none`;
      host.appendChild(el);
      const a = r() * Math.PI * 2, v = 0.6 + r() * 1.6;
      ps.push({ el, vx: Math.cos(a) * v, vy: Math.sin(a) * v - 0.5, spin: (r() - 0.5) * 2 });
    }
    return {
      draw(t, t0, x, y) {
        const d = t - t0;
        ps.forEach((q) => {
          if (d < 0 || d > life) { q.el.style.opacity = "0"; return; }
          const k = d / life;
          const X = x + q.vx * d * 0.9, Y = y + q.vy * d * 0.9 + 0.0009 * d * d;
          q.el.style.transform = `translate(${X.toFixed(1)}px, ${Y.toFixed(1)}px) rotate(${(q.spin * d).toFixed(0)}deg)`;
          q.el.style.opacity = (1 - k).toFixed(3);
        });
      },
    };
  }

  window.FX = { rng, icons, candles, scramble, camera, burst, clamp };
})();
