import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parts2 import *
from pack2 import pack
G, Y = FOREST, AMBER

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.join(HERE, "export") + "/"
TMP = "/tmp/claude-0/"
os.makedirs(E, exist_ok=True); os.makedirs(TMP, exist_ok=True)


def w(n, s): open(E + n, "w").write(s)


w("dumdana-wordmark-green.svg", wordmark(FOREST))
w("dumdana-wordmark-white.svg", wordmark("#FFFFFF"))
w("dumdana-mark.svg", mark())
w("dumdana-mark-circle.svg", mark(shape="circle"))
lock = lockup()
w("dumdana-lockup.svg", lock)
w("dumdana-lockup-white.svg", lockup("#FFFFFF").replace(mark(), mark(bg="#FFFFFF", fg=FOREST)))
FONTCSS = ('<style>body{margin:0}.k-sub{font:500 12.5px Inter}.k-big{font:600 50px "Inter Display";letter-spacing:-.03em}.k-small{font:500 11px Inter}.k-mrp{font:600 13px Inter}.p-sub{font:600 15px "Inter"}.p-pro{font:700 14px "Inter"}'
           '.p-mrp{font:700 8.5px "Inter";letter-spacing:.06em}.p-price{font:800 18px "Inter Display"}.p-wt{font:500 10px "Inter"}</style>')
pages = {
    "dumdana-mark-512": (512, 512, f'<div style="width:512px;height:512px">{mark()}</div>'),
    "favicon-32": (32, 32, f'<div style="width:32px;height:32px">{mark()}</div>'),
    "apple-touch-icon": (180, 180, f'<div style="width:180px;height:180px;background:{FOREST}">{mark().replace(chr(34)+"20"+chr(34), chr(34)+"0"+chr(34))}</div>'),
    "instagram-profile-1080": (1080, 1080, f'<div style="width:1080px;height:1080px;background:{FOREST};display:grid;place-items:center"><div style="width:900px">{mark(shape="circle")}</div></div>'),
    "youtube-profile-800": (800, 800, f'<div style="width:800px;height:800px;background:{FOREST};display:grid;place-items:center"><div style="width:660px">{mark(shape="circle")}</div></div>'),
    "lockup-on-white-2000": (2000, 600, f'<div style="width:2000px;height:600px;background:#fff;display:grid;place-items:center"><div style="width:1400px">{lock}</div></div>'),
    "youtube-banner-2560x1440": (2560, 1440, f'''<div style="width:2560px;height:1440px;background:{SAGE};display:grid;place-items:center">
      <div style="width:1546px;height:423px;display:flex;align-items:center;justify-content:space-between">
        <div><div style="width:620px">{lock}</div><div style="font:600 64px/1.1 'Inter Display';color:{INK};letter-spacing:-.02em;margin-top:40px">High-protein namkeen for ₹10.</div><div style="font:500 30px 'Inter';color:#56645D;margin-top:18px">Roasted chana, soy and peanuts. Market test, 2026.</div></div>
        <div style="display:flex;gap:20px;align-items:flex-end;height:420px"><div style="width:250px">{pack("10","b1")}</div><div style="width:300px">{pack("20","b2")}</div></div>
      </div></div>'''),
    "og-image": (1200, 630, f'''<div style="width:1200px;height:630px;background:#fff;display:grid;grid-template-columns:600px 600px">
      <div style="padding:64px 0 0 64px"><div style="width:250px">{lock}</div>
        <div style="font:600 66px/1.05 'Inter Display';color:{INK};letter-spacing:-.025em;margin-top:56px">High-protein namkeen for ₹10.</div>
        <div style="font:500 26px/1.4 'Inter';color:#56645D;margin-top:24px;width:470px">Dry-roasted chana, soy and peanuts. 6.5 g protein in ₹10, 15.6 g in ₹20.</div></div>
      <div style="background:{SAGE};display:flex;align-items:flex-end;justify-content:center;gap:16px;padding-bottom:60px"><div style="width:220px">{pack("10","o1")}</div><div style="width:270px">{pack("20","o2")}</div></div>
    </div>'''),
}
for n, (W, H, body) in pages.items():
    open(f"{TMP}x_{n}.html", "w").write('<!doctype html><html><head><meta charset="utf-8">' + FONTCSS + "</head><body>" + body + "</body></html>")
open(f"{TMP}x_list.txt", "w").write("\n".join(f"{n} {W} {H}" for n, (W, H, _) in pages.items()))
js = """const { chromium } = require('playwright'); const fs=require('fs');
(async () => { const b = await chromium.launch();
 for (const line of fs.readFileSync('%sx_list.txt','utf8').trim().split('\\n')) { const [n,w,h]=line.split(' ');
  const p = await b.newPage({ viewport: { width:+w, height:+h } }); await p.goto('file://%sx_'+n+'.html');
  await p.screenshot({ path: '%s'+n+'.png', omitBackground: n==='dumdana-mark-512'||n==='favicon-32' }); await p.close(); }
 await b.close(); })();""" % (TMP, TMP, E)
open(TMP + "export.js", "w").write(js)
subprocess.run(["node", TMP + "export.js"], check=True, cwd="/home/claude/build")
print("exported", sorted(os.listdir(E)))
