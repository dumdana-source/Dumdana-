"""Builds the DumDana static site into ./site  (python3 build.py)"""
import json, os, shutil, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "brand"))
from parts2 import wordmark, mark, lockup, FOREST, AMBER, WHITE
from pack2 import pack

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "site")

# ---------------------------------------------------------------- config
# Fill these in after creating the accounts, then run: python3 build.py
CONFIG = {
    "siteUrl": "https://dumdana.vercel.app",
    "ga4Id": "",              # e.g. G-AB12CD34EF   (Google Analytics 4 → Admin → Data streams)
    "clarityId": "",          # e.g. tq1abc2def     (Clarity → Settings → Overview → Project ID)
    "searchConsoleToken": "", # content="..." value from Search Console's HTML-tag method
    "mailchimpAction": "",    # form action URL from Mailchimp's embedded form code
    "surveyUrl": "",          # Google Form share link (forms.gle/...)
    "instagram": "https://www.instagram.com/eatdumdana/",
    "youtube": "https://www.youtube.com/@eatdumdana",
}
cfg_path = os.path.join(ROOT, "config.json")
if os.path.exists(cfg_path):
    CONFIG.update(json.load(open(cfg_path)))
SITE = CONFIG["siteUrl"].rstrip("/")

SOURCES = [
    ("Farmley Healthy Snacking Report 2026, via Open magazine", "https://openthemagazine.com/india/healthy-snacking-on-the-rise-86-of-indians-prioritise-protein-farmley-report-finds"),
    ("SuperYou protein chips launch, Storyboard18", "https://www.storyboard18.com/brand-marketing/ranveer-singh-backed-superyou-launches-high-protein-chips-eyes-rs-25000-cr-snack-market-66666.htm"),
    ("The ₹10 protein push, Agro & Food Processing", "https://agronfoodprocessing.com/?p=31468"),
    ("Why ₹5 and ₹10 packs are getting harder to make, Outlook Business", "https://www.outlookbusiness.com/corporate/fmcg-5-10-rupees-packs-costs-rising-brands-margins-declining-shrinkflation"),
    ("Indian food composition data, roasted Bengal gram, McGill CINE", "https://www.mcgill.ca/cine/sites/cine/files/Dalit_Datatables_pulses_Jn06.pdf"),
    ("Soy nuts nutrition, USDA FoodData Central via GetFoodFacts", "https://getfoodfacts.com/food/soy-nuts-2707433"),
    ("Roasted unsalted peanuts nutrition, FatSecret", "https://www.fatsecret.co.za/calories-nutrition/generic/roasted-unsalted-peanuts"),
    ("Roasted chana wholesale prices, IndiaMART", "https://dir.indiamart.com/patna/roasted-chana.html"),
    ("FSSAI protein claims explained, Khaitan & Co", "https://compass.khaitanco.com/protein-on-trial-regulating-nutritional-claims-in-indias-growing-food-market"),
    ("High-protein claim thresholds, Prowess Buzz", "https://prowessbuzz.com/high-protein-claims-food-compliance/"),
]

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400..700&display=swap" rel="stylesheet">')


def analytics():
    out = []
    if CONFIG["ga4Id"]:
        gid = CONFIG["ga4Id"]
        out.append(f'<script async src="https://www.googletagmanager.com/gtag/js?id={gid}"></script>'
                   f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}"
                   f"gtag('js',new Date());gtag('config','{gid}');</script>")
    if CONFIG["clarityId"]:
        out.append('<script>(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};'
                   't=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];'
                   f'y.parentNode.insertBefore(t,y);}})(window,document,"clarity","script","{CONFIG["clarityId"]}");</script>')
    if CONFIG["searchConsoleToken"]:
        out.append(f'<meta name="google-site-verification" content="{CONFIG["searchConsoleToken"]}">')
    return "\n".join(out)


def head(title, desc, path, extra_ld=None, og_type="website"):
    url = SITE + path
    ld = [{
        "@context": "https://schema.org", "@type": "Organization", "name": "DumDana",
        "url": SITE + "/", "logo": SITE + "/assets/dumdana-mark-512.png",
        "sameAs": [CONFIG["instagram"], CONFIG["youtube"]],
    }]
    if extra_ld:
        ld += extra_ld
    return f'''<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="{FOREST}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="DumDana">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/og-image.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
{FONTS}
<link rel="stylesheet" href="/styles.css">
{analytics()}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>'''


