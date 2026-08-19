# Setup Guide

How to run your own instance of `tech-brief` and get a daily digest emailed to you.

Total time: about 15 minutes. Total cost: about 30 cents a month in Claude tokens, everything else free tier.

---

## Prerequisites

- Python 3.11 or newer
- An Anthropic API key with a monthly cap (I set mine to $2)
- A Resend account (free tier gives you 100 emails a day)
- A GitHub account if you want the daily cron to run in Actions

---

## 1. Clone and install

```bash
git clone https://github.com/SammyBolger/tech-brief.git
cd tech-brief

python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 2. Get an Anthropic API key

1. Sign up at https://console.anthropic.com
2. Add a payment method
3. Set a monthly usage limit at https://console.anthropic.com/settings/billing. Recommend $2. If you hit the cap the API pauses and you stop getting digests until next month.
4. Create an API key: **Settings > API Keys > Create Key**. Save it.

## 3. Get a Resend key

1. Sign up at https://resend.com
2. Verify a sending domain (or use the default `onboarding@resend.dev` for testing)
3. Create an API key: **API Keys > Create API Key**. Save it.

If you want to send from a custom domain like `brief@sammybolger.com`, follow Resend's DNS setup. If you just want it to work today, use their test sending address.

## 4. Fill in your `.env`

```bash
cp .env.example .env
```

Edit `.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
RESEND_API_KEY=re_...
DIGEST_FROM_EMAIL=onboarding@resend.dev
DIGEST_TO_EMAIL=you@example.com
```

## 5. Run it locally

```bash
make all
```

That runs ingest, transform, and digest in order. In about a minute you should see a Resend send log line and an email land in your inbox.

If the email does not arrive within 2 minutes, check the Resend dashboard for a bounce or a delivery log.

## 6. Optional: run it on GitHub Actions every morning

Fork the repo (or use your own copy). Then:

1. Go to **Settings > Secrets and variables > Actions > New repository secret** and add:
   - `ANTHROPIC_API_KEY`
   - `RESEND_API_KEY`
   - `DIGEST_FROM_EMAIL`
   - `DIGEST_TO_EMAIL`
2. That is it. `.github/workflows/daily.yml` is already scheduled for 06:55 CT (11:55 UTC) and will run itself.

The workflow commits each day's brief JSON back to `data/briefs/YYYY-MM-DD.json` so you have a permanent archive.

---

## Troubleshooting

**No email arrives.**
Check `make all` output for errors. Then check the Resend dashboard for a delivery attempt.

**`ANTHROPIC_API_KEY is not set`.**
You forgot to `cp .env.example .env` or the key line is empty.

**Reddit ingestion returns nothing.**
Reddit rate-limits the public JSON API. Wait a few minutes and re-run. If it keeps happening, add a longer sleep in `src/tech_brief/sources/reddit.py`.

**dbt fails with `Compilation Error`.**
Delete `data/tech_brief.duckdb` and re-run `make all`. The schema probably changed since your last run.

---

## Cost summary

- Anthropic (daily digest, ~5k in / 2k out per run): **~$0.30 per month**
- Resend: **$0** (100 emails per day on free tier)
- GitHub Actions: **$0** (unlimited minutes on public repos)
- **Total: ~$0.30 per month**
