"""Build every image asset for the CT wrist simulator from the spec1 photon-counting CT.

Source: D:\\Prometheus\\CT\\Wrist\\Patient 1\\PCCT scan1 (Quintiens et al. 2024, KU Leuven RDR,
doi:10.48804/DWF4RG, CC BY-SA 4.0; Siemens NAEOTOM Alpha, 0.110 mm px, 0.1 mm step), read through
the 2x2x2-binned HU volume ..\\scanogram\\work\\pcct2x.npy (0.2207 mm px, 0.2 mm step, slice 0 = proximal)
made by scanogram\\load_pcct.py.  Anatomically a LEFT wrist (see the DICOM README there).

Outputs (../assets):
  scout_ap.jpg, scout_lat.jpg  - simulated PA + lateral topograms (line integrals through the volume),
                                 0.3 mm px, distal (fingers) at the top, padded with air to SCOUT_W_MM wide,
                                 teal-tinted like the sibling sims.  PA: radius on the viewer's right.
                                 LAT: volar on the left.
  ax_NNN.jpg   - 0.6 mm axial slabs every 1.5 mm from distal to proximal, 512 x 512 native grid,
                 HU encoded with the piecewise HU_LUT so the browser can window / filter them.
  cor_NN.jpg   - 0.6 mm coronal slabs every 1.5 mm through the limb, 0.3 mm px, same frame as the PA scout.
  sag_NN.jpg   - 0.6 mm sagittal slabs every 1.5 mm across the limb, 0.3 mm px, volar on the left.
  calib.json   - geometry, per-slice tissue extents (for DFOV clipping), landmarks.

Run:  python -I gen_assets.py     (needs numpy, opencv-python)
"""
import os, json
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
VOL = r"D:\Prometheus\CT\Wrist\Patient 1\scanogram\work\pcct2x.npy"
OUT = os.path.join(HERE, "..", "assets")
SP, DZ = 0.220704, 0.2           # binned voxel (mm): in-plane, z
PX = 0.3                         # scout / MPR pixel (mm)
STEP = 1.5                       # review interval (mm)
SCOUT_W_MM = 180.0               # topogram width shown (the PCCT field is only 113 mm; the rest is air)
HU_LUT = [(-1000, 0), (-200, 40), (300, 140), (2400, 255)]
MU = 0.0192 / 1000               # water ~0.0192 /mm at 120 kV

# landmarks, mm from the distal (top) edge of the scout - read off a bone MIP with a mm ruler
LANDMARKS = {"mcp": 82, "mc_heads_top": 75, "cmc": 130, "carpus_mid": 152, "rc_joint": 170,
             "druj_lo": 195}


def hu_to_byte(h):
    xs = [p[0] for p in HU_LUT]; ys = [p[1] for p in HU_LUT]
    return np.clip(np.rint(np.interp(h, xs, ys)), 0, 255).astype(np.uint8)


def tint(g):
    g = g.astype(np.float32) / 255
    return (np.stack([g * .95, g * .97, g * .78], -1) * 255).astype(np.uint8)   # BGR for cv2 (= RGB .78/.97/.95)


def body_mask(sl):
    m = (sl > -350).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros_like(m)
    big = st[1:, cv2.CC_STAT_AREA].max() if n > 1 else 0
    for i in range(1, n):                     # limb pieces (fingers count); drops straps and ties
        if st[i, cv2.CC_STAT_AREA] >= max(300, 0.15 * big):
            keep[lab == i] = 1
    return keep


