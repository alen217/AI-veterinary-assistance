"""Generate 5 simple PNG images per class per split for testing."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def make_image(path: Path, color: tuple, text: str = "", size=(256, 256)):
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", size, color=color)
    if text:
        try:
            draw = ImageDraw.Draw(img)
            f = ImageFont.load_default()
            draw.text((10, 10), text, font=f, fill=(255, 255, 255))
        except Exception:
            pass
    img.save(path, format="PNG")


def main(base_dir: Path = Path("../data")):
    splits = ["train", "val", "test"]
    classes = ["mange", "fungal", "wound", "normal"]
    colors = {
        "mange": (200, 50, 50),
        "fungal": (50, 200, 50),
        "wound": (50, 50, 200),
        "normal": (180, 180, 180),
    }

    for split in splits:
        for cls in classes:
            folder = base_dir / split / cls
            folder.mkdir(parents=True, exist_ok=True)
            for i in range(5):
                fname = folder / f"{cls}_{i+1}.png"
                make_image(fname, colors.get(cls, (128, 128, 128)), text=f"{cls} {i+1}")

    print(f"Generated sample images under {base_dir.resolve()}")


if __name__ == "__main__":
    main(Path("../data"))
