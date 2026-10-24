# The Scanogram — CT Wrist

An embeddable, single-file teaching simulator for the Rad-Lad website. Part of the
"Scanogram" family (circle of Willis, carotid, hand, knee, T-spine, CTPA). Marker: **Superman Scanned**.

## Flow

1. **Patient set-up** — the patient arrives supine with the arms by the side; choose how they should lie
   for a CT of the **left** wrist: prone with the arm overhead (the “superman” position, correct), supine with
   the arm overhead (acceptable fall-back, part marks) or supine with the arm by the side (no marks).
   The 3-D room (`room3d.js`, three.js from jsDelivr; falls back to an SVG drawing) shows the chosen pose
   straight away and the choice can be changed until `load`, but only the **first** pick is graded.
   `load` moves the table head first to the lasers and then to the scan position for that pose — with the
   arm by the side the head and chest pass right through the gantry to bring the wrist into the scan plane,
   and the review images then carry simulated beam-hardening streaks and noise.
2. **Scanogram** — PA + lateral localisers (`scout`).
3. **Range + DFOV** — one box on the PA scanogram: its height is the scan range, its width the display
   FOV (square, 512 matrix; the lateral inset shows the depth it covers).
   Ideal: metacarpal bases (≥ 10 mm beyond the CMC joints, not into the fingers) → DRUJ / distal radial
   metaphysis (≥ 25 mm proximal to the radiocarpal joint); DFOV snug to the wrist with no clipping
   (≈ 90–115 mm here).
4. **Reconstruction** — kernel (bone / soft tissue) and slice thickness (0.6 / 3 / 5 mm), with a live
   preview of the carpus.
5. **Review** — axial, coronal and sagittal images rendered in the browser for the chosen range, DFOV,
   kernel and thickness, BONE / SOFT TISSUE windows, coronal hero image and a % score:
   position 15 · distal limit 15 · proximal limit 15 · dose/range 10 · DFOV 25 · kernel 10 · thickness 10.

## Files

- `wrist.embed.html` — self-contained deliverable (~7.7 MB, every image inlined); `index.html` = identical copy for one-drop hosting
- `wrist.html` — source (loads `./assets/`, `assets/calib.js`, `room3d.js`); `python inline.py` rebuilds both
- `room3d.js` — procedural three.js CT room, prone superman pose. Bump `?v=N` in `wrist.html` **and** `inline.py` together.
- `assets/` — `scout_ap/lat`, `ax_000…143` (0.6 mm axial slabs every 1.5 mm, HU-encoded JPEG),
  `cor_NN` / `sag_NN` (0.6 mm reformat slabs every 1.5 mm), `calib.json` / `calib.js` (geometry, per-slice
  tissue outline for DFOV clipping, landmarks), logos
- `tools/gen_assets.py` — rebuilds every image from the source volume (see CREDITS.md)

Debug hooks: `window.__scg` (`parse(cmd)`, `setBox({x0,x1,y0,y1})`, `computeScore()`, `clip()`),
`window.__room()` (`pose(0|2|3)`, `cam([p],[t])`).

## Licence

The imaging is adapted from a **CC BY-SA 4.0** dataset, so the adapted images (everything in `assets/`
and the inlined pages) are shared under **CC BY-SA 4.0** — see CREDITS.md.
