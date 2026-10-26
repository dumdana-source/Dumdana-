"""Stand-up pouch mockups for DumDana v2."""
import random
from parts2 import wordmark, FOREST, WHITE, AMBER, INK


def kernels(seed, x0=36, x1=204, y0=232, rows=2):
    rnd = random.Random(seed)
    kinds = ["chana"] * 7 + ["soy"] * 5 + ["peanut"] * 4
    rnd.shuffle(kinds)
    out = []
    per = 8
    for i, k in enumerate(kinds):
        cx = x0 + (i % per) * ((x1 - x0) / (per - 1)) + rnd.uniform(-5, 5)
        cy = y0 + (i // per) * 24 + rnd.uniform(-4, 4)
        rot = rnd.uniform(-60, 60)
        if k == "chana":
            out.append(f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.0f})"><path d="M-2,-11 C7,-11 12,-4 12,3 C12,10 6,13 0,13 C-7,13 -12,8 -12,1 C-12,-5 -8,-8 -5,-9 C-5,-11 -4,-12 -2,-11 Z" fill="#A9692F"/><path d="M-3,-7 C0,-2 1,3 -1,8" stroke="#7E4A1F" stroke-width="1.5" fill="none" stroke-linecap="round"/></g>')
        elif k == "soy":
            out.append(f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.0f})"><ellipse rx="10" ry="7.5" fill="#E2BC77"/><path d="M-9,0 H9" stroke="#C49A4C" stroke-width="1.3"/></g>')
        else:
            out.append(f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.0f})"><path d="M-11,0 C-11,-6 -6,-8 0,-8 C6,-8 11,-6 11,0 C11,6 6,8 0,8 C-6,8 -11,6 -11,0 Z" fill="#9C5530"/><path d="M-6,-3 C-2,-5 3,-5 7,-2" stroke="#DDB08A" stroke-width="1.5" fill="none" stroke-linecap="round"/></g>')
    return "".join(out)


BODY = "M18,8 Q18,3 23,3 H217 Q222,3 222,8 L229,290 Q230,312 208,314 H32 Q10,312 11,290 Z"


def pack(variant="10", uid="a"):
    if variant == "10":
        bg, fg, sub, seal, protein, wt, mrp = FOREST, WHITE, "rgba(255,255,255,.78)", "#0C3024", "6.5 g", "25 g", "₹10"
    else:
        bg, fg, sub, seal, protein, wt, mrp = "#FBFAF7", FOREST, "#5B6B63", FOREST, "15.6 g", "60 g", "₹20"
    return f'''<svg viewBox="0 0 240 330" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="DumDana {mrp} pack, {protein} protein">
<defs>
  <clipPath id="body-{uid}"><path d="{BODY}"/></clipPath>
  <clipPath id="win-{uid}"><rect x="30" y="214" width="180" height="58" rx="10"/></clipPath>
  <linearGradient id="shade-{uid}" x1="0" x2="1" y1="0" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity=".16"/><stop offset=".18" stop-color="#fff" stop-opacity="0"/>
    <stop offset=".8" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".16"/>
  </linearGradient>
</defs>
<ellipse cx="120" cy="318" rx="104" ry="8" fill="#000" opacity=".12"/>
<g clip-path="url(#body-{uid})">
  <path d="{BODY}" fill="{bg}"/>
  <rect x="0" y="0" width="240" height="26" fill="{seal}"/>
  <g stroke="#000" stroke-opacity=".10">{"".join(f'<line x1="{x}" y1="5" x2="{x}" y2="22"/>' for x in range(22, 222, 5))}</g>
  <line x1="18" y1="34" x2="222" y2="34" stroke="{fg}" stroke-opacity=".18" stroke-dasharray="3 3"/>
  <g transform="translate(32,48) scale(.22)">{wordmark(fg).split('>', 1)[1].rsplit('</svg>', 1)[0]}</g>
  <text x="32" y="90" class="k-sub" fill="{sub}">Roasted protein namkeen</text>
  <text x="30" y="150" class="k-big" fill="{fg}">{protein}</text>
  <text x="32" y="171" class="k-sub" fill="{sub}">protein per pack</text>
  <line x1="32" y1="186" x2="208" y2="186" stroke="{fg}" stroke-opacity=".22"/>
  <text x="32" y="204" class="k-small" fill="{sub}">Chana, soy nuts, peanuts</text>
  <rect x="30" y="214" width="180" height="58" rx="10" fill="#F5EBD9" stroke="{fg}" stroke-opacity=".25"/>
  <g clip-path="url(#win-{uid})">{kernels(3 if variant == "10" else 11)}</g>
  <text x="32" y="296" class="k-small" fill="{sub}">Net wt. {wt}</text>
  <text x="208" y="296" text-anchor="end" class="k-mrp" fill="{fg}">MRP {mrp}</text>
  <rect x="0" y="0" width="240" height="330" fill="url(#shade-{uid})"/>
</g>
</svg>'''
