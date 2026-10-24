# Credits

## CT imaging — KU Leuven cadaveric wrist dataset, specimen 1

**Adapted from:** Quintiens J, et al. *Multimodal CT dataset of cadaveric wrist joints.*
KU Leuven Research Data Repository (RDR), 2024. https://doi.org/10.48804/DWF4RG

- Specimen 1 (`2701230006`), photon-counting CT “scan 1” (Siemens NAEOTOM Alpha, 0.110 mm pixels, 0.1 mm slice step).
- Licence: **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)** —
  https://creativecommons.org/licenses/by-sa/4.0/ . Commercial use is allowed with attribution, a link to the
  licence, an indication of changes, and adapted material shared under the same licence.
- The DICOM header's patient-name field holds a person's name; nothing from the headers is used in this simulator.

### Changes made

1. The volume was resampled to 0.22 mm (2 × 2 × 2 binning).
2. **Scanograms** (`scout_ap`, `scout_lat`) are simulated line-integral projections through that volume — not
   acquired localisers — padded with air to 180 mm wide and teal-tinted to match the sibling sims.
3. **Axial images** are 0.6 mm slabs every 1.5 mm (144 images); **coronal and sagittal reformats** are 0.6 mm slabs
   every 1.5 mm at 0.3 mm pixels; all re-encoded as 8-bit JPEG with a piecewise HU mapping.
4. In the browser the images are cropped and resampled to the chosen DFOV, blurred (0.55 mm gaussian) to simulate a
   soft-tissue kernel, and averaged / smeared along the forearm to simulate thicker slices.
5. **Laterality:** the dataset lists specimen 1 as a right wrist; its anatomy (and rigid registration with the
   HR-pQCT scan of the same specimen) is that of a left wrist, which is how it is presented here.
6. A cadaveric donor scan is presented as a teaching patient. No fracture is marked in the source dataset.
7. The tissue outline used to judge DFOV clipping ignores a cable tie / strap attached to the specimen.
8. If the arm-by-the-side position is chosen, streak artefacts and noise are added to the images in the browser to
   simulate the torso being in the beam — they are not present in the acquired data.

This adaptation (the images in `assets/` and the inlined pages) is shared under **CC BY-SA 4.0**.
Neither the dataset authors nor KU Leuven endorse this simulator.

## Other artwork

- Patient-positioning scene (CT room, three selectable patient positions, head-first table movement, lasers): original 3-D
  scene built procedurally for this project in `room3d.js` — no third-party models, photos or textures. A simpler
  original SVG drawing is the fallback if WebGL or the CDN is unavailable.
- 3-D rendering: [three.js](https://threejs.org) r160 (MIT licence, (c) three.js authors), loaded at runtime from
  https://cdn.jsdelivr.net/npm/three@0.160.0/.
- Rad-Lad logo: property of Rad-Lad.
