/* Vercel serverless function: adds a waitlist signup to Mailchimp from the server,
   so visitors never see Mailchimp's captcha.

   Needs ONE environment variable in Vercel (Project → Settings → Environment Variables):
     MAILCHIMP_API_KEY   e.g. abc123...-us4   (Mailchimp → Profile → Extras → API keys)
   Optional:
     MAILCHIMP_AUDIENCE_ID   defaults to the DumDana audience below
     MAILCHIMP_DOUBLE_OPTIN  "true" (default: Mailchimp emails a confirm link) or "false"
*/
const crypto = require("crypto");

const DEFAULT_AUDIENCE = "5a0a2ba3ee";
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

function clean(v, max) {
  return String(v == null ? "" : v).replace(/[\u0000-\u001f<>]/g, "").trim().slice(0, max);
}

async function mc(url, key, method, body) {
  const r = await fetch(url, {
    method,
    headers: {
      Authorization: "Basic " + Buffer.from("dumdana:" + key).toString("base64"),
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  let data = {};
  try { data = await r.json(); } catch (e) { /* empty body */ }
  return { status: r.status, data };
}

module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ ok: false, error: "method" });
  }

  const key = process.env.MAILCHIMP_API_KEY || "";
  const server = (key.split("-")[1] || "").trim();
  if (!key || !server) return res.status(503).json({ ok: false, error: "not_configured" });
  const audience = process.env.MAILCHIMP_AUDIENCE_ID || DEFAULT_AUDIENCE;
  const doubleOptIn = process.env.MAILCHIMP_DOUBLE_OPTIN !== "false";

  let body = req.body;
  if (typeof body === "string") { try { body = JSON.parse(body); } catch (e) { body = {}; } }
  body = body || {};

  // Bots fill the hidden "company" field; real people never see it.
  if (clean(body.company, 100)) return res.status(200).json({ ok: true, status: "pending" });

  const email = clean(body.email, 254).toLowerCase();
  if (!EMAIL_RE.test(email)) return res.status(400).json({ ok: false, error: "invalid_email" });

  const merge = {};
  const fname = clean(body.name, 60); if (fname) merge.FNAME = fname;
  const city = clean(body.city, 60); if (city) merge.CITY = city;
  const flavour = clean(body.flavour, 40); if (flavour) merge.FLAVOUR = flavour;
  const source = clean(body.source, 120); if (source) merge.SOURCE = source;

  const hash = crypto.createHash("md5").update(email).digest("hex");
  const url = `https://${server}.api.mailchimp.com/3.0/lists/${audience}/members/${hash}`;
  const member = { email_address: email, status_if_new: doubleOptIn ? "pending" : "subscribed", merge_fields: merge };

  try {
    let r = await mc(url, key, "PUT", member);
    // If the extra fields (CITY, FLAVOUR, SOURCE) don't exist in Mailchimp yet, save just the name and email.
    if (r.status === 400 && /merge/i.test(JSON.stringify(r.data))) {
      member.merge_fields = fname ? { FNAME: fname } : {};
      r = await mc(url, key, "PUT", member);
    }
    if (r.status >= 200 && r.status < 300) {
      return res.status(200).json({ ok: true, status: r.data.status || "pending" });
    }
    const detail = String((r.data && (r.data.detail || r.data.title)) || "");
    if (/fake|invalid|valid email/i.test(detail)) return res.status(400).json({ ok: false, error: "invalid_email" });
    if (/compliance|unsubscribed|permanently deleted/i.test(detail)) return res.status(409).json({ ok: false, error: "resubscribe" });
    if (r.status === 429 || /too many/i.test(detail)) return res.status(429).json({ ok: false, error: "rate_limited" });
    return res.status(502).json({ ok: false, error: "mailchimp", detail: detail.slice(0, 200) });
  } catch (e) {
    return res.status(502).json({ ok: false, error: "network" });
  }
};
