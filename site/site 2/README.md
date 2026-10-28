# DumDana website (v4)

Plain HTML, CSS and JavaScript. No build step needed: upload the files and Vercel serves them.

## The only file you need to edit: config.js
Paste each code between the quotes, save, commit:
- `ga4Id` – Google Analytics 4 Measurement ID (starts with G-)
- `clarityId` – Microsoft Clarity project ID
- `mailchimpAction` – Mailchimp embedded form URL (already filled in)
- `surveyUrl` – Google Form link (forms.gle/...)
- `instagram`, `youtube` – profile links

## Pages
- `/` – landing page (hero signup, pack picker, comparison, savings calculator, recipe, standards, flavour vote, roadmap, waitlist, FAQ)
- `/blog/high-protein-snacks-india/` – SEO article: high-protein snacks in India compared by price
- `/blog/protein-in-roasted-chana/` – SEO article: protein in roasted chana
- `/blog/`, `/privacy/`, `404.html`

## Analytics events (GA4 + Clarity)
generate_lead, waitlist_form_start, waitlist_fallback, survey_click, cta_click, pack_pick,
compare_sort, flavour_click, calculator_used, social_click, scroll_depth

## Search Console
Use the "HTML file" verification method: download Google's file and upload it into this folder.