def header(home=True):
    links = ('<a href="/#price">Compare</a><a href="/#inside">Ingredients</a>'
             '<a href="/#standards">Our standards</a><a href="/#flavours">Flavours</a><a href="/blog/">Blog</a>')
    return f'''<a class="skip" href="#main">Skip to content</a>
<div class="status"><div class="wrap"><span><strong>Market test:</strong> DumDana isn't on sale yet.</span><a href="/#join" data-track="cta_click" data-where="status-bar">Join the waitlist for first samples</a></div></div>
<header class="site-head">
  <div class="wrap">
    <a class="brand" href="/" aria-label="DumDana home">{lockup().replace('role="img" aria-label="DumDana"', 'aria-hidden="true"')}</a>
    <nav class="nav" aria-label="Main">
      {links}
      <a class="btn btn-primary" href="/#join" data-track="cta_click" data-where="header">Join waitlist</a>
    </nav>
  </div>
</header>'''


def footer():
    srcs = "".join(f'<li><a href="{u}" rel="noopener" target="_blank">{t}</a></li>' for t, u in SOURCES)
    return f'''<footer class="site-foot">
  <div class="wrap">
    <div class="top">
      {wordmark('#FFFFFF').replace('<svg ', '<svg class="word" aria-hidden="true" ')}
      <nav aria-label="Footer">
        <a data-link="instagram" data-where="footer" href="#" rel="noopener" target="_blank">Instagram</a>
        <a data-link="youtube" data-where="footer" href="#" rel="noopener" target="_blank">YouTube</a>
        <a href="/blog/">Blog</a>
        <a href="/privacy/">Privacy</a>
      </nav>
    </div>
    <p class="honest">DumDana is a student market-testing project. Nothing is on sale yet: we're finding out whether people want a ₹10 protein namkeen before anyone makes it. Nutrition values are targets calculated from standard food data and still need a lab test.</p>
    <details class="sources">
      <summary>Sources for the numbers on this site</summary>
      <ol>{srcs}</ol>
    </details>
    <p class="copy">© 2026 DumDana. A student market-testing project.</p>
  </div>
</footer>
<script src="/config.js"></script>
<script src="/main.js" defer></script>
</body>
</html>'''


FAQ = [
    ("Can I buy DumDana right now?",
     "<p>Not yet. DumDana is a market test run by a college team. We're checking whether people want a ₹10 protein namkeen before making it. Join the waitlist and you'll hear first if it goes ahead.</p>"),
    ("Where do the protein numbers come from?",
     "<p>We calculated them from published nutrition data: Indian food composition tables for roasted chana, and USDA data for soy nuts and peanuts. They're targets, not lab results. No value goes on a real pack until an accredited lab has tested it.</p>"),
    ("Why 25 g in the ₹10 pack and not more?",
     "<p>After the shop's margin, the distributor's margin and 5% GST, a ₹10 pack leaves the maker about ₹6.50. A 30 g pack would leave almost nothing for packaging and transport. 25 g keeps the price honest. If you want the most protein for your money, the ₹20 pack (60 g, about 15.6 g of protein) is the better deal.</p>"),
    ("Is it fried?",
     "<p>No. The chana, soy nuts and peanuts are dry-roasted. A little oil is used only to make the masala stick.</p>"),
    ("What are the allergens?",
     "<p>DumDana contains <strong>peanuts and soy</strong>. Please skip it if you're allergic to either.</p>"),
    ("Will it help me build muscle or lose weight?",
     "<p>We don't make health claims. DumDana is a namkeen with a lot more protein per rupee than most snacks. How it fits into your diet is up to you and, if you need advice, a qualified nutritionist.</p>"),
    ("How is this different from protein chips?",
     "<p>Protein chips cost around ₹50 for 10 g of protein. DumDana gets its protein from whole roasted chana, soy and peanuts, and its ₹20 pack works out to about ₹12.80 for the same 10 g.</p>"),
    ("When will DumDana launch?",
     "<p>There's no date yet. If the market test shows enough people want it, the next step is a small sample batch and a lab test. Waitlist members hear first, and we'll tell you honestly if we decide not to go ahead.</p>"),
]


