#!/usr/bin/env python3
"""Assemble a vertical short video from AI-generated scenes + narration.

Reads a JSON project config, scales every scene clip to the output frame,
burns text overlays, concatenates the scenes, and mixes the narration track.

Usage:
    python src/assemble.py --config project.json --out final.mp4 [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from captions import overlay_text, position_expr


def run(cmd: list[str], dry_run: bool) -> None:
    print("+", " ".join(cmd))
    if not dry_run:
        subprocess.run(cmd, check=True)


def build_scene_filter(scene: dict, cfg: dict) -> str:
    """ffmpeg filter chain for one scene: scale/crop to frame, burn overlay."""
    out = cfg["output"]
    w, h, fps = out["width"], out["height"], out.get("fps", 30)
    filters = [
        f"scale={w}:{h}:force_original_aspect_ratio=increase",
        f"crop={w}:{h}",
        f"fps={fps}",
        "setsar=1",
    ]
    overlay = scene.get("overlay")
    if overlay and overlay.get("text"):
        text = overlay_text(overlay["text"])
        x, y = position_expr(overlay.get("position", "bottom"), w, h)
        parts = [
            f"fontfile={cfg['font']}",
            f"text='{text}'",
            "fontsize=" + str(overlay.get("fontsize", 72)),
            "fontcolor=white",
            "borderw=3",
            "bordercolor=black",
            f"x={x}",
            f"y={y}",
            "line_spacing=10",
        ]
        if "start" in overlay and "end" in overlay:
            parts.append(f"enable='between(t,{overlay['start']},{overlay['end']})'")
        filters.append("drawtext=" + ":".join(parts))
    return ",".join(filters)


def assemble(config_path: Path, out_path: Path, dry_run: bool = False) -> None:
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    base = config_path.parent
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        scene_files = []
        for i, scene in enumerate(cfg["scenes"]):
            clip = base / scene["clip"]
            dest = tmp / f"scene_{i:03d}.mp4"
            run([
                "ffmpeg", "-y", "-i", str(clip),
                "-vf", build_scene_filter(scene, cfg),
                "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                str(dest),
            ], dry_run)
            scene_files.append(dest)

        concat_list = tmp / "concat.txt"
        if not dry_run:
            concat_list.write_text(
                "".join(f"file '{f}'\n" for f in scene_files), encoding="utf-8"
            )
        video_only = tmp / "video.mp4"
        run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_list), "-c", "copy", str(video_only),
        ], dry_run)

        narration = base / cfg["narration"]
        run([
            "ffmpeg", "-y", "-i", str(video_only), "-i", str(narration),
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-shortest", str(out_path),
        ], dry_run)
    print(f"Done -> {out_path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the ffmpeg commands without running them")
    args = parser.parse_args(argv)
    assemble(args.config, args.out, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
