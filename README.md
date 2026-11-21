# AI Video Pipeline

A small Python toolkit for assembling vertical short-form videos (9:16) from
AI-generated scene clips and voiceover narration. Built to power an Egyptian
Arabic Facebook content channel: scenes are generated with text-to-video
models, narration is voiced with a TTS service, and this pipeline does the
assembly - scaling, Arabic text overlays, captions, and audio - with ffmpeg.

## What it does

- Takes a project config (JSON) describing scenes, overlays, and narration
- Scales and crops every scene clip to 1080x1920 (9:16 vertical)
- Burns hook / punchline text overlays with proper Arabic shaping and bidi
- Concatenates scenes, mixes the narration track, normalizes loudness
- Writes a ready-to-upload MP4 (H.264 + AAC)

## Requirements

- Python 3.9+
- `ffmpeg` and `ffprobe` on your PATH
- `pip install -r requirements.txt`

For Arabic text you need a font that supports it (e.g. Cairo, Noto Naskh
Arabic, or Amiri). Point the config at the `.ttf` file.

## Quick start

```bash
python src/assemble.py --config examples/hook-video.config.json --out out/final.mp4
```

A project config looks like this (see `examples/` for a full one):

```json
{
  "output": { "width": 1080, "height": 1920, "fps": 30 },
  "font": "fonts/Cairo-Bold.ttf",
  "narration": "assets/narration.mp3",
  "scenes": [
    {
      "clip": "assets/scene-01.mp4",
      "overlay": { "text": "ساعتين سكرول... وفي الآخر إيه اللي اتغير؟", "position": "top", "start": 0.2, "end": 3.5 }
    }
  ]
}
```

## Repository layout

| Path | Purpose |
| --- | --- |
| `src/assemble.py` | Main assembly entry point (config -> final MP4) |
| `src/captions.py` | Arabic text shaping, wrapping and overlay placement |
| `prompts/scene-templates.md` | Reusable prompt templates for scene generation |
| `examples/` | Sample configs you can copy and adapt |

## Scene generation workflow

1. Draft the hook and narration in Egyptian Arabic.
2. Voice the narration with your TTS provider of choice.
3. Generate one clip per scene with a text-to-video model using the
   templates in `prompts/scene-templates.md` (start and end frames help
   continuity).
4. Fill in a config JSON and run `assemble.py`.

## License

MIT - see [LICENSE](LICENSE).