ICON = {
 "lab": '<svg viewBox="0 0 24 24" fill="none" stroke="#123F2F" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 3h6M10 3v6L4.5 18.5A1.7 1.7 0 0 0 6 21h12a1.7 1.7 0 0 0 1.5-2.5L14 9V3"/><path d="M7 15h10"/></svg>',
 "claim": '<svg viewBox="0 0 24 24" fill="none" stroke="#123F2F" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l7 3v5c0 4.5-3 8.3-7 10-4-1.7-7-5.5-7-10V6l7-3z"/><path d="M9 12l2 2 4-4"/></svg>',
 "allergen": '<svg viewBox="0 0 24 24" fill="none" stroke="#123F2F" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l9.5 17h-19L12 3z"/><path d="M12 10v4M12 17.5v.01"/></svg>',
 "source": '<svg viewBox="0 0 24 24" fill="none" stroke="#123F2F" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 4h10l4 4v12H5z"/><path d="M15 4v4h4M8 12h8M8 16h6"/></svg>',
}
CHECK = '<svg viewBox="0 0 20 20" fill="none" stroke="#C98A2B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 10.5l4 4 8-9"/></svg>'


def home():
    faq_html = "".join(f"<details><summary>{q}</summary><div>{a}</div></details>" for q, a in FAQ)
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    site_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": "DumDana", "url": SITE + "/"}
    compare = [
        # name, sub, price, protein, cost per 10 g, ready to eat, ours
        ("DumDana ₹20 pack", "Target values", "₹20 for 60 g", "15.6 g", "₹12.80", "Yes", True),
        ("DumDana ₹10 pack", "Target values", "₹10 for 25 g", "6.5 g", "₹15.40", "Yes", True),
        ("Protein chips", f'<a href="{SOURCES[1][1]}" target="_blank" rel="noopener">SuperYou</a>', "₹50 for 40 g", "10 g", "₹50.00", "Yes", False),
        ("Chana sattu", f'<a href="{SOURCES[2][1]}" target="_blank" rel="noopener">ITC, eastern India</a>', "₹10 pack", "10 g", "₹10.00", "No, mix or cook it", False),
        ("Loose roasted chana", f'<a href="{SOURCES[7][1]}" target="_blank" rel="noopener">Wholesale, ₹80–120/kg</a>', "Sold by weight", "22.5 g per 100 g", "₹3.60–5.30", "Yes, unpacked and plain", False),
    ]
    rows = "".join(
        f'<tr class="{"ours" if ours else ""}"><th scope="row">{n}<small>{s}</small></th>'
        f'<td data-label="Price">{p}</td><td data-label="Protein">{pr}</td>'
        f'<td data-label="Cost of 10 g protein" class="cost">{c}</td><td data-label="Ready to eat">{r}</td></tr>'
        for n, s, p, pr, c, r, ours in compare)
    flavours = [
        ("Classic masala", "#A9692F", "Chaat masala, black salt and a little red chilli. The canteen classic."),
        ("Pudina", "#4E7D5B", "Dried mint and amchur. Cool and tangy."),
        ("Nimbu-mirchi", "#B8A23A", "Lemon and green chilli. Sharp, with a kick."),
        ("Peri-peri", "#B4442C", "Smoky chilli and garlic. The bold one."),
    ]
    flav_html = "".join(
        f'<li><span class="fdot" style="background:{c}"></span><h3>{n}</h3><p>{d}</p>'
        f'<a href="#join" class="vote" data-flavour="{n}" data-track="flavour_click" data-where="{n}">Vote for {n}</a></li>'
        for n, c, d in flavours)
    steps = [
        ("Done", "Research", "Market data, search trends and the recipe maths. 86% want protein snacks, but only 32% will pay extra."),
        ("Now", "Market test", "This website, a 2-minute survey and the waitlist. We're measuring real interest at ₹10 and ₹20."),
        ("Next", "Samples and lab test", "A small batch of the most-voted flavour, with the protein values tested by an accredited lab."),
        ("Then", "Launch decision", "We launch only if enough people want it at this price. Either way, the waitlist hears first."),
    ]
    step_html = "".join(
        f'<li class="{"now" if st == "Now" else ("done" if st == "Done" else "")}"><span class="st">{st}</span><h3>{t}</h3><p>{d}</p></li>'
        for st, t, d in steps)

    return head(
        "DumDana | High-protein namkeen for ₹10, made from roasted chana, soy and peanuts",
        "DumDana is a dry-roasted high-protein namkeen: about 6.5 g protein in a ₹10 pack and 15.6 g in a ₹20 pack. Join the waitlist and help us test the idea.",
        "/", [site_ld, faq_ld]) + f'''
<body>
{header()}
<main id="main">
<section class="hero" id="top" aria-labelledby="hero-h">
  <div class="wrap">
    <div>
      <h1 id="hero-h">High-protein namkeen for ₹10.</h1>
      <p class="lede">Dry-roasted chana, soy nuts and peanuts with masala. About 6.5 g of protein in a ₹10 pack and 15.6 g in a ₹20 pack, from whole ingredients, not protein powder.</p>
      <form class="hero-form" data-waitlist data-where="hero" novalidate>
        <label class="sr-only" for="h-email">Email address</label>
        <input id="h-email" name="EMAIL" type="email" autocomplete="email" placeholder="Your email address" required>
        <button class="btn btn-primary" type="submit">Get early access</button>
        <p class="form-msg" role="status" aria-live="polite"></p>
      </form>
      <p class="hero-note">Free to join. One email when samples are ready. Prefer to just give feedback? <a data-link="surveyUrl" data-where="hero" href="#" target="_blank" rel="noopener">Take the 2-minute survey</a>.</p>
      <ul class="proof" aria-label="Key facts">
        <li><b>26 g</b>protein per 100 g of the mix (target)</li>
        <li><b>Not fried</b>dry-roasted, a little oil for the masala</li>
        <li><b>₹12.80</b>for 10 g of protein in the ₹20 pack</li>
      </ul>
    </div>
    <figure class="stage">
      <div class="packs">
        <div class="p10">{pack("10", "h10")}</div>
        <div class="p20">{pack("20", "h20")}</div>
      </div>
      <figcaption>Pack design for the market test. Nutrition values are targets, pending a lab test.</figcaption>
    </figure>
  </div>
</section>

<section class="section problem" id="why" aria-labelledby="why-h">
  <div class="wrap">
    <div class="section-head">
      <h2 id="why-h">People want protein. They don't want to pay ₹50 for it.</h2>
      <p>We started with the price a student can pay every day, then designed the recipe to fit it.</p>
    </div>
    <div class="stats">
      <div class="stat"><span class="num">86%</span><p>of Indians say they prioritise protein-rich snacks.</p><a class="src" href="{SOURCES[0][1]}" target="_blank" rel="noopener">Farmley Snacking Report 2026</a></div>
      <div class="stat"><span class="num">32%</span><p>are willing to pay a premium for them.</p><a class="src" href="{SOURCES[0][1]}" target="_blank" rel="noopener">Same survey, 6,000+ people</a></div>
      <div class="stat"><span class="num">₹50</span><p>for 10 g of protein in today's protein chips.</p><a class="src" href="{SOURCES[1][1]}" target="_blank" rel="noopener">SuperYou launch pricing</a></div>
    </div>
  </div>
</section>

<section class="section compare" id="price" aria-labelledby="price-h">
  <div class="wrap">
    <div class="section-head">
      <h2 id="price-h">What 10 g of protein costs you</h2>
      <p>The honest comparison, including the options cheaper than us. Of these, DumDana is the cheapest protein that comes ready to eat in a sealed, flavoured pack.</p>
    </div>
    <div class="table-wrap">
      <table class="cmp">
        <thead><tr><th scope="col">Option</th><th scope="col">Price</th><th scope="col">Protein</th><th scope="col">Cost of 10 g protein</th><th scope="col">Ready to eat</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>

    <div class="calc" aria-labelledby="calc-h">
      <div class="calc-in">
        <h3 id="calc-h">See what you'd save</h3>
        <label for="calc-n">Protein snacks you eat in a week: <output id="calc-n-out" for="calc-n">5</output></label>
        <input id="calc-n" type="range" min="1" max="14" step="1" value="5">
        <div class="calc-scale" aria-hidden="true"><span>1</span><span>7</span><span>14</span></div>
      </div>
      <dl class="calc-out">
        <div><dt>Protein chips, per month</dt><dd id="calc-chips">₹1,070</dd></div>
        <div><dt>Same protein from DumDana</dt><dd id="calc-dd">₹270</dd></div>
        <div class="save"><dt>You'd save every month</dt><dd id="calc-save">₹800</dd></div>
      </dl>
      <p class="calc-note">Assumes each snack gives 10 g of protein: ₹50 a pack for protein chips, or DumDana's ₹20 pack at its target of 15.6 g. Rounded to the nearest ₹10.</p>
    </div>
  </div>
</section>

<section class="section inside" id="inside" aria-labelledby="inside-h">
  <div class="wrap grid">
    <div>
      <h2 id="inside-h">Four ingredients. Nothing hidden.</h2>
      <p>All the protein comes from the chana, soy and peanuts themselves. Here's the full recipe by weight, and the maths behind the number on the pack.</p>
      <div class="mix">
        <div class="mix-bar" role="img" aria-label="Recipe by weight: 50% roasted chana, 25% soy nuts, 20% peanuts, 5% masala, salt and oil"><span class="c"></span><span class="s"></span><span class="p"></span><span class="m"></span></div>
        <ul class="mix-key">
          <li><span class="sw" style="background:#A9692F"></span><span class="pc">50%</span><span><b>Roasted chana</b><small>22.5 g protein per 100 g</small></span></li>
          <li><span class="sw" style="background:#E2BC77"></span><span class="pc">25%</span><span><b>Dry-roasted soy nuts</b><small>About 38.5 g protein per 100 g</small></span></li>
          <li><span class="sw" style="background:#9C5530"></span><span class="pc">20%</span><span><b>Roasted peanuts</b><small>About 26 g protein per 100 g</small></span></li>
          <li><span class="sw" style="background:#123F2F"></span><span class="pc">5%</span><span><b>Masala, salt and a little oil</b><small>Flavour only, counted as zero protein</small></span></li>
        </ul>
      </div>
      <p class="math">(0.50 × 22.5) + (0.25 × 38.5) + (0.20 × 26) ≈ <strong>26 g protein per 100 g</strong></p>
    </div>
    <div class="label" role="group" aria-labelledby="label-h">
      <h3 id="label-h">Nutrition information</h3>
      <p class="tag">Target values from standard nutrition data. Pending lab test.</p>
      <table>
        <thead><tr><th scope="col"></th><th scope="col">Per 100 g</th><th scope="col">₹10 pack<br>25 g</th><th scope="col">₹20 pack<br>60 g</th></tr></thead>
        <tbody>
          <tr class="key"><td>Protein</td><td>26 g</td><td>6.5 g</td><td>15.6 g</td></tr>
          <tr><td>Energy</td><td>445 kcal</td><td>111 kcal</td><td>267 kcal</td></tr>
          <tr><td>Fat</td><td>21 g</td><td>5.3 g</td><td>12.6 g</td></tr>
        </tbody>
      </table>
      <p class="small">About 23% of the calories come from protein.</p>
      <p class="allergen">Contains peanut and soy.</p>
      <p class="small">At about 26 g of protein per 100 g, the mix is more than twice the 12 g per 100 g usually cited for a "high protein" claim on solid food under FSSAI rules. We'll print the claim only after a lab confirms it.</p>
    </div>
  </div>
</section>

<section class="section standards" id="standards" aria-labelledby="std-h">
  <div class="wrap">
    <div class="section-head">
      <h2 id="std-h">Our standards</h2>
      <p>Protein snacks are full of big claims. These are the rules we hold ourselves to while we test DumDana.</p>
    </div>
    <ul class="standards-grid">
      <li><span class="ico">{ICON["lab"]}</span><div><h3>Lab-tested before launch</h3><p>Every number on this site is calculated from published nutrition data. Nothing goes on a real pack until an accredited lab confirms it.</p></div></li>
      <li><span class="ico">{ICON["claim"]}</span><div><h3>No health claims</h3><p>We don't say DumDana builds muscle, burns fat or boosts immunity. It's a namkeen with more protein per rupee, and we say exactly how much.</p></div></li>
      <li><span class="ico">{ICON["allergen"]}</span><div><h3>Allergens up front</h3><p>DumDana contains peanut and soy. We say so on the pack, on this page and in every post.</p></div></li>
      <li><span class="ico">{ICON["source"]}</span><div><h3>Sources you can check</h3><p>Every statistic links to where it came from. The full list is at the bottom of this page.</p></div></li>
    </ul>
  </div>
</section>

<section class="section flavours" id="flavours" aria-labelledby="flav-h">
  <div class="wrap">
    <div class="section-head">
      <h2 id="flav-h">Pick the first flavour</h2>
      <p>We'll make samples of the flavour with the most votes. Choose one and it's pre-selected in the waitlist form.</p>
    </div>
    <ul class="flav-list">{flav_html}</ul>
  </div>
</section>

<section class="section roadmap" id="roadmap" aria-labelledby="road-h">
  <div class="wrap">
    <div class="section-head">
      <h2 id="road-h">Where we are</h2>
      <p>DumDana is a market test run by a college team. Here's the plan, and what happens to your signup.</p>
    </div>
    <ol class="steps">{step_html}</ol>
  </div>
</section>

<section class="section join" id="join" aria-labelledby="join-h">
  <div class="wrap grid">
    <div class="intro">
      <h2 id="join-h">Be first to try DumDana</h2>
      <p>Join the waitlist and pick the flavour you'd try first. It takes 20 seconds.</p>
      <ul class="checks">
        <li>{CHECK}<span>An email when the first samples are ready</span></li>
        <li>{CHECK}<span>Your vote on the first flavour counts toward the sample batch</span></li>
        <li>{CHECK}<span>An honest update if we decide not to make it</span></li>
      </ul>
      <div class="survey">
        <h3>Have 2 more minutes?</h3>
        <p>Tell us what you snack on and what you'd pay. Every answer shapes the recipe and the price.</p>
        <a class="btn btn-light" data-link="surveyUrl" data-where="join" href="#" target="_blank" rel="noopener">Take the survey</a>
      </div>
    </div>
    <form class="form" id="waitlist" data-waitlist data-where="join-form" novalidate>
      <h3>Join the waitlist</h3>
      <div class="field">
        <label for="f-name">Your name</label>
        <input id="f-name" name="FNAME" type="text" autocomplete="given-name">
      </div>
      <div class="field">
        <label for="f-email">Email</label>
        <input id="f-email" name="EMAIL" type="email" autocomplete="email" required>
      </div>
      <div class="field">
        <label for="f-city">City <span class="opt">(optional)</span></label>
        <input id="f-city" name="CITY" type="text" autocomplete="address-level2">
      </div>
      <fieldset class="field">
        <legend>Which flavour would you try first?</legend>
        <div class="chips">
          <label><input type="radio" name="FLAVOUR" value="Classic masala" checked><span>Classic masala</span></label>
          <label><input type="radio" name="FLAVOUR" value="Pudina"><span>Pudina</span></label>
          <label><input type="radio" name="FLAVOUR" value="Nimbu-mirchi"><span>Nimbu-mirchi</span></label>
          <label><input type="radio" name="FLAVOUR" value="Peri-peri"><span>Peri-peri</span></label>
        </div>
      </fieldset>
      <button class="btn btn-primary" type="submit">Join the waitlist</button>
      <p class="form-msg" role="status" aria-live="polite"></p>
      <p class="small">We'll only email you about DumDana. Unsubscribe in one click. Read our <a href="/privacy/">privacy note</a>.</p>
    </form>
  </div>
</section>

<section class="section faq" id="faq" aria-labelledby="faq-h">
  <div class="wrap grid">
    <div>
      <h2 id="faq-h">Questions</h2>
      <p class="muted">Want the numbers for plain roasted chana? <a href="/blog/protein-in-roasted-chana/">Read our breakdown</a>.</p>
    </div>
    <div>{faq_html}</div>
  </div>
</section>
</main>
<div class="mcta" id="mcta" hidden>
  <span><b>₹10 protein namkeen</b>Not on sale yet</span>
  <a class="btn btn-primary" href="#join" data-track="cta_click" data-where="mobile-bar">Join waitlist</a>
</div>
''' + footer()


