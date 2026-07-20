# SAIDIO Operations Desk

Static GitHub Pages dashboard for daily music briefs, production progress and SeanRadar signals.

## Local preview

Open `index.html`, or use any static file server. No build step is required.

## Daily automation setup

Create repository secrets before enabling `.github/workflows/daily-brief.yml`:

- `GEMINI_API_KEY`: Gemini API key used to generate the brief and prompt variants.
- `DISCORD_WEBHOOK_URL`: Discord incoming webhook. Never place it in a tracked file.

The workflow updates `data/dashboard.json`, commits the day’s archive and POSTs the same formatted message to Discord. GitHub Pages deploys when `main` changes.

## Data contract

`data/dashboard.json` is the public source used by the website. Do not include private keys, webhook URLs, client data or unpublished performance data in it.
