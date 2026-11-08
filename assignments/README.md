# Cloud City v3

CDF Assignment 01 — **Bauhaus 3D Composition**. A floating city with one continuous **Form 0–1** driver, a twisted central tower, seeded satellite cities and automatic bridges. The crown language is deliberately restrained: **flat crystal caps + floating halo orbs, no upward spikes**.

## Open and edit

1. Keep `assignments/` and `src/` in this folder.
2. In Rhino 8, open Grasshopper and load `assignments/assignment-01.gh` (or `.ghx`).
3. Let the Python 3 component finish its first initialization.
4. The component finds `src/cdf/geometry_basics.py` automatically; no personal path is required.
5. Adjust the twelve sliders. The saved default is **variant 02** (Form 0.50, 7 levels, 7 satellites).
6. Edit `create_sky_city` in `src/cdf/geometry_basics.py` and recompute to reload the source.

## What is different from v2

- `Style` (0/1/2) is replaced by one continuous **`Form` 0–1**: opening aspect, top/bottom exponents, lobes, plan roundness, twist, lean, vertical slot, crown height/flare all interpolate.
- **Void ratio** scales the opening in every form: `a = w * (0.07 + 0.32 * void_ratio / 0.70)`. It is no longer clamped to one form.
- The main crown is a **flat crystal eave + floating halo orb**; satellites and side towers get **flat crystal caps + orbs**. The spire satellite type and the thin crystal blades are removed.
- The tower body is a twisted, leaning rounded-square stack; the top two bays stay whole so no thin slit remainders appear above the roof.
- Horizontal mullions, terrace vines and floating debris from the study are removed; one vertical mullion remains per opening.

## Files

| Path | Content |
|---|---|
| `assignments/assignment-01.gh` | Binary Grasshopper definition, 12 sliders + Python 3 + Custom Preview |
| `assignments/assignment-01.ghx` | XML version of the same definition |
| `src/cdf/geometry_basics.py` | Course geometry functions + `create_cloud_city_v2` + `create_sky_city` |
| `models/01_compact.3dm` | Form 0.12, 354 closed Breps |
| `models/02_perforated.3dm` | Form 0.50, 525 closed Breps |
| `models/03_split.3dm` | Form 0.88, 418 closed Breps |
| `models/Cloud_City_v3.3dm` | Default (02) model |
| `renders/01_compact.png` | 1200 × 1200 viewport render |
| `renders/02_perforated.png` | 1200 × 1200 viewport render |
| `renders/03_split.png` | 1200 × 1200 viewport render |
| `renders/contact_sheet.png` | Three variants side by side |
| `renders/void_study.png` | Same Form 0.50 at void 0.25 / 0.45 / 0.65 |
| `renders/Cloud_City_v3_dynamic.gif` | 4.7 s dynamic GIF: Form 0→1 continuous, then Void 0.20→0.37; GH sliders move with the model; 1280×720, 12 fps, 56 frames |
| `renders/Cloud_City_v3_transformations_poster.png` | 1920×1080 poster frame (02 Perforated) |
| `Cloud_City_v3.pdf` | One-page template PDF (GIF shows its first frame) |
| `Cloud_City_v3.pptx` | 1 slide, template layout: parameters + relationships + large dynamic GIF + 01/02 cards |
| `parameters/controls.json` | Control ranges, defaults and descriptions |
| `parameters/presets.json` | Exact values of the three variants |
| `validation.json` | Rhino/Grasshopper checks and counts |

## The twelve controls

| # | Control | Range | Default | Drives |
|---|---|---|---|---|
| 1 | Form | 0–1 | 0.50 | Continuous arch → oculus → split/bloom; tower section, twist, lean, slot, crown cap |
| 2 | Main levels | 3–9 | 7 | Main tower height, opening rhythm and crown position |
| 3 | Void ratio | 0.20–0.70 | 0.55 | Opening width/height in every form |
| 4 | Satellite count | 0–8 | 7 | Number of satellite cities; ring radius follows |
| 5 | Seed | 0–999 | 24 | Opening sequence, satellite angles, radii, heights and sizes |
| 6 | Island depth | 0.6–1.6 | 1.00 | Taper depth of the floating island bases |
| 7 | Ring radius | 13–32 | 24 | Satellite distance and bridge length |
| 8 | Satellite size | 0.40–1.00 | 0.70 | Satellite footprint/height; bridge width follows |
| 9 | Height variation | 0–1 | 0.65 | Vertical scatter of satellite roofs and bridge slopes |
| 10 | Bridge width | 0.5–1.6 | 0.90 | Bridge width multiplier |
| 11 | Detail | 0–2 | 2 | Roots/orbs/waterfalls |
| 12 | Model scale | 0.5–2.0 | 1.00 | Uniform scale of the whole composition |

## Variants

| | 01 Compact | 02 Perforated | 03 Split |
|---|---|---|---|
| Form | 0.12 | 0.50 | 0.88 |
| Main levels | 4 | 7 | 6 |
| Void ratio | 0.45 | 0.55 | 0.55 |
| Satellite count | 4 | 7 | 5 |
| Ring radius | 18 | 24 | 21 |
| Satellite size | 0.90 | 0.70 | 0.80 |
| Height variation | 0.25 | 0.65 | 0.90 |
| Seed | 12 | 24 | 36 |
| Bridge width | 1.10 | 0.90 | 1.10 |
| Island depth | 0.95 | 1.00 | 1.15 |
| Detail | 2 | 2 | 2 |
| Model scale | 1.00 | 1.00 | 1.00 |

## Checks

- Rhino 8 / Grasshopper 8, Python 3 component and RhinoCommon geometry; no additional plug-ins.
- The integrated `.ghx` solves with 20 objects, **539 geometry / 539 colours, 0 errors / 0 warnings** in the validation session. A fresh open imports the current module; the 3dm/render counts are 354 / 525 / 418 (a few boolean slivers are filtered from the confirmed models).
- All four `.3dm` files reopen in Rhino as metres, one layer, with the expected counts.
- `Cloud_City_v3.pdf` and `Cloud_City_v3.pptx` are both one page, following the `CC_V1/Cloud_City_Assignment1_Template.pdf` layout. The large center panel is the dynamic model GIF; it animates in PowerPoint slideshow, while the PDF shows its first frame. The full version with the GH panel remains `renders/Cloud_City_v3_dynamic.gif`; the square model crop used on the slide is `renders/Cloud_City_v3_dynamic_model.gif`.
- `renders/Cloud_City_v3_dynamic.gif` is 56 frames / 4.7 s / 1280×720 / 12 fps / ~7 MB. It is a continuous process, not a state slideshow: Form 0→1 then Void 0.20→0.37, with the GH-style slider panel moving in sync; model is centered on a white/clay (Arctic-style) background.

## Note on the brief

The Moodle brief was not inside the supplied folder. The requirements were reconstructed from the course slides `02_1 Computational Geometry Examples.pdf` (Assignment 1 — Bauhaus 3D Composition; feedback 02.11.2026; second submission 09.11.2026; one slide with parametric variations + parameter explanation; Grasshopper + src code via GitHub). The floating-city programme is the design concept, not an additional course requirement.

## 中文简注

- `CC_V3` 是新的连续形态版本；`CC_V2` 是上一版，保留未动。
- 顶部已彻底去掉尖刺：主城是平晶檐口 + 悬浮光环；卫星/侧塔是平晶帽 + 金球。
- GH 默认 02；把 `Form` 从 0 拖到 1 即可看到连续变化，`Void ratio` 在所有形态下都放大/缩小开口。
