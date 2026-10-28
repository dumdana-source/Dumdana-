/* Vercel serverless function: adds a waitlist signup to Mailchimp from the server
   (so visitors never see a captcha), then sends a welcome email straight away from Gmail.

   Environment variables (Vercel → Project → Settings → Environment Variables):
     MAILCHIMP_API_KEY      required, e.g. abc123...-us4  (Mailchimp → Profile → Extras → API keys)
     GMAIL_USER             the Gmail address the welcome email is sent from
     GMAIL_APP_PASSWORD     a 16-letter Google "app password" for that Gmail (not the normal password)
   Optional:
     MAILCHIMP_AUDIENCE_ID   defaults to the DumDana audience below
     MAILCHIMP_DOUBLE_OPTIN  "false" (default: added as Subscribed at once) or "true" (Mailchimp sends a confirm link)
     SITE_URL                defaults to https://dumdana-site.vercel.app
*/
const crypto = require("crypto");

const DEFAULT_AUDIENCE = "5a0a2ba3ee";
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

function clean(v, max) {
  return String(v == null ? "" : v).replace(/[\u0000-\u001f<>]/g, "").trim().slice(0, max);
}

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
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

function welcomeEmail(name, flavour, site) {
  const hi = name ? "Hi " + esc(name) + "," : "Hi,";
  const flav = flavour
    ? "<p style=\"margin:0 0 16px\">You voted for <strong>" + esc(flavour) + "</strong> as your first flavour. Thank you, we're counting every vote.</p>"
    : "<p style=\"margin:0 0 16px\">One quick ask: which flavour should we make first? Just reply to this email with <strong>Classic masala</strong>, <strong>Pudina</strong>, <strong>Nimbu-mirchi</strong> or <strong>Peri-peri</strong>.</p>";
  const html =
    "<div style=\"background:#EEF3EF;padding:32px 16px;font-family:Arial,Helvetica,sans-serif\">" +
    "<div style=\"max-width:520px;margin:0 auto;background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #D9E1DC\">" +
    "<div style=\"background:#123F2F;color:#ffffff;padding:22px 28px;font-size:22px;font-weight:bold;letter-spacing:-.01em\">DumDana</div>" +
    "<div style=\"padding:28px;color:#33443B;font-size:15px;line-height:1.6\">" +
    "<p style=\"margin:0 0 16px;color:#10241B;font-size:20px;font-weight:bold;line-height:1.3\">You're on the DumDana waitlist.</p>" +
    "<p style=\"margin:0 0 16px\">" + hi + "</p>" +
    "<p style=\"margin:0 0 16px\">Thanks for joining. DumDana is a high-protein namkeen made from chana, soy nuts and peanuts, dry-roasted and never fried. It will come in ₹20 and ₹30 packs.</p>" +
    "<p style=\"margin:0 0 16px\">We're in the market-testing stage, so nothing is on sale yet. Your opinion decides what we make first.</p>" +
    flav +
    "<p style=\"margin:24px 0\"><a href=\"" + site + "/?utm_source=mailchimp&utm_medium=email&utm_campaign=welcome\" style=\"background:#123F2F;color:#ffffff;text-decoration:none;padding:12px 20px;border-radius:8px;font-weight:bold;display:inline-block\">Visit DumDana</a></p>" +
    "<p style=\"margin:0\">Har din ka protein.<br>Team DumDana</p>" +
    "</div></div>" +
    "<p style=\"max-width:520px;margin:16px auto 0;color:#56645D;font-size:12px;line-height:1.5;text-align:center\">You're getting this because you joined the waitlist on " + site.replace(/^https?:\/\//, "") + ". Reply \"stop\" and we'll remove you.</p>" +
    "</div>";
  const text =
    (name ? "Hi " + name + "," : "Hi,") + "\n\n" +
    "Thanks for joining the DumDana waitlist. DumDana is a high-protein namkeen made from chana, soy nuts and peanuts, dry-roasted and never fried. It will come in Rs 20 and Rs 30 packs.\n\n" +
    "We're in the market-testing stage, so nothing is on sale yet. Your opinion decides what we make first.\n\n" +
    (flavour ? "You voted for " + flavour + " as your first flavour. Thank you.\n\n"
             : "Which flavour should we make first? Reply with Classic masala, Pudina, Nimbu-mirchi or Peri-peri.\n\n") +
    "Visit: " + site + "\n\nHar din ka protein.\nTeam DumDana\n";
  return { html, text };
}

async function sendWelcome(to, name, flavour) {
  const user = process.env.GMAIL_USER;
  const pass = (process.env.GMAIL_APP_PASSWORD || "").replace(/\s+/g, "");
  if (!user || !pass) return "skipped";
  const site = (process.env.SITE_URL || "https://dumdana-site.vercel.app").replace(/\/$/, "");
  const nodemailer = require("nodemailer");
  const t = nodemailer.createTransport({ service: "gmail", auth: { user, pass } });
  const { html, text } = welcomeEmail(name, flavour, site);
  await t.sendMail({
    from: { name: "DumDana", address: user },
    to,
    subject: "You're on the DumDana waitlist",
    text,
    html,
  });
  return "sent";
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
  const doubleOptIn = process.env.MAILCHIMP_DOUBLE_OPTIN === "true";

  let body = req.body;
  if (typeof body === "string") { try { body = JSON.parse(body); } catch (e) { body = {}; } }
  body = body || {};

  // Bots fill the hidden "company" field; real people never see it.
  if (clean(body.company, 100)) return res.status(200).json({ ok: true, status: "subscribed" });

  const email = clean(body.email, 254).toLowerCase();
  if (!EMAIL_RE.test(email)) return res.status(400).json({ ok: false, error: "invalid_email" });

  const merge = {};
  const fname = clean(body.name, 60); if (fname) merge.FNAME = fname;
  const city = clean(body.city, 60); if (city) merge.CITY = city;
  const flavour = clean(body.flavour, 40); if (flavour) merge.FLAVOUR = flavour;
  const source = clean(body.source, 120); if (source) merge.SOURCE = source;

  const hash = crypto.createHash("md5").update(email).digest("hex");
  const url = `https://${server}.api.mailchimp.com/3.0/lists/${audience}/members/${hash}`;

  try {
    // Is this person already on the list? (So we only send the welcome email once.)
    const before = await mc(url, key, "GET");
    const isNew = before.status === 404 || !["subscribed", "pending"].includes(before.data && before.data.status);

    const member = { email_address: email, merge_fields: merge, status_if_new: doubleOptIn ? "pending" : "subscribed" };
    // Someone who unsubscribed earlier and signs up again: put them back on the list.
    if (!doubleOptIn && before.status === 200 && before.data.status === "unsubscribed") member.status = "subscribed";

    let r = await mc(url, key, "PUT", member);
    // If the extra fields (CITY, FLAVOUR, SOURCE) don't exist in Mailchimp yet, save just the name and email.
    if (r.status === 400 && /merge/i.test(JSON.stringify(r.data))) {
      member.merge_fields = fname ? { FNAME: fname } : {};
      r = await mc(url, key, "PUT", member);
    }

    if (r.status >= 200 && r.status < 300) {
      let welcome = "already_member";
      if (isNew && !doubleOptIn) {
        try { welcome = await sendWelcome(email, fname, flavour); }
        catch (e) { welcome = "failed"; console.error("welcome email failed:", e && e.message); }
      }
      return res.status(200).json({ ok: true, status: r.data.status || "subscribed", welcome });
    }

    const detail = String((r.data && (r.data.detail || r.data.title)) || "");
    console.error("mailchimp error", r.status, detail);
    if (/fake|invalid|valid email/i.test(detail)) return res.status(400).json({ ok: false, error: "invalid_email" });
    if (/compliance|unsubscribed|permanently deleted/i.test(detail)) return res.status(409).json({ ok: false, error: "resubscribe" });
    if (r.status === 429 || /too many/i.test(detail)) return res.status(429).json({ ok: false, error: "rate_limited" });
    return res.status(502).json({ ok: false, error: "mailchimp", detail: detail.slice(0, 200) });
  } catch (e) {
    console.error("network error", e && e.message);
    return res.status(502).json({ ok: false, error: "network" });
  }
};
