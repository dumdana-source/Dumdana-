# DumDana website

Static site: plain HTML, CSS and JavaScript. No build step is needed to host it.

## Files
- `index.html` – landing page (hero signup, comparison, savings calculator, ingredients, standards, flavour vote, roadmap, waitlist, FAQ)
- `blog/protein-in-roasted-chana/` – SEO article
- `privacy/`, `404.html` – privacy note and not-found page
- `styles.css` – all styling
- `main.js` – waitlist forms (Mailchimp), calculator, flavour vote, mobile bar, analytics events
- `config.js` – links you can edit yourself (see below)
- `sitemap.xml`, `robots.txt`, `site.webmanifest`, `vercel.json`, `favicon.svg`, `assets/`

## Edit these yourself in config.js
- `mailchimpAction` – the form action URL from Mailchimp's embedded form
- `surveyUrl` – your Google Form link (forms.gle/...)
- `instagram`, `youtube` – profile links

## Analytics events sent to GA4 and Clarity
`generate_lead` (waitlist signup), `waitlist_form_start`, `survey_click`, `cta_click`,
`flavour_click`, `calculator_used`, `social_click`, `scroll_depth`

GA4, Clarity and Search Console codes go in the page `<head>`; send them to Claude to add.
