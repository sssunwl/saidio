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


def best_trim(strip, master_width, cards):
    """How much to trim off the master's left so each card gets a centred motif.

    An image model cannot land its motifs on exact 1/N boundaries, so an otherwise
    correct plate still slices arches down the middle. Trimming where we start cutting
    is free; moving the artwork is not.

    The objective is CENTRING, not "quiet at the seam". Minimising ink at the cuts has
    a degenerate answer for frame-shaped motifs — an arch's interior is bare paper, so
    the cheapest seam runs straight through the middle of an arch. Measured on the
    first real plate that made the drift three times worse. Centring each card's ink
    mass is what actually matches the eye.
    """
    ink = ink_profile(strip)
    strip_width = strip.width
    half = CARD_WIDTH / 2

    def cost(trim):
        # Trimming `trim` master px rescales the remainder over the whole strip.
        span = master_width - trim
        if span < master_width * 0.5:
            return float("inf")
        total = 0.0
        for index in range(cards):
            weight = mass = 0.0
            for x in range(index * CARD_WIDTH, (index + 1) * CARD_WIDTH, 4):
                source = int((trim + x * span / strip_width) * strip_width / master_width)
                if not 0 <= source < strip_width:
                    return float("inf")
                value = ink[source]
                mass += value
                weight += value * (x - index * CARD_WIDTH)
            if mass > 0:
                total += abs(weight / mass - half)
        return total

    step = max(1, master_width // (cards * 60))
    candidates = range(0, master_width // cards, step)
    chosen = min(candidates, key=cost)
    baseline = cost(0)
    gain = 0.0 if baseline in (0, float("inf")) else 1 - cost(chosen) / baseline
    return chosen, gain


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
        "--align", choices=("auto", "none"), default="none",
        help="auto: trim the master so motifs sit nearer their card centres. Best effort — "
             "on a plate that is already on the grid it makes things worse, so read the "
             "seam report and only reach for it when the report says the cuts are dirty",
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
        trim, gain = best_trim(strip, master.width, args.cards)
        if trim and gain > 0.15:
            master = master.crop((trim, 0, master.width, master.height))
            strip = fit_to_strip(master, strip_width, args.fit)
            print(f"align: trimmed {trim}px off the master — motifs sit {gain:.0%} "
                  "closer to their card centres")
        else:
            print("align: plate is already on the grid, cutting as-is")

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
