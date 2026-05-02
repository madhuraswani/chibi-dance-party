"""
Script to generate a simple chibi‑style placeholder image.

This script uses the Python Imaging Library (Pillow) to draw a cute
cartoon character. It generates a 256x256 PNG with a round head,
large eyes, and a smiling mouth. The image is saved to
`characters/sample_chibi.png` relative to the project root.

You can modify the parameters below to change colours or facial
features. Feel free to replace this placeholder with your own PNG
sprites.
"""

from pathlib import Path
from PIL import Image, ImageDraw

# Ensure output directory exists
out_dir = Path(__file__).resolve().parent / "characters"
out_dir.mkdir(parents=True, exist_ok=True)


def draw_chibi(path: Path) -> None:
    """Generate a simple chibi placeholder image and save it."""
    # Create transparent canvas
    size = (256, 256)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Head background
    head_radius = 100
    head_center = (size[0] // 2, size[1] // 2)
    bbox = [
        head_center[0] - head_radius,
        head_center[1] - head_radius,
        head_center[0] + head_radius,
        head_center[1] + head_radius,
    ]
    draw.ellipse(bbox, fill=(255, 230, 230, 255))

    # Eyes
    eye_radius = 20
    eye_y = head_center[1] - 20
    eye_offset_x = 40
    for sign in (-1, 1):
        eye_x = head_center[0] + sign * eye_offset_x
        eye_bbox = [
            eye_x - eye_radius,
            eye_y - eye_radius,
            eye_x + eye_radius,
            eye_y + eye_radius,
        ]
        draw.ellipse(eye_bbox, fill=(255, 255, 255, 255))  # white sclera
        pupil_radius = 10
        pupil_bbox = [
            eye_x - pupil_radius,
            eye_y - pupil_radius,
            eye_x + pupil_radius,
            eye_y + pupil_radius,
        ]
        draw.ellipse(pupil_bbox, fill=(0, 0, 0, 255))  # black pupil
    # Mouth
    mouth_box = [
        head_center[0] - 30,
        head_center[1] + 30,
        head_center[0] + 30,
        head_center[1] + 50,
    ]
    draw.arc(mouth_box, start=0, end=180, fill=(255, 105, 180, 255), width=4)

    # Blush cheeks
    blush_radius = 15
    blush_y = head_center[1] + 20
    blush_offset_x = 60
    for sign in (-1, 1):
        blush_x = head_center[0] + sign * blush_offset_x
        blush_bbox = [
            blush_x - blush_radius,
            blush_y - blush_radius,
            blush_x + blush_radius,
            blush_y + blush_radius,
        ]
        draw.ellipse(blush_bbox, fill=(255, 182, 193, 128))

    # Save image
    img.save(path, format="PNG")


if __name__ == "__main__":
    output_path = out_dir / "sample_chibi.png"
    draw_chibi(output_path)
    print(f"Chibi placeholder saved to {output_path}")
