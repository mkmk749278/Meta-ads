/**
 * Deterministic ad timeline.
 *
 * Every visual in an ad is a pure function of time `t` (ms), so the MP4
 * renderer (tools/render.py) can seek to any frame and get the identical
 * picture the browser preview shows. Two mechanisms:
 *
 *   1. Declarative tweens on elements:
 *        data-in="up"   data-at="1200" data-dur="600"      (enter)
 *        data-out="fade" data-until="5200" data-odur="400"  (exit)
 *      in types: fade up down left right pop zoom wipe blur draw
 *   2. Ambient CSS animations (infinite glows, radar sweeps): paused and
 *      seeked via document.getAnimations(), so they are frame-exact too.
 *   3. Custom per-frame hooks: Ad.onFrame(t => ...), used for counters and
 *      price paths.
 *
 * Preview: open the page in any browser; it loops in real time.
 * Render:  the renderer calls window.Ad.seek(ms) once per frame.
 */
(function () {
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const ease = {
    out: (p) => 1 - Math.pow(1 - p, 3),
    inOut: (p) => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2),
    back: (p) => {
      const c1 = 1.70158, c3 = c1 + 1;
      return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2);
    },
  };

  const hooks = [];
  let tweened = [];

  function collect() {
    tweened = [...document.querySelectorAll("[data-in],[data-out]")].map((el) => ({
      el,
      kind: el.dataset.in || null,
      at: +(el.dataset.at || 0),
      dur: +(el.dataset.dur || 600),
      out: el.dataset.out || null,
      until: el.dataset.until ? +el.dataset.until : Infinity,
      odur: +(el.dataset.odur || 400),
      // .center-x relies on translateX(-50%); keep it under the tween transform.
      baseTransform: (el.classList.contains("center-x") ? "translateX(-50%) " : "") + (el.dataset.base || ""),
    }));
    tweened.forEach(({ el, kind }) => {
      if (kind === "draw") {
        el.setAttribute("pathLength", "1");
        el.style.strokeDasharray = "1";
      }
    });
  }

  function apply(t) {
    for (const tw of tweened) {
      const { el, kind, at, dur, out, until, odur, baseTransform } = tw;
      let opacity = 1, tx = 0, ty = 0, sc = 1, blur = 0, clip = null;
      if (kind) {
        const raw = clamp((t - at) / dur);
        const p = kind === "pop" ? ease.back(raw) : ease.out(raw);
        const q = ease.out(raw);
        switch (kind) {
          case "fade": opacity = q; break;
          case "up": opacity = q; ty = (1 - p) * 70; break;
          case "down": opacity = q; ty = (1 - p) * -70; break;
          case "left": opacity = q; tx = (1 - p) * -110; break;
          case "right": opacity = q; tx = (1 - p) * 110; break;
          case "pop": opacity = q; sc = 0.55 + 0.45 * p; break;
          case "zoom": opacity = q; sc = 1.25 - 0.25 * p; break;
          case "blur": opacity = q; blur = (1 - q) * 24; sc = 1.08 - 0.08 * q; break;
          case "wipe": clip = `inset(0 ${(1 - q) * 100}% 0 0)`; break;
          case "draw": el.style.strokeDashoffset = String(1 - ease.inOut(raw)); break;
        }
      }
      if (out && t > until) {
        const r = ease.out(clamp((t - until) / odur));
        opacity *= 1 - r;
        if (out === "up") ty -= r * 60;
        if (out === "shrink") sc *= 1 - 0.15 * r;
        if (out === "left") tx -= r * 140;
      }
      el.style.opacity = opacity.toFixed(4);
      el.style.visibility = opacity < 0.002 ? "hidden" : "visible";
      if (kind !== "draw") {
        el.style.transform =
          `${baseTransform} translate(${tx.toFixed(2)}px, ${ty.toFixed(2)}px) scale(${sc.toFixed(4)})`;
        el.style.filter = blur > 0.05 ? `blur(${blur.toFixed(2)}px)` : "";
        if (clip) el.style.clipPath = clip;
      }
    }
  }

  const Ad = {
    duration: +(document.documentElement.dataset.duration || 20000),
    ease, clamp,
    onFrame(fn) { hooks.push(fn); },
    /** Seek every animated thing to time t (ms). */
    seek(t) {
      document.getAnimations().forEach((a) => { a.pause(); a.currentTime = t; });
      apply(t);
      hooks.forEach((fn) => fn(t));
    },
    /** Linear 0..1 progress of t across [a, b]. */
    span(t, a, b) { return clamp((t - a) / (b - a)); },
  };
  window.Ad = Ad;

  window.addEventListener("DOMContentLoaded", () => {
    collect();
    Ad.seek(0);
    const rendering = new URLSearchParams(location.search).has("render");
    if (!rendering) {
      const start = performance.now();
      const loop = (now) => { Ad.seek((now - start) % Ad.duration); requestAnimationFrame(loop); };
      document.fonts.ready.then(() => requestAnimationFrame(loop));
    }
    window.__adReady = true;
  });
})();
