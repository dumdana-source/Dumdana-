/* Loads Google Analytics 4 and Microsoft Clarity using the IDs in config.js. No code changes needed: just fill in config.js. */
(function () {
  var C = window.DD_CONFIG || {};
  if (C.ga4Id && /^G-[A-Z0-9]+$/i.test(C.ga4Id)) {
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(C.ga4Id);
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", C.ga4Id);
  }
  if (C.clarityId && /^[a-z0-9]+$/i.test(C.clarityId)) {
    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = 1; t.src = "https://www.clarity.ms/tag/" + i;
      y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
    })(window, document, "clarity", "script", C.clarityId);
  }
})();
