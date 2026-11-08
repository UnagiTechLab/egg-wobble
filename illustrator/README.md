# EggWobble for Adobe Illustrator

**Unagi Tech Inc.（株式会社うなぎテック）** · v1.2.0 · [MIT License](LICENSE)

Soft, low-frequency “fried egg” paths: wobble for the white, plus an offset yolk ellipse. Modeless palette — keep the panel open while you work in the document.

Released by Unagi Tech Inc. Related: physical goods (e.g. Luci Brasil) and print data on MakersLabo may use the same look; this package is the Illustrator tool only.

## Requirements

- Adobe Illustrator (ExtendScript / JSX)

Not affiliated with Adobe.

## Install / run

1. Open a document in Illustrator  
2. **File → Scripts → Other Script…** and choose `egg_wobble.jsx`  
   (or drag the file onto Illustrator / add it to your Scripts folder)

## Usage

| Button | Action |
|--------|--------|
| Create / Replace / Confirm | Row 1 (centered, equal width) — create → live → lock |
| Random / Reset / Close | Row 2 (centered, equal width) — shuffle / defaults / close |

Numeric fields use a slider plus an edit box. Live preview rebuilds the last egg (same flow as Maya).

Paths are normal Illustrator path items (group `eggWobble_seedN`). Edit with the Direct Selection tool (A).

## Parameters

| Control | Meaning | Tip |
|---------|---------|-----|
| Seed | Phase / shape variation | `7` is a good default |
| White radius (pt) | Egg-white size | |
| Wobble | Distortion (`0` = circle) | ~0.18–0.28 |
| Subdivs | Anchor count on the white | 64 is fine to start |
| Yolk radius / offset | Yolk size and position | |
| Stroke (pt) | Outline weight | |

Formula:

`r(θ) = R × (1 + wobble × (0.35 cos(2θ+φ₂) + 0.55 cos(3θ+φ₃) + 0.25 cos(4θ+φ₄)))`

## License

MIT — see [LICENSE](LICENSE).

You may use, copy, modify, and redistribute. If you modify or redistribute, **keep the copyright / credit** (file headers and this notice).

使ってくれたら [X @UnagiTech](https://x.com/UnagiTech) をフォロー／作品にタグ付けしてくれると嬉しいです（お願いであり、商用の条件ではありません）。

If you use it, a follow or tag of [@UnagiTech](https://x.com/UnagiTech) on X is appreciated (request only — not a commercial-use condition).

## Credits

Created and distributed by **Unagi Tech Inc.**（株式会社うなぎテック）
