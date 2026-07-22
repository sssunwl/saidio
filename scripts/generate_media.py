#!/usr/bin/env python3
"""Generate one daily voiceover, music bed, and video with Gemini media APIs.

The script is intentionally resumable: items already marked ready are skipped, failures are
recorded on the individual item, and --stream can rerun only one media type. Generated files are
written to outputs/ for the workflow to publish as GitHub Release assets.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import wave
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
API = "https://generativelanguage.googleapis.com/v1beta"
FILES = {
    "music": ROOT / "data/dashboard.json",
    "voiceover": ROOT / "data/voiceover.json",
    "video": ROOT / "data/suntravel.json",
}
DEFAULT_VOICES = {
    "V-INVEST": "Charon",
    "V-TRAVEL-F": "Leda",
    "V-TRAVEL-M": "Iapetus",
    "V-CALM": "Achernar",
    "V-SLEEP": "Enceladus",
}


class MediaError(RuntimeError):
    pass


def request_json(url, key, payload=None, timeout=120):
    data = json.dumps(payload).encode() if payload is not None else None
    req = Request(url, data=data, headers={"Content-Type": "application/json", "x-goog-api-key": key})
    for attempt in range(1, 5):
        try:
            with urlopen(req, timeout=timeout) as response:
                return json.loads(response.read())
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:900]
            if error.code in (429, 500, 502, 503, 504) and attempt < 4:
                time.sleep(min(30, 4 * 2 ** (attempt - 1)))
                continue
            raise MediaError(f"API {error.code}: {detail}") from error
        except URLError as error:
            if attempt < 4:
                time.sleep(min(30, 4 * 2 ** (attempt - 1)))
                continue
            raise MediaError(f"network error: {error.reason}") from error


def find_block(value, block_type):
    if isinstance(value, dict):
        if value.get("type") == block_type and value.get("data"):
            return value
        for child in value.values():
            found = find_block(child, block_type)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_block(child, block_type)
            if found:
                return found
    return None


def find_video_uri(value):
    if isinstance(value, dict):
        uri = value.get("uri")
        if isinstance(uri, str) and uri.startswith("http"):
            return uri
        for child in value.values():
            found = find_video_uri(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_video_uri(child)
            if found:
                return found
    return None


def latest_brief(path, target_date):
    payload = json.loads(path.read_text())
    brief = next((b for b in reversed(payload.get("briefs", [])) if b.get("date") == target_date), None)
    if brief is None:
        raise MediaError(f"no brief for {target_date} in {path.name}")
    return payload, brief


def normalized_music_items(brief):
    if "items" not in brief:
        brief["items"] = [
            {"type": "音樂 prompt", "purpose": brief.get("focus", ""), "engine": "Lyria", "status": "prompt", "text": text}
            for text in brief.get("prompts", [])
        ]
    return brief["items"]


def choose_item(items, accepted_types, index=0):
    candidates = [item for item in items if item.get("type") in accepted_types]
    if not candidates:
        raise MediaError(f"no matching item: {', '.join(sorted(accepted_types))}")
    selected = candidates[min(index, len(candidates) - 1)]
    return None if selected.get("generation", {}).get("status") == "ready" else selected


def voice_map():
    result = dict(DEFAULT_VOICES)
    raw = os.environ.get("SAIDIO_VOICE_MAP_JSON", "").strip()
    if raw:
        result.update(json.loads(raw))
    return result


def generate_tts(item, key, out_path):
    voices = voice_map()
    voice_code = item.get("voice") or "V-INVEST"
    speech = [{"voice": voices.get(voice_code, "Kore")}]
    text = item["text"]
    if "[F]" in text and "[M]" in text:
        speech = [
            {"speaker": "F", "voice": voices.get("V-TRAVEL-F", "Leda")},
            {"speaker": "M", "voice": voices.get("V-TRAVEL-M", "Iapetus")},
        ]
        text = "請以自然的繁體中文雙人對話朗讀；F 與 M 是說話者標記。\n" + text
    payload = {
        "model": os.environ.get("TTS_MODEL", "gemini-3.1-flash-tts-preview"),
        "input": text,
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": speech},
    }
    response = request_json(f"{API}/interactions", key, payload)
    block = find_block(response, "audio")
    if not block:
        raise MediaError("TTS response contained no audio")
    pcm = base64.b64decode(block["data"])
    with wave.open(str(out_path), "wb") as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(24000); wav.writeframes(pcm)


def generate_music(item, key, out_path):
    payload = {
        "model": os.environ.get("LYRIA_MODEL", "lyria-3-clip-preview"),
        "input": item["text"],
        "response_format": {"type": "audio"},
    }
    response = request_json(f"{API}/interactions", key, payload, timeout=300)
    block = find_block(response, "audio")
    if not block:
        raise MediaError("Lyria response contained no audio")
    out_path.write_bytes(base64.b64decode(block["data"]))


def generate_video(item, key, out_path):
    model = os.environ.get("VEO_MODEL", "veo-3.1-fast-generate-preview")
    payload = {
        "instances": [{"prompt": item["text"]}],
        "parameters": {
            "aspectRatio": os.environ.get("VEO_ASPECT_RATIO", "9:16"),
            "durationSeconds": os.environ.get("VEO_DURATION_SECONDS", "8"),
            "resolution": os.environ.get("VEO_RESOLUTION", "720p"),
            "sampleCount": 1,
        },
    }
    operation = request_json(f"{API}/models/{model}:predictLongRunning", key, payload)
    name = operation.get("name")
    if not name:
        raise MediaError("Veo did not return an operation name")
    deadline = time.time() + int(os.environ.get("VEO_TIMEOUT_SECONDS", "600"))
    while time.time() < deadline:
        time.sleep(10)
        operation = request_json(f"{API}/{name}", key, timeout=60)
        if operation.get("done"):
            break
    else:
        raise MediaError("Veo generation timed out; rerun to try again")
    if operation.get("error"):
        raise MediaError(f"Veo failed: {operation['error']}")
    uri = find_video_uri(operation.get("response", operation))
    if not uri:
        raise MediaError("Veo completed without a downloadable video URI")
    req = Request(uri, headers={"x-goog-api-key": key})
    with urlopen(req, timeout=180) as response:
        out_path.write_bytes(response.read())


def asset_url(filename, target_date):
    base = os.environ.get("SAIDIO_ASSET_BASE_URL", "").rstrip("/")
    if not base:
        repo = os.environ.get("GITHUB_REPOSITORY", "sssunwl/saidio")
        base = f"https://github.com/{repo}/releases/download/media-{target_date[:7]}"
    return f"{base}/{filename}"


def mark(item, status, **extra):
    item["generation"] = {
        **item.get("generation", {}),
        "status": status,
        "updatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **extra,
    }


def run_stream(stream, target_date, key, dry_run=False):
    path = FILES[stream]
    payload, brief = latest_brief(path, target_date)
    if stream == "music":
        items = normalized_music_items(brief)
        item = choose_item(items, {"音樂 prompt"}, int(os.environ.get("SAIDIO_MUSIC_INDEX", "8")))
        suffix, generator = ".mp3", generate_music
    elif stream == "voiceover":
        item = choose_item(brief.get("items", []), {"旁白腳本"}, int(os.environ.get("SAIDIO_VOICE_INDEX", "0")))
        suffix, generator = ".wav", generate_tts
    else:
        item = choose_item(brief.get("items", []), {"B-roll"}, int(os.environ.get("SAIDIO_VIDEO_INDEX", "0")))
        suffix, generator = ".mp4", generate_video
    if item is None:
        print(f"{stream}: already ready")
        return None
    filename = f"{target_date}-{stream}{suffix}"
    if dry_run:
        print(f"{stream}: would generate {filename} from {item.get('type')}")
        return filename
    OUTPUTS.mkdir(exist_ok=True)
    out_path = OUTPUTS / filename
    mark(item, "running")
    try:
        generator(item, key, out_path)
        mark(item, "ready", model={"music": os.environ.get("LYRIA_MODEL", "lyria-3-clip-preview"), "voiceover": os.environ.get("TTS_MODEL", "gemini-3.1-flash-tts-preview"), "video": os.environ.get("VEO_MODEL", "veo-3.1-fast-generate-preview")}[stream], assetUrl=asset_url(filename, target_date), filename=filename)
        print(f"{stream}: generated {filename}")
    except Exception as error:
        mark(item, "failed", error=str(error)[:500])
        print(f"{stream}: failed: {error}", file=sys.stderr)
    payload["updatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return filename


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stream", choices=["all", *FILES], default="all")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    key = os.environ.get("GEMINI_API_KEY")
    if not key and not args.dry_run:
        sys.exit("GEMINI_API_KEY is required")
    streams = list(FILES) if args.stream == "all" else [args.stream]
    for stream in streams:
        try:
            run_stream(stream, args.date, key or "dry-run", args.dry_run)
        except Exception as error:
            print(f"{stream}: failed before generation: {error}", file=sys.stderr)


if __name__ == "__main__":
    main()
