# EggWobble for Maya

**Unagi Tech Inc.（株式会社うなぎテック）** · v1.2.1 · [MIT License](LICENSE)

Soft, low-frequency “fried egg” outline: wobble on a disc (egg white) plus an offset circle (yolk). Create a live preview, tweak sliders in real time, then Confirm to bake.

Released by Unagi Tech Inc. Related: physical goods (e.g. Luci Brasil) and print data on MakersLabo may use the same look; this package is the Maya tool only.

## Requirements

- Autodesk Maya (Python / `maya.cmds` + OpenMaya)

Not affiliated with Autodesk.

## Install

1. Run `run-install-to-maya-scripts.cmd`  
   (or copy `egg_wobble.py` and `egg_wobble_launch.mel` into `Documents\maya\scripts\`)
2. Script Editor → **Python**:

```python
import importlib
import egg_wobble as ew
importlib.reload(ew)
ew.show()
```

Shelf: run `egg_wobble_launch.mel` from the MEL tab (or paste into a shelf button).

## Usage

Flow: **Create Mesh / Curve** → adjust sliders (live) → **Confirm（確定）** to bake.

| Button | Action |
|--------|--------|
| Create Mesh | Builds `ew_live` as a filled disc on XZ (`Thickness` > 0 extrudes). Sliders update it live. |
| Create Curve | Builds `ew_live` as periodic NURBS (white) + circle (yolk). Sliders update it live. |
| Randomize | New seed; applies immediately if live exists |
| Confirm（確定） | Renames `ew_live` → `ew_result…` and stops live updates |
| Discard live | Deletes the live preview object |
| Reset defaults | Restores default slider values (applies immediately if live) |

Units follow the scene (cm → Radius 5 ≈ ~10 cm across plus wobble).

## Parameters

| Control | Meaning | Tip |
|---------|---------|-----|
| Seed | Phase / shape variation | `7` matches the reference look |
| White radius | Egg-white size | |
| Wobble | Distortion (`0` = circle) | ~0.18–0.28 |
| Subdivs | Rim resolution | 64–128 |
| Include yolk | Toggle yolk | |
| Yolk radius / offset X·Z | Yolk size and position | |
| Thickness | Extrude; `0` = flat | ~0.8–3 mm for print-scale scenes |

Formula (shared with the Illustrator build):

`r(θ) = R × (1 + wobble × (0.35 cos(2θ+φ₂) + 0.55 cos(3θ+φ₃) + 0.25 cos(4θ+φ₄)))`

## License

MIT — see [LICENSE](LICENSE).

You may use, copy, modify, and redistribute. If you modify or redistribute, **keep the copyright / credit** (file headers and this notice).

使ってくれたら [X @UnagiTech](https://x.com/UnagiTech) をフォロー／作品にタグ付けしてくれると嬉しいです（お願いであり、商用の条件ではありません）。

If you use it, a follow or tag of [@UnagiTech](https://x.com/UnagiTech) on X is appreciated (request only — not a commercial-use condition).

## Credits

Created and distributed by **Unagi Tech Inc.**（株式会社うなぎテック）
