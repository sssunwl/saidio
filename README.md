# SAIDIO Operations Desk

Static GitHub Pages dashboard and **daily media factory** for three streams — music, voiceover and
Suntravel visuals. One workflow creates the daily briefs, calls Gemini TTS, Lyria and Veo, publishes
the outputs as monthly GitHub Release assets, and exposes generation status and links on the site.

## Streams & schedule

| Workflow | Cron (UTC / JST) | Output |
|---|---|---|
| `daily-production.yml` | 00:12 / 09:12 | All three briefs + one TTS + one Lyria clip + one Veo clip |
| Legacy per-stream workflows | Manual only | Brief generation/recovery without automatic media |

Voice/character consistency is governed by [`VOICES.md`](VOICES.md) — the single source of truth
for every narration voice and drama character. Lock a voice name there once, reuse it forever.

## Local preview

Open `index.html`, or use any static file server. No build step is required.

## Daily automation setup

Create repository secrets before enabling `.github/workflows/daily-production.yml`:

- `GEMINI_API_KEY`: Gemini API key used to generate the brief and prompt variants.
- `DISCORD_WEBHOOK_URL`: Discord incoming webhook. Never place it in a tracked file.
- `SAIDIO_VOICE_MAP_JSON` (optional): voice-code overrides, for example
  `{"V-INVEST":"Charon","V-TRAVEL-F":"Leda"}`.

Set the repository variable `SAIDIO_MEDIA_ENABLED` to `true` only after billing and API access are
ready. Scheduled runs deliberately generate just **one 30-second music clip, one voiceover and one
8-second 720p vertical video per day**. Until that variable is enabled, the combined workflow still
creates all three text briefs without incurring media-generation charges. A manual run can select
`music`, `voiceover`, `video`, or `all`; ready items are skipped and failed items can be rerun.

Generated files are public and are stored in a monthly Release (`media-YYYY-MM`), not in the Git
history. Never use this pipeline for confidential scripts or client assets.

Local validation does not call paid APIs:

```sh
python -m unittest discover -s tests -v
python scripts/generate_media.py --dry-run --stream all --date YYYY-MM-DD
```

The workflow updates all three JSON archives, commits the generation state and posts a compact
summary to Discord. GitHub Pages deploys when `main` changes.

## Data contract

`data/dashboard.json` is the public source used by the website. Do not include private keys, webhook URLs, client data or unpublished performance data in it.
