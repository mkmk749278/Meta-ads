/**
 * Device-aware CTA for the ad landing page.
 *
 *  iPhone/iPad → primary "Lumin kholo" = the web app (app.luminapp.org), plus
 *                Add-to-Home-Screen steps (push notifications only work from
 *                the home-screen app on iOS 16.4+).
 *  Android     → primary "Google Play", secondary the web app.
 *  Desktop     → both.
 *  Instagram / Facebook in-app browser → a banner telling the user to open
 *                Safari/Chrome, because Add to Home Screen does not exist there.
 *
 * UTM parameters from the ad click are forwarded to both destinations. Play
 * receives them in `referrer`, which is how Play Console attributes installs.
 * The Meta Pixel loads only when config.js carries an ID; a click on any CTA
 * fires a standard `Lead` event naming the destination.
 */
(function () {
  const cfg = window.LUMIN_CONFIG || {};
  const ua = navigator.userAgent || "";
  const isIOS = /iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  const isAndroid = /Android/.test(ua);
  const inApp = /FBAN|FBAV|FB_IAB|Instagram/.test(ua);

  // ---- UTM passthrough ----------------------------------------------------
  const incoming = new URLSearchParams(location.search);
  const utm = new URLSearchParams();
  for (const [k, v] of incoming) if (/^utm_|^fbclid$/.test(k)) utm.set(k, v);
  if (!utm.has("utm_source")) utm.set("utm_source", "landing");

  const webUrl = new URL(cfg.webAppUrl || "https://app.luminapp.org/");
  utm.forEach((v, k) => webUrl.searchParams.set(k, v));
  const playUrl = new URL(cfg.playUrl || "https://play.google.com/store/apps/details?id=org.luminapp.lumin");
  const ref = new URLSearchParams(); utm.forEach((v, k) => k.startsWith("utm_") && ref.set(k, v));
  playUrl.searchParams.set("referrer", ref.toString());

  // ---- Meta Pixel (only with an ID) ----------------------------------------
  const pixel = (cfg.metaPixelId || "").trim();
  if (/^\d{6,20}$/.test(pixel)) {
    /* eslint-disable */
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
    n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
    n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
    document,'script','https://connect.facebook.net/en_US/fbevents.js');
    /* eslint-enable */
    fbq("init", pixel);
    fbq("track", "PageView");
    fbq("track", "ViewContent", { content_name: isIOS ? "ios" : isAndroid ? "android" : "desktop" });
  }
  const track = (dest) => { if (window.fbq) fbq("track", "Lead", { content_name: dest }); };

  // ---- Wire the CTAs --------------------------------------------------------
  const primary = document.getElementById("cta-primary");
  const secondary = document.getElementById("cta-secondary");
  const note = document.getElementById("cta-note");

  const set = (el, label, href, dest) => { el.textContent = label; el.href = href; el.dataset.dest = dest; };
  if (isAndroid) {
    set(primary, "Google Play se install karo", playUrl, "play");
    set(secondary, "Ya web app kholo", webUrl, "webapp");
  } else if (isIOS) {
    set(primary, "Lumin kholo (iPhone)", webUrl, "webapp");
    secondary.hidden = true;
    note.textContent = "App Store ki zarurat nahi · 18+ only · 3 din live signals free";
    document.getElementById("a2hs").hidden = false;
  } else {
    set(primary, "Web app kholo", webUrl, "webapp");
    set(secondary, "Google Play (Android)", playUrl, "play");
  }

  // Every CTA that points at a destination records the Lead, then navigates.
  document.querySelectorAll("a.cta, a.small-cta").forEach((a) => {
    if (a.getAttribute("href") === "#get") return;
    a.addEventListener("click", (e) => {
      if (!window.fbq) return;
      e.preventDefault();
      track(a.dataset.dest || "unknown");
      setTimeout(() => (location.href = a.href), 250);
    });
  });

  // ---- In-app browser banner ------------------------------------------------
  if (inApp) {
    const bar = document.getElementById("iab");
    bar.hidden = false;
    if (!isIOS) bar.innerHTML = bar.innerHTML.replace("(Safari)", "(Chrome)").replace("iPhone pe app install", "Best experience");
    document.getElementById("copy")?.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(location.href); } catch (_) { /* older in-app webviews */ }
      document.getElementById("copy").textContent = "Copied ✓";
    });
  }
})();
