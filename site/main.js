/* DumDana site script v4
   - links from config.js, UTM source capture
   - waitlist forms → Mailchimp (JSONP), with captcha / connection fallback and email typo check
   - pack picker, savings calculator, sortable comparison, flavour vote, recipe bar
   - scroll reveal, count-up numbers, mobile menu, sticky header, mobile waitlist bar
   - analytics events for GA4 and Clarity */
(function () {
  "use strict";
  var C = window.DD_CONFIG || {};
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  function track(name, params) {
    try {
      if (typeof window.gtag === "function") window.gtag("event", name, params || {});
      if (typeof window.clarity === "function") window.clarity("event", name);
    } catch (e) { /* analytics must never break the page */ }
  }

  /* ---------- where the visitor came from (UTM tags) ---------- */
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
  } catch (e) { /* storage blocked */ }

  /* ---------- survey and social links from config.js ---------- */
  $$("[data-link]").forEach(function (a) {
    var key = a.getAttribute("data-link");
    var url = C[key];
    if (!url) { a.hidden = true; return; }
    a.href = url;
    a.addEventListener("click", function () {
      track(key === "surveyUrl" ? "survey_click" : "social_click", { link: key, location: a.getAttribute("data-where") || "" });
    });
  });
  if (!C.surveyUrl) {
    var note = $(".hero-note");
    if (note) note.textContent = "Free to join. One email when samples are ready, nothing else.";
  }
  $$("[data-track]").forEach(function (el) {
    el.addEventListener("click", function () { track(el.getAttribute("data-track"), { location: el.getAttribute("data-where") || "" }); });
  });

  /* ---------- header: shadow on scroll, mobile menu, active link ---------- */
  var head = $("#site-head");
  var menuBtn = $("#menu-btn");
  var nav = $("#main-nav");
  function onScroll() {
    if (head) head.classList.toggle("scrolled", window.scrollY > 8);
    if (window.scrollY < 200) $$(".nav a.active").forEach(function (l) { l.classList.remove("active"); });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  function closeMenu() { if (nav && menuBtn) { nav.classList.remove("open"); menuBtn.setAttribute("aria-expanded", "false"); } }
  if (menuBtn && nav) {
    menuBtn.addEventListener("click", function () {
      var open = !nav.classList.contains("open");
      nav.classList.toggle("open", open);
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    $$("a", nav).forEach(function (a) { a.addEventListener("click", closeMenu); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeMenu(); });
    document.addEventListener("click", function (e) { if (!head.contains(e.target)) closeMenu(); });
  }
  if ("IntersectionObserver" in window && nav) {
    var navLinks = $$("a[href^='/#']", nav);
    var secObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        navLinks.forEach(function (l) { l.classList.toggle("active", l.getAttribute("href") === "/#" + en.target.id); });
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    navLinks.forEach(function (l) { var s = document.getElementById(l.getAttribute("href").slice(2)); if (s) secObs.observe(s); });
  }

  /* ---------- scroll reveal + count-up ---------- */
  function countUp(el) {
    var end = +el.getAttribute("data-count");
    var pre = el.getAttribute("data-prefix") || "", suf = el.getAttribute("data-suffix") || "";
    if (reduceMotion) { el.textContent = pre + end + suf; return; }
    var t0 = null, dur = 1100;
    function step(t) {
      if (!t0) t0 = t;
      var p = Math.min(1, (t - t0) / dur);
      var v = Math.round(end * (1 - Math.pow(1 - p, 3)));
      el.textContent = pre + v + suf;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  var revealEls = $$("[data-reveal], #mix");
  if ("IntersectionObserver" in window && !reduceMotion) {
    var ro = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add("in");
        $$("[data-count]", en.target).forEach(countUp);
        ro.unobserve(en.target);
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });
    revealEls.forEach(function (el) { ro.observe(el); });
    // safety net: never leave content hidden
    setTimeout(function () { revealEls.forEach(function (el) { el.classList.add("in"); }); }, 4000);
  } else {
    revealEls.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---------- pack picker ---------- */
  var PACKS = {
    s: { protein: "7.5 g", weight: "30 g", cost: "₹26.70", label: "₹20 pack" },
    l: { protein: "18 g", weight: "70 g", cost: "₹16.70", label: "₹30 pack" }
  };
  var stage = $("#stage");
  function pick(k, user) {
    if (!stage || !PACKS[k]) return;
    stage.setAttribute("data-pack", k);
    $$(".picker button", stage).forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-pick") === k ? "true" : "false"); });
    $$("[data-f]", stage).forEach(function (dd) {
      dd.textContent = PACKS[k][dd.getAttribute("data-f")];
      dd.classList.remove("flash"); void dd.offsetWidth; dd.classList.add("flash");
    });
    if (user) track("pack_pick", { pack: PACKS[k].label });
  }
  if (stage) {
    $$("[data-pick]", stage).forEach(function (b) { b.addEventListener("click", function () { pick(b.getAttribute("data-pick"), true); }); });
    var packs = $("#packs");
    if (packs && !reduceMotion && window.matchMedia("(pointer: fine)").matches) {
      stage.addEventListener("pointermove", function (e) {
        var r = stage.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        packs.style.transform = "rotateY(" + (x * 10).toFixed(2) + "deg) rotateX(" + (-y * 8).toFixed(2) + "deg)";
      });
      stage.addEventListener("pointerleave", function () { packs.style.transform = ""; });
      packs.style.transition = "transform .3s cubic-bezier(.2,.7,.2,1)";
    }
  }

  /* ---------- sortable comparison table ---------- */
  var cmp = $("#cmp");
  if (cmp) {
    var tbody = cmp.tBodies[0];
    function sortBy(key) {
      var rows = $$("tr", tbody);
      rows.sort(function (a, b) {
        var x = +a.getAttribute("data-" + key), y = +b.getAttribute("data-" + key);
        if (key === "p100") return y - x;      // most protein first
        return x - y;                           // cheapest first
      });
      rows.forEach(function (r, i) {
        tbody.appendChild(r);
        if (!reduceMotion) { r.classList.remove("moved"); void r.offsetWidth; r.style.animationDelay = (i * 40) + "ms"; r.classList.add("moved"); }
      });
      $$(".sorter button").forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-sort") === key ? "true" : "false"); });
    }
    $$(".sorter button").forEach(function (b) {
      b.addEventListener("click", function () { sortBy(b.getAttribute("data-sort")); track("compare_sort", { by: b.getAttribute("data-sort") }); });
    });
    sortBy("p100");
  }

  /* ---------- recipe bar: highlight an ingredient ---------- */
  var mix = $("#mix");
  if (mix) {
    var hl = function (k) {
      mix.classList.toggle("hl", !!k);
      $$("[data-k]", mix).forEach(function (el) { el.classList.toggle("on", el.getAttribute("data-k") === k); });
    };
    $$("[data-k]", mix).forEach(function (el) {
      el.addEventListener("mouseenter", function () { hl(el.getAttribute("data-k")); });
      el.addEventListener("mouseleave", function () { hl(null); });
    });
  }

  /* ---------- flavour vote cards ---------- */
  $$(".flav").forEach(function (card) {
    card.addEventListener("click", function () {
      var v = card.getAttribute("data-flavour");
      $$(".flav").forEach(function (c) { c.setAttribute("aria-pressed", c === card ? "true" : "false"); });
      var radio = $('#waitlist input[name="FLAVOUR"][value="' + v + '"]');
      if (radio) radio.checked = true;
      var join = $("#join");
      if (join) {
        setTimeout(function () {
          join.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
          setTimeout(function () { var e = $("#f-email"); if (e) e.focus({ preventScroll: true }); }, reduceMotion ? 0 : 650);
        }, 350);
      }
    });
  });
  var initFlav = $('#waitlist input[name="FLAVOUR"]:checked');
  if (initFlav) $$(".flav").forEach(function (c) { c.setAttribute("aria-pressed", c.getAttribute("data-flavour") === initFlav.value ? "true" : "false"); });
  $$('#waitlist input[name="FLAVOUR"]').forEach(function (r) {
    r.addEventListener("change", function () {
      $$(".flav").forEach(function (c) { c.setAttribute("aria-pressed", c.getAttribute("data-flavour") === r.value ? "true" : "false"); });
    });
  });

  /* ---------- waitlist forms → Mailchimp ---------- */
  function setMsg(el, kind, text) { el.className = "form-msg " + kind; el.textContent = text; }
  function shake(el) { if (reduceMotion) return; el.classList.remove("shake"); void el.offsetWidth; el.classList.add("shake"); }

  function finishOnMailchimp(data, msg, where, intro) {
    msg.className = "form-msg info";
    msg.textContent = "";
    var p = document.createElement("span");
    p.textContent = (intro || "One more step: confirm you're not a robot on Mailchimp's page.") + " ";
    var b = document.createElement("button");
    b.type = "button";
    b.className = "linkbtn";
    b.textContent = "Finish signing up";
    b.addEventListener("click", function () {
      var f = document.createElement("form");
      f.method = "post"; f.action = C.mailchimpAction; f.target = "_blank";
      data.forEach(function (v, k) { var i = document.createElement("input"); i.type = "hidden"; i.name = k; i.value = v; f.appendChild(i); });
      document.body.appendChild(f); f.submit(); f.remove();
      track("generate_lead", { method: "waitlist_mailchimp_page", location: where, flavour: data.get("FLAVOUR") || "", source: source });
      msg.textContent = "Thanks! Finish on the Mailchimp tab, then check your inbox.";
    });
    msg.appendChild(p); msg.appendChild(b);
    track("waitlist_fallback", { location: where });
  }

  $$("form[data-waitlist]").forEach(function (form) {
    var msg = $(".form-msg", form);
    var btn = $("button[type=submit]", form);
    var label = btn.textContent;
    var where = form.getAttribute("data-where") || "form";
    var started = false;
    form.addEventListener("focusin", function () { if (!started) { started = true; track("waitlist_form_start", { location: where }); } });

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      setMsg(msg, "", "");
      var email = (form.EMAIL.value || "").trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
        setMsg(msg, "err", "Enter an email address like name@gmail.com."); shake(form.EMAIL); form.EMAIL.focus(); return;
      }
      var typo = email.match(/@(gmail|yahoo|hotmail|outlook|rediffmail|icloud)\.([a-z.]+)$/i);
      if (typo && typo[2].toLowerCase() !== "com" && !(typo[1].toLowerCase() === "yahoo" && /^(co\.in|in)$/i.test(typo[2]))) {
        setMsg(msg, "err", "Check your email address. Did you mean @" + typo[1].toLowerCase() + ".com?"); shake(form.EMAIL); form.EMAIL.focus(); return;
      }
      if (!C.mailchimpAction) { setMsg(msg, "err", "The waitlist opens soon. Please check back in a little while."); return; }
      if (!form.FLAVOUR) {
        var chosen = $(".flav[aria-pressed='true']");
        if (chosen) form.dataset.flavour = chosen.getAttribute("data-flavour");
      }
      var data = new URLSearchParams(new FormData(form));
      if (!data.get("FLAVOUR") && form.dataset.flavour) data.set("FLAVOUR", form.dataset.flavour);
      data.set("SOURCE", source + " (" + where + ")");
      var cb = "ddmc" + Date.now();
      var url = C.mailchimpAction.replace("/post?", "/post-json?") + "&" + data.toString() + "&c=" + cb;
      btn.disabled = true; btn.textContent = "Adding you…";
      var s = document.createElement("script");
      var timer = setTimeout(fail, 10000);
      function done() { clearTimeout(timer); btn.disabled = false; btn.textContent = label; s.remove(); window[cb] = function () {}; }
      function fail() { done(); finishOnMailchimp(data, msg, where, "Almost done: we couldn't connect automatically."); }
      window[cb] = function (res) {
        done();
        if (res && res.result === "success") {
          setMsg(msg, "ok", "You're on the list. Check your inbox and confirm your email.");
          form.reset();
          track("generate_lead", { method: "waitlist", location: where, flavour: data.get("FLAVOUR") || "", source: source });
          return;
        }
        var text = (res && res.msg ? String(res.msg) : "").replace(/<[^>]+>/g, "").replace(/^\d+\s*-\s*/, "");
        if (/captcha/i.test(text)) { finishOnMailchimp(data, msg, where); return; }
        setMsg(msg, "err", /already subscribed/i.test(text) ? "You're already on the list with this email."
          : /too many/i.test(text) ? "Too many tries from this email. Please wait a few minutes and try again."
          : (text || "That didn't go through. Check your email address and try again."));
      };
      s.onerror = fail;
      s.src = url;
      document.body.appendChild(s);
    });
  });

  /* ---------- savings calculator ---------- */
  var range = $("#calc-n");
  if (range) {
    var out = $("#calc-n-out"), elChips = $("#calc-chips"), elDd = $("#calc-dd"), elSave = $("#calc-save");
    var CHIPS_PER_10G = 50;            // ₹50 for 10 g protein (SuperYou, ₹50 for 40 g)
    var DD_PER_10G = 30 / 18 * 10;     // ₹30 pack, 18 g protein (target) → ₹16.67 per 10 g
    var fmt = function (n) { return "₹" + Math.round(n).toLocaleString("en-IN"); };
    var r10 = function (n) { return Math.round(n / 10) * 10; };
    var used = false;
    var calc = function () {
      var perMonth = +range.value * 30 / 7;
      var chips = r10(perMonth * CHIPS_PER_10G), dd = r10(perMonth * DD_PER_10G);
      out.textContent = range.value;
      elChips.textContent = fmt(chips); elDd.textContent = fmt(dd); elSave.textContent = fmt(chips - dd);
    };
    range.addEventListener("input", function () { calc(); if (!used) { used = true; track("calculator_used"); } });
    calc();
  }

  /* ---------- mobile waitlist bar: shows after the hero, hides at the form ---------- */
  var bar = $("#mcta"), hero = $("#top"), joinSec = $("#join");
  if (bar && hero && joinSec && "IntersectionObserver" in window) {
    var heroVisible = true, joinVisible = false;
    var update = function () { bar.hidden = heroVisible || joinVisible; };
    new IntersectionObserver(function (e) { heroVisible = e[0].isIntersecting; update(); }).observe(hero);
    new IntersectionObserver(function (e) { joinVisible = e[0].isIntersecting; update(); }).observe(joinSec);
  }

  /* ---------- how far people read ---------- */
  var marks = [25, 50, 75, 100], hit = {};
  window.addEventListener("scroll", function () {
    var h = document.documentElement;
    var pct = Math.round((h.scrollTop + innerHeight) / h.scrollHeight * 100);
    marks.forEach(function (m) { if (pct >= m && !hit[m]) { hit[m] = 1; track("scroll_depth", { percent: m }); } });
  }, { passive: true });
})();