def blog_post():
    path = "/blog/protein-in-roasted-chana/"
    title = "How much protein is in roasted chana? (Per 100 g, per handful, per rupee)"
    desc = "Roasted chana has about 22.5 g of protein per 100 g. Here's what that means per handful, how it compares with peanuts and soy nuts, and what 10 g of protein costs."
    art_ld = {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc,
              "datePublished": "2026-10-25", "dateModified": "2026-10-25",
              "author": {"@type": "Organization", "name": "DumDana"},
              "publisher": {"@type": "Organization", "name": "DumDana", "logo": {"@type": "ImageObject", "url": SITE + "/assets/dumdana-mark-512.png"}},
              "mainEntityOfPage": SITE + path, "image": SITE + "/assets/og-image.png"}
    qa = [("How much protein is in 100 g of roasted chana?", "About 22.5 g, according to Indian food composition data for roasted Bengal gram."),
          ("How much protein is in a handful of roasted chana?", "A 30 g handful has about 6.7 g of protein. A 50 g bowl has about 11 g."),
          ("Which has more protein: roasted chana, peanuts or soy nuts?", "Soy nuts have the most (about 38.5 g per 100 g), then peanuts (about 26 g), then roasted chana (22.5 g). Chana has much less fat than peanuts.")]
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}
    return head(title, desc, path, [art_ld, faq_ld], "article") + f'''
<body class="page">
{header(False)}
<main id="main" class="article">
<div class="wrap">
  <p class="meta"><a href="/blog/">Blog</a> / Nutrition</p>
  <h1>How much protein is in roasted chana?</h1>
  <p class="meta">Published 25 October 2026 by the DumDana team. 5 minute read.</p>

  <p class="answer"><strong>Roasted chana has about 22.5 g of protein per 100 g.</strong> A 30 g handful gives you roughly 6.7 g of protein, for about ₹3 at wholesale prices. That makes it one of the cheapest ready-to-eat protein sources in India.</p>

  <h2>Protein in roasted chana, by portion</h2>
  <p>The figures below use 22.5 g of protein per 100 g, from Indian food composition data for roasted Bengal gram (the small, dark desi chana sold roasted in most markets).</p>
  <div class="table-scroll"><table>
    <thead><tr><th>Portion</th><th class="n">Weight</th><th class="n">Protein</th></tr></thead>
    <tbody>
      <tr><td>A small handful</td><td class="n">30 g</td><td class="n">6.7 g</td></tr>
      <tr><td>A katori (small bowl)</td><td class="n">50 g</td><td class="n">11.3 g</td></tr>
      <tr><td>100 g</td><td class="n">100 g</td><td class="n">22.5 g</td></tr>
    </tbody>
  </table></div>
  <p>Handful sizes vary, so weigh it once if you're tracking protein closely.</p>

  <h2>Roasted chana vs peanuts vs soy nuts</h2>
  <p>All three are roasted, cheap and sold loose at most kirana shops. Here's how they compare on protein:</p>
  <div class="table-scroll"><table>
    <thead><tr><th>Snack</th><th class="n">Protein per 100 g</th><th>Good to know</th></tr></thead>
    <tbody>
      <tr><td>Dry-roasted soy nuts</td><td class="n">≈38.5 g</td><td>The most protein of the three. USDA lists roasted soy at about 35–43 g; we use the middle value.</td></tr>
      <tr><td>Roasted peanuts</td><td class="n">≈26 g</td><td>Tasty and filling, but much higher in fat.</td></tr>
      <tr><td>Roasted chana</td><td class="n">22.5 g</td><td>Low in fat, very cheap, and the crunchiest base.</td></tr>
    </tbody>
  </table></div>
  <p>Mixing them works well. Our DumDana recipe (50% chana, 25% soy nuts, 20% peanuts, 5% masala) comes out at about 26 g of protein per 100 g: more than chana alone, with less fat than peanuts alone.</p>

  <h2>What 10 g of protein costs</h2>
  <p>Roasted chana sells wholesale for roughly ₹80–120 per kg (IndiaMART listings, October 2026). At those prices, 10 g of protein from roasted chana costs about ₹3.60–5.30 before any packaging or shop margin. Compare that with packaged protein snacks:</p>
  <ul>
    <li><strong>Protein chips:</strong> about ₹50 for 10 g of protein (SuperYou, ₹50 for a 40 g pack).</li>
    <li><strong>DumDana ₹20 pack (target):</strong> about ₹13 for 10 g of protein, packed and sold at a shop.</li>
    <li><strong>Loose roasted chana:</strong> about ₹4–5 for 10 g of protein, if you buy it loose and portion it yourself.</li>
  </ul>
  <p>Loose chana is the cheapest option of all. A pack makes sense when you want it portioned, flavoured and sold next to the chai.</p>

  <h2>Can you call roasted chana "high protein"?</h2>
  <p>Under the FSSAI (Advertising and Claims) Regulations, 2018, a solid food needs at least 20% of the protein RDA per 100 g to be called "high in protein". Compliance guides translate that to roughly 12 g of protein per 100 g. Roasted chana, at 22.5 g, clears it easily. Packaged brands still need an accredited lab report before printing the claim.</p>

  <h2>Quick answers</h2>
  {"".join(f"<h3>{q}</h3><p>{a}</p>" for q, a in qa)}

  <div class="cta-box">
    <h2>We're turning this into a ₹10 snack</h2>
    <p>DumDana is a roasted chana, soy and peanut namkeen with about 6.5 g of protein in a ₹10 pack. It's not on sale yet. Join the waitlist to help us decide whether to make it.</p>
    <a class="btn btn-light" href="/#join" data-track="cta_click" data-where="blog">Join the waitlist</a>
  </div>

  <h2>Sources</h2>
  <ol>
    <li><a href="{SOURCES[4][1]}" target="_blank" rel="noopener">{SOURCES[4][0]}</a></li>
    <li><a href="{SOURCES[5][1]}" target="_blank" rel="noopener">{SOURCES[5][0]}</a></li>
    <li><a href="{SOURCES[6][1]}" target="_blank" rel="noopener">{SOURCES[6][0]}</a></li>
    <li><a href="{SOURCES[7][1]}" target="_blank" rel="noopener">{SOURCES[7][0]}</a></li>
    <li><a href="{SOURCES[1][1]}" target="_blank" rel="noopener">{SOURCES[1][0]}</a></li>
    <li><a href="{SOURCES[8][1]}" target="_blank" rel="noopener">{SOURCES[8][0]}</a></li>
    <li><a href="{SOURCES[9][1]}" target="_blank" rel="noopener">{SOURCES[9][0]}</a></li>
  </ol>
  <p class="meta">This article is general information, not dietary advice.</p>
</div>
</main>
''' + footer()


