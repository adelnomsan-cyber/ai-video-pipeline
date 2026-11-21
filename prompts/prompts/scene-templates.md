# Scene generation prompt templates

Templates used to generate consistent scenes for the Egyptian Arabic
short-video channel. Fill the `{slots}` and keep style keywords stable so
clips cut together cleanly.

## Character-consistent base style

```
{character description}, minimalist white cartoon character, clean dark
background, soft rim lighting, flat illustration style, vertical composition,
9:16, cinematic, smooth motion
```

## Hook scene (first 1-2 seconds)

```
{character} {hook action - something visually surprising or relatable},
extreme scroll of an endless vertical feed behind them, slight camera push-in,
base style
```

## Build / transformation scene

```
{character} {building or creating something - bricks, code, sketch},
time-lapse feel, objects snapping into place, warm accent light, base style
```

## Split-screen contrast

```
split screen: left {passive behaviour, e.g. lying in bed scrolling},
right {active behaviour, e.g. working at a desk}, mirrored framing, base style
```

## Final card / call-to-action

```
{character} facing camera, confident, {gesture}, negative space at the top
for the closing caption, base style
```

## Notes

- Keep the character description identical across prompts for continuity.
- Generate start and end frames when the model supports it; chain scene N's
  end frame as scene N+1's start frame.
- Short clips (2-4 s) cut tighter than one long generation.
