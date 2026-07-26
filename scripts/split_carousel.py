#!/usr/bin/env python3
"""Cut one wide master image into N ready-to-post Instagram carousel cards.

Why this exists: a set of N cards laid side by side is N×0.75 wide — 4.5:1 for six
3:4 cards — and no image model outputs that. So the master arrives at whatever the
tool gave (usually 16:9) and has to be fitted here.

Two fit modes, and the choice is not cosmetic:

  --fit stretch   Non-uniformly scale the master to the full strip. Invisible on
                  abstract texture, gradient or blurred botanical backgrounds.
                  Anything with recognizable geometry — arches, framed photos,
                  objects, faces — will look wrong. Default, because the master is
                  supposed to be a text-free background plate.
  --fit cover     Scale uniformly and crop the overflow. Keeps geometry honest but
                  throws away most of the master's height.

The preview (--preview) is the part worth looking at before you commit: it draws the
seams and the 80 px danger zone either side of them, so you can see which decoration
is about to be sliced across a swipe.

    python3 scripts/split_carousel.py plate.png --cards 9
    python3 scripts/split_carousel.py plate.png --cards 6 --fit cover --out ./day01
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

CARD_WIDTH, CARD_HEIGHT = 1080, 1440  # 3:4, the 2026 Instagram feed + grid ratio
SEAM_DANGER = 80  # keep text, faces and logos this far from every cut


def fit_to_strip(master, strip_width, mode):
    """Bring the master up to the exact strip size."""
    if mode == "stretch":
        return master.resize((strip_width, CARD_HEIGHT), Image.Resampling.LANCZOS)
    scale = max(strip_width / master.width, CARD_HEIGHT / master.height)
    scaled = master.resize(
        (round(master.width * scale), round(master.height * scale)), Image.Resampling.LANCZOS
    )
    left = (scaled.width - strip_width) // 2
    top = (scaled.height - CARD_HEIGHT) // 2
    return scaled.crop((left, top, left + strip_width, top + CARD_HEIGHT))


def write_preview(strip, cards, path):
    """Draw seams and their danger zones so a bad slice is visible before posting."""
    scale = 0.25
    preview = strip.resize((round(strip.width * scale), round(strip.height * scale)))
    draw = ImageDraw.Draw(preview, "RGBA")
    for index in range(1, cards):
        x = index * CARD_WIDTH * scale
        draw.rectangle(
            [x - SEAM_DANGER * scale, 0, x + SEAM_DANGER * scale, preview.height],
            fill=(255, 60, 60, 70),
        )
        draw.line([(x, 0), (x, preview.height)], fill=(255, 60, 60, 255), width=2)
    preview.save(path, "PNG")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("source", type=Path, help="the wide, text-free master plate")
    parser.add_argument("--cards", type=int, default=9, help="how many cards (6–12)")
    parser.add_argument("--fit", choices=("stretch", "cover"), default="stretch")
    parser.add_argument("--out", type=Path, help="output directory (default: <source>_cards/)")
    parser.add_argument("--preview", action="store_true", default=True)
    parser.add_argument("--no-preview", dest="preview", action="store_false")
    args = parser.parse_args()

    if not 6 <= args.cards <= 12:
        raise SystemExit("--cards must be between 6 and 12; 8–10 performs best")
    if not args.source.exists():
        raise SystemExit(f"no such file: {args.source}")

    master = Image.open(args.source).convert("RGB")
    strip_width = CARD_WIDTH * args.cards
    upscale = strip_width / master.width
    if args.fit == "stretch" and upscale > 5:
        print(f"warning: stretching {upscale:.1f}× — fine for texture, not for structure")

    strip = fit_to_strip(master, strip_width, args.fit)
    out = args.out or args.source.with_name(f"{args.source.stem}_cards")
    out.mkdir(parents=True, exist_ok=True)

    for index in range(args.cards):
        left = index * CARD_WIDTH
        card = strip.crop((left, 0, left + CARD_WIDTH, CARD_HEIGHT))
        card.save(out / f"{args.source.stem}_{index + 1:02d}.png", "PNG")

    print(f"master {master.width}×{master.height} → strip {strip_width}×{CARD_HEIGHT} ({args.fit})")
    print(f"wrote {args.cards} cards of {CARD_WIDTH}×{CARD_HEIGHT} to {out}/")
    if args.preview:
        preview_path = out / "_seam_preview.png"
        write_preview(strip, args.cards, preview_path)
        print(f"seam preview: {preview_path.name} — red bands are the ±{SEAM_DANGER}px no-text zone")


if __name__ == "__main__":
    main()