def blog_index():
    return head("DumDana blog: affordable protein, explained", "Plain answers about cheap, everyday protein in India, from the team behind DumDana.", "/blog/") + f'''
<body class="page">
{header(False)}
<main id="main" class="article">
<div class="wrap">
  <h1>The DumDana blog</h1>
  <p>Plain answers about getting protein in India without spending ₹50 a snack.</p>
  <ul class="post-list">
    <li><a href="/blog/protein-in-roasted-chana/">How much protein is in roasted chana?</a><p>Per 100 g, per handful and per rupee, compared with peanuts and soy nuts.</p></li>
  </ul>
</div>
</main>
''' + footer()


def privacy():
    return head("Privacy note | DumDana", "How DumDana handles waitlist emails and website analytics.", "/privacy/") + f'''
<body class="page">
{header(False)}
<main id="main" class="article">
<div class="wrap">
  <h1>Privacy note</h1>
  <p class="meta">Last updated 25 October 2026</p>
  <h2>What we collect</h2>
  <ul>
    <li><strong>Waitlist:</strong> the name, email, city and flavour choice you type into the form, plus which link brought you to the site. These are stored in Mailchimp.</li>
    <li><strong>Survey:</strong> answers you give in our Google Form, stored in Google Forms.</li>
    <li><strong>Website analytics:</strong> Google Analytics and Microsoft Clarity record anonymous visits, clicks and scrolling so we can see which parts of the page work.</li>
  </ul>
  <h2>What we do with it</h2>
  <p>We use it only to run this market test: to email waitlist members about DumDana and to report results for a college project. We don't sell or share your details.</p>
  <h2>Your choices</h2>
  <p>Every email has an unsubscribe link. To have your details deleted, reply to any of our emails or message us on Instagram at <a href="{CONFIG["instagram"]}" target="_blank" rel="noopener">@eatdumdana</a>.</p>
</div>
</main>
''' + footer()


