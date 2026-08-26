from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "esteros-photos"
OUTPUT = ROOT / "docs" / "assets" / "esteros-contact-sheet.jpg"

SCORES = {
    1: 7.5, 2: 6.0, 3: 7.5, 4: 5.5, 5: 7.8, 6: 6.3, 7: 6.8,
    8: 7.9, 9: 7.0, 10: 5.5, 11: 5.8, 12: 8.4, 13: 7.6, 14: 7.2,
}


def font(size: int, bold: bool = False):
    candidates = (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def main():
    files = sorted(SOURCE.glob("*.jpg"), key=lambda p: int(p.stem.rsplit(" ", 1)[-1]))
    card_w, card_h = 360, 300
    cols = 3
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * card_w, rows * card_h), "#f2eee4")
    draw = ImageDraw.Draw(sheet)
    title_font = font(24, True)
    meta_font = font(16)
    score_font = font(20, True)

    for i, path in enumerate(files):
        number = int(path.stem.rsplit(" ", 1)[-1])
        image = Image.open(path).convert("RGB")
        image.thumbnail((card_w - 24, 220))
        x = (i % cols) * card_w
        y = (i // cols) * card_h
        image_x = x + (card_w - image.width) // 2
        image_y = y + 12
        sheet.paste(image, (image_x, image_y))
        draw.text((x + 12, y + 238), f"#{number}  {path.name}", fill="#102f56", font=title_font)
        draw.text((x + 12, y + 268), f"{Image.open(path).size[0]} × {Image.open(path).size[1]} px", fill="#53606e", font=meta_font)
        draw.text((x + card_w - 84, y + 263), f"{SCORES[number]:.1f}", fill="#b34b2e", font=score_font)
        draw.line((x, y + card_h - 1, x + card_w, y + card_h - 1), fill="#d2c8b8", width=1)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUTPUT, quality=92, optimize=True)
    print(f"Wrote {OUTPUT} ({sheet.width}x{sheet.height})")


if __name__ == "__main__":
    main()
