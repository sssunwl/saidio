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


def ink_profile(strip):
    """Mean darkness per column, 0 = paper, higher = decoration.

    Resizing to one pixel tall averages each column — cheap, and enough to tell an
    arch leg from bare paper without pulling in numpy.
    """
    row = strip.convert("L").resize((strip.width, 1), Image.Resampling.BOX)
    values = list(row.getdata())
    paper = sorted(values)[int(len(values) * 0.95)]  # the plate's own background tone
    return [max(0, paper - v) for v in values]


def find_motif_centres(master, cards):
    """Locate the repeating motif once per card, by its vertical strokes.

    Sampled from the middle band only: the top is usually empty and the bottom often
    carries a continuous rule, and neither says anything about where a repeat sits.
    Returns one centre per repeat, or None when the plate has no countable rhythm
    (a gradient wash, a plain texture) or the count does not match the card count.
    """
    width, height = master.size
    band = master.convert("L").crop((0, round(height * 0.25), width, round(height * 0.70)))
    values = list(band.resize((width, 1), Image.Resampling.BOX).getdata())
    paper = sorted(values)[int(len(values) * 0.95)]
    ink = [max(0, paper - v) for v in values]
    if not any(ink):
        return None

    threshold = max(ink) * 0.35
    peaks, index = [], 0
    while index < width:
        if ink[index] > threshold:
            start = index
            while index < width and ink[index] > threshold:
                index += 1
            peaks.append((start + index - 1) / 2)
        else:
            index += 1

    # A frame motif shows two strokes per repeat (an arch's legs); a rule or stem shows one.
    if len(peaks) == cards * 2:
        return [(peaks[2 * i] + peaks[2 * i + 1]) / 2 for i in range(cards)]
    if len(peaks) == cards:
        return peaks
    return None


def grid_crop(master, cards):
    """Crop so the motif rhythm lands exactly on the card grid.

    The mismatch is systematic: a model spaces its repeats evenly across the artwork
    but insets the whole block from the edges, so the repeat pitch never equals the
    card pitch and the error accumulates outwards — the end cards look lopsided while
    the middle ones look fine. Cropping to half a pitch outside the first and last
    repeat makes the two pitches identical.
    """
    centres = find_motif_centres(master, cards)
    if not centres or len(centres) < 2:
        return None
    width = master.width
    pitch = (centres[-1] - centres[0]) / (cards - 1)
    left = centres[0] - pitch / 2
    right = centres[-1] + pitch / 2
    if left < -1 or right > width + 1 or right - left < width * 0.5:
        return None

    def worst(origin, span):
        return max(
            abs(centres[i] - (origin + span / cards * (i + 0.5))) * (CARD_WIDTH * cards / span)
            for i in range(cards)
        )

    before, after = worst(0, width), worst(left, right - left)
    if after >= before:
        return None
    return (max(0, round(left)), min(width, round(right))), before, after


def report_seams(strip, cards):
    """Print how much decoration each cut runs through.

    The seam preview shows this, but a number is easier to act on than a red band:
    a plate whose motifs land on the grid scores near zero at every cut.
    """
    ink = ink_profile(strip)
    scores = []
    for index in range(1, cards):
        x = index * CARD_WIDTH
        window = ink[x - SEAM_DANGER:x + SEAM_DANGER]
        scores.append(sum(window) / max(len(window), 1))
    if not scores:
        return
    worst = max(scores)
    print("seam report — decoration crossing each cut (lower is cleaner):")
    for index, score in enumerate(scores, 1):
        bar = "█" * min(30, round(score / 2)) or "·"
        flag = "  ← sliced" if score > 12 else ""
        print(f"  cut {index}|{index + 1}  {score:5.1f}  {bar}{flag}")
    if worst > 12:
        print("  at least one motif is being cut in half. Either regenerate the plate with "
              "the repeats on the grid, or try --align auto and compare.")


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
    parser.add_argument(
        "--align", choices=("auto", "none"), default="auto",
        help="auto: crop the master so the repeat pitch matches the card pitch. Does nothing "
             "unless it finds exactly one repeat per card and the crop measurably helps",
    )
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

    if args.align == "auto":
        result = grid_crop(master, args.cards)
        if result:
            (left, right), before, after = result
            master = master.crop((left, 0, right, master.height))
            strip = fit_to_strip(master, strip_width, args.fit)
            print(f"align: cropped the master to x={left}–{right} — worst motif offset "
                  f"{before:.0f}px → {after:.0f}px")
        else:
            print("align: no countable repeat on the card grid, cutting as-is")

    out = args.out or args.source.with_name(f"{args.source.stem}_cards")
    out.mkdir(parents=True, exist_ok=True)

    for index in range(args.cards):
        left = index * CARD_WIDTH
        card = strip.crop((left, 0, left + CARD_WIDTH, CARD_HEIGHT))
        card.save(out / f"{args.source.stem}_{index + 1:02d}.png", "PNG")

    print(f"master {master.width}×{master.height} → strip {strip_width}×{CARD_HEIGHT} ({args.fit})")
    print(f"wrote {args.cards} cards of {CARD_WIDTH}×{CARD_HEIGHT} to {out}/")
    report_seams(strip, args.cards)
    if args.preview:
        preview_path = out / "_seam_preview.png"
        write_preview(strip, args.cards, preview_path)
        print(f"seam preview: {preview_path.name} — red bands are the ±{SEAM_DANGER}px no-text zone")


if __name__ == "__main__":
    main()