def main():
    os.makedirs(OUT, exist_ok=True)
    v = np.load(VOL, mmap_mode="r")
    nz, ny, nx = v.shape
    field = nx * SP
    pad_mm = (SCOUT_W_MM - field) / 2
    H_MM = nz * DZ

    # ---- topograms ----
    pa = np.zeros((nz, nx), np.float32); lat = np.zeros((nz, ny), np.float32)
    ymin, ymax, xmin, xmax = ny, 0, nx, 0
    masks = {}
    for z0 in range(0, nz, 64):
        a = np.asarray(v[z0:z0 + 64]).astype(np.float32)
        mu = np.maximum(a + 1000, 0) * MU
        pa[z0:z0 + 64] = mu.sum(1) * SP
        lat[z0:z0 + 64] = mu.sum(2) * SP

    def topo(p, flip):
        img = p[::-1]
        if flip:
            img = img[:, ::-1]
        h, w = img.shape
        img = cv2.resize(img, (int(round(w * SP / PX)), int(round(h * DZ / PX))), interpolation=cv2.INTER_AREA)
        img = cv2.GaussianBlur(img, (0, 0), 0.6)
        rng = np.random.default_rng(7)
        img = img + rng.normal(0, 0.012, img.shape).astype(np.float32) * np.sqrt(np.maximum(img, 0.05))
        hi = np.percentile(img, 99.7)
        out = (np.clip(img / hi, 0, 1) ** 0.85 * 255).astype(np.uint8)
        padpx = int(round(pad_mm / PX))
        out = cv2.copyMakeBorder(out, 0, 0, padpx, padpx, cv2.BORDER_CONSTANT, value=0)
        return tint(out)

    cv2.imwrite(os.path.join(OUT, "scout_ap.jpg"), topo(pa, False), [cv2.IMWRITE_JPEG_QUALITY, 88])
    cv2.imwrite(os.path.join(OUT, "scout_lat.jpg"), topo(lat, True), [cv2.IMWRITE_JPEG_QUALITY, 88])

    # ---- axial slabs, distal -> proximal ----
    ax = []
    k = 0
    while True:
        ztop = STEP / 2 + STEP * k                 # mm from the distal edge
        if ztop > H_MM - 0.4:
            break
        zi = int(round(nz - 1 - ztop / DZ))        # volume index (0 = proximal)
        sl = np.asarray(v[max(0, zi - 1):zi + 2]).astype(np.float32).mean(0)
        cv2.imwrite(os.path.join(OUT, f"ax_{k:03d}.jpg"), hu_to_byte(sl), [cv2.IMWRITE_JPEG_QUALITY, 88])
        m = body_mask(np.asarray(v[zi]).astype(np.float32))
        ys, xs = np.nonzero(m)
        if len(xs):
            e = [round(pad_mm + xs.min() * SP, 1), round(pad_mm + (xs.max() + 1) * SP, 1),
                 round(ys.min() * SP, 1), round((ys.max() + 1) * SP, 1)]
            ymin, ymax = min(ymin, ys.min()), max(ymax, ys.max())
            xmin, xmax = min(xmin, xs.min()), max(xmax, xs.max())
        else:
            e = None
        ax.append({"z": round(ztop, 2), "ext": e})
        k += 1
    # smooth the outline along z (running median over 5 slices) so stray specks do not drive DFOV clipping
    E = np.array([a["ext"] for a in ax], float)
    for i in range(len(ax)):
        ax[i]["ext"] = [round(float(x), 1) for x in np.median(E[max(0, i - 2):i + 3], axis=0)]
    print("axial", len(ax))

    # ---- coronal (across AP depth) and sagittal (across width) slabs through the limb ----
    def resample(img):
        h, w = img.shape
        return cv2.resize(img, (int(round(w * SP / PX)), int(round(h * DZ / PX))), interpolation=cv2.INTER_AREA)

    cor_y, sag_x = [], []
    y_mm = ymin * SP
    i = 0
    while y_mm <= (ymax + 1) * SP:
        yi = int(round(y_mm / SP))
        sl = np.asarray(v[:, max(0, yi - 1):yi + 2, :]).astype(np.float32).mean(1)[::-1]
        cv2.imwrite(os.path.join(OUT, f"cor_{i:02d}.jpg"), hu_to_byte(resample(sl)), [cv2.IMWRITE_JPEG_QUALITY, 86])
        cor_y.append(round(y_mm, 2)); y_mm += STEP; i += 1
    x_mm = xmin * SP
    i = 0
    while x_mm <= (xmax + 1) * SP:
        xi = int(round(x_mm / SP))
        sl = np.asarray(v[:, :, max(0, xi - 1):xi + 2]).astype(np.float32).mean(2)[::-1, ::-1]   # volar (+y) left
        cv2.imwrite(os.path.join(OUT, f"sag_{i:02d}.jpg"), hu_to_byte(resample(sl)), [cv2.IMWRITE_JPEG_QUALITY, 86])
        sag_x.append(round(pad_mm + x_mm, 2)); x_mm += STEP; i += 1
    print("coronal", len(cor_y), "sagittal", len(sag_x))

    calib = {
        "source": "PCCT spec1 (Quintiens et al. 2024, doi:10.48804/DWF4RG, CC BY-SA 4.0), 2x binned",
        "sp": SP, "dz": DZ, "px": PX, "step": STEP, "field_mm": round(field, 3), "pad_mm": round(pad_mm, 3),
        "scout_w_mm": SCOUT_W_MM, "scout_h_mm": round(H_MM, 2), "img_w": nx, "hu_lut": HU_LUT,
        "landmarks": LANDMARKS, "ax": ax, "cor_y": cor_y, "sag_x": sag_x,
        "mpr_size": [int(round(nx * SP / PX)), int(round(nz * DZ / PX))],
    }
    with open(os.path.join(OUT, "calib.json"), "w") as f:
        json.dump(calib, f, separators=(",", ":"))
    with open(os.path.join(OUT, "calib.js"), "w") as f:          # loaded by wrist.html (inlined by inline.py)
        f.write("window.SCG_CALIB=" + json.dumps(calib, separators=(",", ":")) + ";\n")
    print("done", round(field, 1), "mm field, pad", round(pad_mm, 1))


if __name__ == "__main__":
    main()