def not_found():
    return head("Page not found | DumDana", "This page doesn't exist.", "/404") + f'''
<body class="page">
{header(False)}
<main id="main" class="article">
<div class="wrap">
  <h1>This page isn't here</h1>
  <p>The link may be old or mistyped. Go back to the <a href="/">DumDana home page</a> or read <a href="/blog/protein-in-roasted-chana/">how much protein is in roasted chana</a>.</p>
</div>
</main>
''' + footer()


def write(rel, content):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    write("index.html", home())
    write("blog/index.html", blog_index())
    write("blog/protein-in-roasted-chana/index.html", blog_post())
    write("privacy/index.html", privacy())
    write("404.html", not_found())
    for f in ("styles.css", "main.js", "README.md"):
        shutil.copy(os.path.join(ROOT, "site_src", f), os.path.join(OUT, f))
    pub = {k: CONFIG[k] for k in ("mailchimpAction", "surveyUrl", "instagram", "youtube")}
    write("config.js", "window.DD_CONFIG = " + json.dumps(pub, indent=2) + ";\n")
    write("favicon.svg", mark())
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    urls = ["/", "/blog/", "/blog/protein-in-roasted-chana/", "/privacy/"]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>2026-10-25</lastmod></url>\n" for u in urls) + "</urlset>\n")
    write("site.webmanifest", json.dumps({"name": "DumDana", "short_name": "DumDana", "icons": [
        {"src": "/assets/dumdana-mark-512.png", "sizes": "512x512", "type": "image/png"}],
        "theme_color": FOREST, "background_color": "#ffffff", "display": "browser"}, indent=2))
    write("vercel.json", json.dumps({"cleanUrls": True, "trailingSlash": True}, indent=2))
    assets = os.path.join(ROOT, "brand", "export")
    if os.path.isdir(assets):
        for f in os.listdir(assets):
            if f.startswith(("favicon", "apple", "dumdana-mark-512", "og-image")):
                os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
                shutil.copy(os.path.join(assets, f), os.path.join(OUT, "assets", f))
    print("built", OUT)


if __name__ == "__main__":
    main()
