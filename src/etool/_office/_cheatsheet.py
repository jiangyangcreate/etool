"""Command cheat-sheet wallpaper generator (Pillow; data-driven, optional LLM data)."""

from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Any

from .._core.errors import ErrorCode, EtoolError

_BG_COLOR = (0x1A, 0x1A, 0x2E)
_TEXT_COLOR = (0xF8, 0xF8, 0xF2)
_ACCENT_COLOR = (0x50, 0xFA, 0x7B)
_CATEGORY_COLORS = [
    (0xFF, 0x79, 0xC6),  # pink
    (0x8B, 0xE9, 0xFD),  # cyan
    (0x50, 0xFA, 0x7B),  # green
    (0xFF, 0xB8, 0x6C),  # orange
    (0xBD, 0x93, 0xF9),  # purple
    (0xF1, 0xFA, 0x8C),  # yellow
    (0xFF, 0x55, 0x55),  # red
]
_SYSTEM_FONTS = [
    # Windows
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    # macOS
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    # Linux
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def _normalize_data(data: dict[str, Any]) -> list[dict[str, Any]]:
    categories = data.get("categories") if isinstance(data, dict) else None
    if not categories or not isinstance(categories, list):
        raise EtoolError(
            ErrorCode.VALIDATION_ERROR,
            'cheatsheet data must be {"categories": [{"name", "commands": [{"command", "description"}]}]}',
        )
    normalized = []
    for category in categories:
        commands = [
            (str(cmd.get("command", "")), str(cmd.get("description", "")))
            for cmd in category.get("commands", [])
            if cmd.get("command")
        ]
        if commands:
            normalized.append({"name": str(category.get("name", "")), "commands": commands})
    if not normalized:
        raise EtoolError(ErrorCode.VALIDATION_ERROR, "cheatsheet data has no commands")
    return normalized


class ManagerCheatsheet:
    @staticmethod
    def _font(size: int, font_path: str | None = None):
        from PIL import ImageFont

        candidates = ([font_path] if font_path else []) + _SYSTEM_FONTS
        for path in candidates:
            try:
                if Path(path).exists():
                    return ImageFont.truetype(path, size)
            except OSError:
                continue
        return ImageFont.load_default(size)

    @classmethod
    def generate(
        cls,
        data: dict[str, Any],
        output_path: str,
        *,
        title: str | None = None,
        subtitle: str | None = None,
        width: int = 1920,
        height: int = 1080,
        font_path: str | None = None,
        left_margin_ratio: float = 0.25,
    ) -> str:
        """Render a cheat-sheet wallpaper PNG from category/command data.

        :param data: {"categories": [{"name": str, "commands": [{"command", "description"}]}]}
        :param left_margin_ratio: fraction of width kept clear for desktop icons (0 disables)
        :return: the output path
        """
        from PIL import Image, ImageDraw

        categories = _normalize_data(data)[:9]
        left_margin = int(width * max(0.0, min(left_margin_ratio, 0.6)))

        img = Image.new("RGBA", (width, height), _BG_COLOR)
        draw = ImageDraw.Draw(img)

        # gradient background
        for y in range(height):
            ratio = y / height
            draw.line(
                [(0, y), (width, y)],
                fill=(
                    int(_BG_COLOR[0] * (1 - ratio * 0.3)),
                    int(_BG_COLOR[1] * (1 - ratio * 0.3)),
                    int(_BG_COLOR[2] + ratio * 20),
                ),
            )

        # decorative dots (fixed seed for reproducible output)
        rng = random.Random(42)
        for _ in range(20):
            x, y = rng.randint(0, width), rng.randint(0, height)
            size = rng.randint(2, max(3, width // 480))
            draw.ellipse([x, y, x + size, y + size], fill=(0x8B, 0xE9, 0xFD, rng.randint(30, 80)))

        # reserved left area with a thin accent border
        if left_margin > 0:
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([0, 0, left_margin, height], fill=(0x2A, 0x2A, 0x40, 180))
            overlay_draw.rectangle(
                [left_margin - 3, 0, left_margin, height], fill=(0x50, 0xFA, 0x7B, 100)
            )
            img = Image.alpha_composite(img, overlay)
            draw = ImageDraw.Draw(img)

        # title block centered in the content area
        content_x = left_margin
        content_width = width - left_margin
        title_font = cls._font(max(24, int(height * 0.055)), font_path)
        subtitle_font = cls._font(max(14, int(height * 0.024)), font_path)
        title_text = title or "Cheat Sheet"
        title_w = draw.textbbox((0, 0), title_text, font=title_font)[2]
        title_y = int(height * 0.03)
        draw.text(
            (content_x + (content_width - title_w) // 2 + 3, title_y + 3),
            title_text,
            font=title_font,
            fill=(0, 0, 0),
        )
        draw.text(
            (content_x + (content_width - title_w) // 2, title_y),
            title_text,
            font=title_font,
            fill=_CATEGORY_COLORS[0],
        )
        grid_top = title_y + int(height * 0.075)
        if subtitle:
            sub_w = draw.textbbox((0, 0), subtitle, font=subtitle_font)[2]
            draw.text(
                (content_x + (content_width - sub_w) // 2, grid_top),
                subtitle,
                font=subtitle_font,
                fill=_TEXT_COLOR,
            )
            grid_top += int(height * 0.05)

        # category cards in an up-to-3×3 grid
        cols = min(3, len(categories))
        rows = math.ceil(len(categories) / cols)
        outer = max(10, width // 100)
        grid_w = content_width - 2 * outer
        grid_h = height - grid_top - outer
        cell_w = grid_w // cols
        cell_h = grid_h // rows

        name_font = cls._font(max(12, int(cell_h * 0.085)), font_path)
        cmd_font = cls._font(max(11, int(cell_h * 0.07)), font_path)
        desc_font = cls._font(max(10, int(cell_h * 0.055)), font_path)
        row_step = int(cell_h * 0.115)
        pad = max(8, cell_w // 40)

        for i, category in enumerate(categories):
            cell_x = content_x + outer + (i % cols) * cell_w
            cell_y = grid_top + (i // cols) * cell_h
            draw.rounded_rectangle(
                [cell_x + 4, cell_y + 4, cell_x + cell_w - 4, cell_y + cell_h - 4],
                radius=max(6, cell_h // 30),
                fill=(40, 40, 60, 180),
            )
            color = _CATEGORY_COLORS[i % len(_CATEGORY_COLORS)]
            draw.text((cell_x + pad, cell_y + pad), category["name"], font=name_font, fill=color)

            line_y = cell_y + pad + int(cell_h * 0.13)
            for command, description in category["commands"]:
                if line_y + row_step > cell_y + cell_h - pad:
                    break
                draw.text((cell_x + pad, line_y), command, font=cmd_font, fill=_ACCENT_COLOR)
                if description:
                    desc_w = draw.textbbox((0, 0), description, font=desc_font)[2]
                    draw.text(
                        (cell_x + cell_w - pad - desc_w, line_y + int(row_step * 0.12)),
                        description,
                        font=desc_font,
                        fill=_TEXT_COLOR,
                    )
                line_y += row_step

        out = Path(output_path)
        if out.parent != Path("."):
            out.parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(out, "PNG")
        return str(out)

    @staticmethod
    def data_from_llm(keyword: str, **chat_kwargs: Any) -> dict[str, Any]:
        """Ask an LLM (see ManagerLlm) for cheat-sheet data about a tool/tech keyword."""
        from .._ai._llm import ManagerLlm

        prompt = (
            f'Create command cheat-sheet data for the technology "{keyword}". '
            "Group commands by purpose: at most 9 categories, at most 7 commands each. "
            "Descriptions must be short (under 30 characters), in the same language as the keyword. "
            "Output exactly one JSON object, no markdown fences:\n"
            '{"categories": [{"name": "...", "commands": '
            '[{"command": "...", "description": "..."}]}]}'
        )
        data = ManagerLlm.extract_json(ManagerLlm.chat(prompt, **chat_kwargs))
        _normalize_data(data)
        return data
