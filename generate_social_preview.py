#!/usr/bin/env python3
"""Generate the Open Graph preview image for the site."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "combined.json"
OUTPUT_PATHS = [
    ROOT / "social-preview-v2.png",
    ROOT / "social-preview.png",
]

ROWS = [
    ("Hub-spoke", "hub-spoke-architecture"),
    ("Private PaaS", "private-connectivity-paas"),
    ("Global edge", "global-load-balancer"),
]

CLOUDS = ("azure", "aws", "gcp")
CLOUD_COLORS = {
    "azure": "#0078D4",
    "aws": "#FF9900",
    "gcp": "#EA4335",
}
CLOUD_NAMES = {
    "azure": "Azure",
    "aws": "AWS",
    "gcp": "GCP",
}


def render_mermaid_diagrams(data: dict, temp_dir: Path) -> dict[tuple[str, str], Path]:
    rendered: dict[tuple[str, str], Path] = {}
    puppeteer_config = temp_dir / "pptr.json"
    puppeteer_config.write_text('{"args":["--no-sandbox"]}\n')

    for _row_label, feature_id in ROWS:
        feature = next(item for item in data["features"] if item["id"] == feature_id)
        for cloud in CLOUDS:
            mmd_path = temp_dir / f"{feature_id}-{cloud}.mmd"
            png_path = temp_dir / f"{feature_id}-{cloud}.png"
            mmd_path.write_text(feature[cloud]["diagram"])
            subprocess.run(
                [
                    "npx",
                    "-y",
                    "@mermaid-js/mermaid-cli",
                    "-p",
                    str(puppeteer_config),
                    "-i",
                    str(mmd_path),
                    "-o",
                    str(png_path),
                    "-t",
                    "dark",
                    "-b",
                    "transparent",
                    "-w",
                    "320",
                    "-H",
                    "160",
                    "-s",
                    "2",
                    "-q",
                ],
                check=True,
            )
            rendered[(feature_id, cloud)] = png_path

    return rendered


def build_image(rendered: dict[tuple[str, str], Path]) -> None:
    width, height = 1200, 630
    bg = "#0d1117"
    surface = "#161b22"
    surface2 = "#21262d"
    border = "#30363d"
    text = "#e6edf3"
    text_dim = "#8b949e"
    accent = "#58a6ff"

    image = Image.new("RGBA", (width, height), bg)
    draw = ImageDraw.Draw(image)

    for y in range(height):
        blend = int(14 + (28 - 14) * (y / height))
        draw.line([(0, y), (width, y)], fill=(13, 17, blend, 255))

    font_regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    title_font = ImageFont.truetype(font_bold, 42)
    subtitle_font = ImageFont.truetype(font_regular, 20)
    pill_font = ImageFont.truetype(font_bold, 18)
    row_font = ImageFont.truetype(font_bold, 24)
    cloud_font = ImageFont.truetype(font_bold, 16)
    footer_font = ImageFont.truetype(font_regular, 14)

    margin_x = 44
    header_y = 34

    draw.text((margin_x, header_y), "Cloud Networking Compared", font=title_font, fill=text)
    draw.text(
        (margin_x, header_y + 54),
        "Azure, AWS, and GCP networking features, side by side.",
        font=subtitle_font,
        fill=text_dim,
    )

    pill_y = header_y + 4
    pill_specs = [
        ("Azure", CLOUD_COLORS["azure"]),
        ("AWS", CLOUD_COLORS["aws"]),
        ("GCP", CLOUD_COLORS["gcp"]),
    ]
    pill_x = width - margin_x
    for label, color in reversed(pill_specs):
        bbox = draw.textbbox((0, 0), label, font=pill_font)
        pill_width = (bbox[2] - bbox[0]) + 30
        pill_x -= pill_width
        draw.rounded_rectangle(
            (pill_x, pill_y, pill_x + pill_width, pill_y + 34),
            radius=17,
            fill=surface2,
            outline=border,
            width=1,
        )
        draw.ellipse((pill_x + 10, pill_y + 12, pill_x + 18, pill_y + 20), fill=color)
        draw.text((pill_x + 24, pill_y + 7), label, font=pill_font, fill=text)
        pill_x -= 12

    content_top = 122
    row_h = 148
    row_gap = 14
    label_w = 190
    tile_gap = 14
    tile_w = 284
    tile_h = 124
    right_x = margin_x + label_w + 20

    for idx, (row_label, feature_id) in enumerate(ROWS):
        y = content_top + idx * (row_h + row_gap)
        draw.rounded_rectangle(
            (margin_x, y, margin_x + label_w, y + tile_h),
            radius=18,
            fill=surface,
            outline=border,
            width=1,
        )
        row_bbox = draw.textbbox((0, 0), row_label, font=row_font)
        row_height = row_bbox[3] - row_bbox[1]
        draw.text((margin_x + 18, y + ((tile_h - row_height) // 2) - 4), row_label, font=row_font, fill=text)

        for cloud_index, cloud in enumerate(CLOUDS):
            x = right_x + cloud_index * (tile_w + tile_gap)
            draw.rounded_rectangle(
                (x, y, x + tile_w, y + tile_h),
                radius=18,
                fill=surface,
                outline=border,
                width=1,
            )
            draw.text((x + 18, y + 14), CLOUD_NAMES[cloud], font=cloud_font, fill=CLOUD_COLORS[cloud])
            diagram = Image.open(rendered[(feature_id, cloud)]).convert("RGBA")
            alpha = diagram.getchannel("A")
            bbox = alpha.getbbox()
            if bbox:
                diagram = diagram.crop(bbox)
            max_w = tile_w - 28
            max_h = tile_h - 46
            scale = min(max_w / diagram.width, max_h / diagram.height)
            diagram = diagram.resize(
                (max(1, int(diagram.width * scale)), max(1, int(diagram.height * scale))),
                Image.LANCZOS,
            )
            px = x + (tile_w - diagram.width) // 2
            py = y + 34 + (max_h - diagram.height) // 2
            image.alpha_composite(diagram, (px, py))

    footer_y = height - 34
    draw.text(
        (margin_x, footer_y),
        "adstuart.github.io/cloud-networking-compared",
        font=footer_font,
        fill=text_dim,
    )

    for output_path in OUTPUT_PATHS:
        image.save(output_path)


def main() -> None:
    with DATA_PATH.open() as handle:
        data = json.load(handle)
    with tempfile.TemporaryDirectory(prefix="social-preview-") as temp_dir_name:
        rendered = render_mermaid_diagrams(data, Path(temp_dir_name))
        build_image(rendered)
    for output_path in OUTPUT_PATHS:
        print(f"Wrote {output_path} ({os.path.getsize(output_path)} bytes)")


if __name__ == "__main__":
    main()
