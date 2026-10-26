/* DumDana site script: config links, waitlist forms (Mailchimp), savings calculator, analytics events */
(function () {
  "use strict";
  var C = window.DD_CONFIG || {};

  function track(name, params) {
    if (typeof window.gtag === "function") window.gtag("event", name, params || {});
    if (typeof window.clarity === "function") window.clarity("event", name);
  }

  /* ---------- where the visitor came from (UTM tags), saved with their signup ---------- */
  var source = "direct";
  try {
    var q = new URLSearchParams(location.search);
    if (q.get("utm_source")) {
      source = [q.get("utm_source"), q.get("utm_medium"), q.get("utm_campaign"), q.get("utm_content")].filter(Boolean).join(" / ");
      sessionStorage.setItem("dd_source", source);
    } else if (sessionStorage.getItem("dd_source")) {
      source = sessionStorage.getItem("dd_source");
    } else if (document.referrer && document.referrer.indexOf(location.host) === -1) {
      source = new URL(document.referrer).hostname;
    }
  } catch (e) { /* storage blocked: keep "direct" */ }

  /* ---------- survey and social links from config.js ---------- */
  function addUtm(url) {
    try {
      var u = new URL(url);
      if (/google\.com$|forms\.gle$/.test(u.hostname)) return url;
      u.searchParams.set("utm_source", "website");
      u.searchParams.set("utm_medium", "site_link");
      return u.toString();
    } catch (e) { return url; }
  }
  document.querySelectorAll("[data-link]").forEach(function (a) {
    var key = a.getAttribute("data-link");
    var url = C[key];
    if (!url) { a.hidden = true; return; }
    a.href = key === "surveyUrl" ? url : addUtm(url);
    a.addEventListener("click", function () {
      track(key === "surveyUrl" ? "survey_click" : "social_click", { link: key, location: a.getAttribute("data-where") || "" });
    });
  });
  // Hide the survey sentence in the hero until a survey link exists
  if (!C.surveyUrl) {
    var note = document.querySelector(".hero-note");
    if (note) note.textContent = "Free to join. One email when samples are ready, nothing else.";
  }

  document.querySelectorAll("[data-track]").forEach(function (el) {
    el.addEventListener("click", function () { track(el.getAttribute("data-track"), { location: el.getAttribute("data-where") || "" }); });
  });

  /* ---------- flavour links pre-select the flavour in the main form ---------- */
  document.querySelectorAll("[data-flavour]").forEach(function (a) {
    a.addEventListener("click", function () {
      var v = a.getAttribute("data-flavour");
      var radio = document.querySelector('#waitlist input[name="FLAVOUR"][value="' + v + '"]');
      if (radio) radio.checked = true;
      setTimeout(function () { var e = document.getElementById("f-email"); if (e) e.focus({ preventScroll: true }); }, 450);
    });
  });

  /* ---------- waitlist forms → Mailchimp (JSONP endpoint, visitor stays on the page) ---------- */
  function setMsg(el, kind, text) { el.className = "form-msg " + kind; el.textContent = text; }

  document.querySelectorAll("form[data-waitlist]").forEach(function (form) {
    var msg = form.querySelector(".form-msg");
    var btn = form.querySelector("button[type=submit]");
    var label = btn.textContent;
    var where = form.getAttribute("data-where") || "form";
    var started = false;

    form.addEventListener("focusin", function () {
      if (!started) { started = true; track("waitlist_form_start", { location: where }); }
    });

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      setMsg(msg, "", "");
      var email = (form.EMAIL.value || "").trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        setMsg(msg, "err", "Enter an email address like name@gmail.com.");
        form.EMAIL.focus();
        return;
      }
      if (!C.mailchimpAction) {
        setMsg(msg, "err", "The waitlist opens in a few hours. Please check back soon.");
        return;
      }
      var data = new URLSearchParams(new FormData(form));
      data.set("SOURCE", source + " (" + where + ")");
      var cb = "ddmc" + Date.now();
      var url = C.mailchimpAction.replace("/post?", "/post-json?") + "&" + data.toString() + "&c=" + cb;
      btn.disabled = true; btn.textContent = "Adding you…";
      var s = document.createElement("script");
      var timer = setTimeout(function () { fail("Couldn't reach the waitlist. Check your connection and try again."); }, 12000);
      function done() { clearTimeout(timer); btn.disabled = false; btn.textContent = label; s.remove(); try { delete window[cb]; } catch (e) { window[cb] = undefined; } }
      function fail(text) { done(); setMsg(msg, "err", text); }
      window[cb] = function (res) {
        done();
        if (res && res.result === "success") {
          setMsg(msg, "ok", "You're on the list. Check your inbox and confirm your email.");
          form.reset();
          track("generate_lead", { method: "waitlist", location: where, flavour: data.get("FLAVOUR") || "", source: source });
        } else {
          var text = (res && res.msg ? String(res.msg) : "").replace(/<[^>]+>/g, "").replace(/^\d+\s*-\s*/, "");
          setMsg(msg, "err", /already subscribed/i.test(text)
            ? "You're already on the list with this email."
            : (text || "That didn't go through. Check your email address and try again."));
        }
      };
      s.onerror = function () { fail("Couldn't reach the waitlist. Check your connection and try again."); };
      s.src = url;
      document.body.appendChild(s);
    });
  });

  /* ---------- savings calculator ---------- */
  var range = document.getElementById("calc-n");
  if (range) {
    var out = document.getElementById("calc-n-out");
    var elChips = document.getElementById("calc-chips");
    var elDd = document.getElementById("calc-dd");
    var elSave = document.getElementById("calc-save");
    var CHIPS_PER_10G = 50;          // ₹50 for 10 g protein (SuperYou, 40 g pack)
    var DD_PER_10G = 20 / 15.6 * 10; // ₹20 pack, 15.6 g protein target → ₹12.82 per 10 g
    var fmt = function (n) { return "₹" + Math.round(n).toLocaleString("en-IN"); };
    var r10 = function (n) { return Math.round(n / 10) * 10; };
    var used = false;
    var calc = function () {
      var perWeek = +range.value;
      var perMonth = perWeek * 30 / 7;
      var chips = r10(perMonth * CHIPS_PER_10G);
      var dd = r10(perMonth * DD_PER_10G);
      out.textContent = perWeek;
      elChips.textContent = fmt(chips);
      elDd.textContent = fmt(dd);
      elSave.textContent = fmt(chips - dd);
    };
    range.addEventListener("input", function () {
      calc();
      if (!used) { used = true; track("calculator_used"); }
    });
    calc();
  }

  /* ---------- mobile waitlist bar: shows after the hero, hides at the form ---------- */
  var bar = document.getElementById("mcta");
  var hero = document.getElementById("top");
  var join = document.getElementById("join");
  if (bar && hero && join && "IntersectionObserver" in window) {
    var heroVisible = true, joinVisible = false;
    var update = function () { bar.hidden = heroVisible || joinVisible; };
    new IntersectionObserver(function (e) { heroVisible = e[0].isIntersecting; update(); }).observe(hero);
    new IntersectionObserver(function (e) { joinVisible = e[0].isIntersecting; update(); }).observe(join);
  }

  /* ---------- how far people read ---------- */
  var marks = [25, 50, 75, 100], hit = {};
  window.addEventListener("scroll", function () {
    var h = document.documentElement;
    var pct = Math.round((h.scrollTop + innerHeight) / h.scrollHeight * 100);
    marks.forEach(function (m) { if (pct >= m && !hit[m]) { hit[m] = 1; track("scroll_depth", { percent: m }); } });
  }, { passive: true });
})();
