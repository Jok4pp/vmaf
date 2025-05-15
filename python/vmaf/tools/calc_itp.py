import tifffile as tiff
import subprocess
from PIL import Image
import os
import numpy as np
from skimage.transform import resize
import colour as c
from colour.difference import delta_E_ITP
from colour import RGB_to_ICtCp

def load_hdr_pq_tiff(path: str) -> np.ndarray:
    """
    Lädt ein 16-Bit TIFF mit PQ EOTF (ST2084) und gibt normierte RGB-Werte [0,1] zurück.
    """
    try:
        data = tiff.imread(path).astype(np.float32)
        # print("ref (0,0):", data[0,0])
        return data / (2**16 - 1)
    except NotImplementedError:
        # TIFF uses chroma subsampling that tifffile cannot decode → fallback
        # print(f"⚠️  TIFF codec not supported for {path}, falling back to FFmpeg")
        # use PIL to read size
        img = Image.open(path)
        width, height = img.size
        # call ffmpeg to convert subsampled TIFF → raw 16-bit RGB
        cmd = [
            "ffmpeg", "-v", "error",
            "-i", path,
            "-pix_fmt", "rgb48le",
            "-f", "rawvideo", "-"
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
        arr = np.frombuffer(proc.stdout, dtype=np.uint16)
        arr = arr.reshape((height, width, 3))
        arr = arr.astype(np.float32)
        print("ref (0,0):", arr[0,0])
        return arr / 65535.0
def rgb_to_ictcp(lin_rgb: np.ndarray, peak_nits: float) -> np.ndarray:
    """
    Konvertiert normiertes RGB in ICtCp (PQ-EOTF intern).
    """
    return RGB_to_ICtCp(lin_rgb, method='ITU-R BT.2100-2 PQ', L_p=peak_nits)

def run_dEipt_folder_hdr(distorted_folder: str, reference_folder: str):
    """
    Vergleicht HDR-Kompression ohne GainMap anhand von DeltaE IPT.
    Referenzbilder → mehrere verzerrte Versionen pro Referenz.
    """
    peak_nits = 10000
    print(f"Compare '{distorted_folder}' with '{reference_folder}' for DeltaE IPT")

    # gather files
    files_ref = sorted([
        f for f in os.listdir(reference_folder)
        if f.lower().endswith(('.tif', '.tiff'))
    ])
    files_cmp = sorted([
        f for f in os.listdir(distorted_folder)
        if f.lower().endswith(('.tif', '.tiff'))
    ])

    results = {}  # map distorted-filename → ΔE_ITP
    for f_ref in files_ref:
        ref_base = os.path.splitext(f_ref)[0]
        # extract the “video ID” after the last underscore, e.g. “firework”
        video_id = ref_base.split('_')[-1]
        # find all distorted files whose base ends with that same ID
        matches = [f for f in files_cmp
                   if os.path.splitext(f)[0].split('_')[-1] == video_id]
        if not matches:
            print(f"⚠️  No distorted match for reference {f_ref}")
            continue

        # load reference once
        ref_path = os.path.join(reference_folder, f_ref)
        rgb_ref_orig = load_hdr_pq_tiff(ref_path)

        for f_cmp in matches:
            cmp_path = os.path.join(distorted_folder, f_cmp)
            rgb_cmp = load_hdr_pq_tiff(cmp_path)

            # resize reference to distorted resolution
            H, W, _ = rgb_cmp.shape
            rgb_ref = resize(
                rgb_ref_orig,
                (H, W, 3),
                preserve_range=True,
                order=1,
                anti_aliasing=True
            ).astype(np.float32)

            # Debug: raw PQ-encoded RGB
            print(f"ref={rgb_ref[0,0]}")

            # PQ-EOTF → linear RGB
            rgb_cmp_lin = c.eotf(rgb_cmp, function="ST 2084", L_p=peak_nits)
            rgb_ref_lin = c.eotf(rgb_ref, function="ST 2084", L_p=peak_nits)
            # Debug: linear RGB
            #print(f"[debug] After EOTF RGB    @ (0,0): ref={rgb_ref_lin[0,0]} cmp={rgb_cmp_lin[0,0]}")

            # ICtCp conversion
            ict_ref = RGB_to_ICtCp(rgb_ref_lin, method='ITU-R BT.2100-2 PQ', L_p=peak_nits)
            ict_cmp = RGB_to_ICtCp(rgb_cmp_lin, method='ITU-R BT.2100-2 PQ', L_p=peak_nits)
            # Debug: ICtCp
            #print(f"[debug] ICtCp         @ (0,0): ref={ict_ref[0,0]} cmp={ict_cmp[0,0]}")

            # ΔE_ITP
            delta = delta_E_ITP(ict_ref, ict_cmp)
            # Debug: per-pixel ΔE_ITP at (0,0)
            #print(f"[debug] ΔE_ITP pixel  @ (0,0): {delta[0,0]}")

            mean_delta = float(np.mean(delta))
            results[f_cmp] = mean_delta
            #print(f"{f_cmp}: ΔE_ITP={mean_delta:.4f}")

    return results

# Basis- und Dist-Ordner
dist_dir = r"LIVE-HDR_tiff/dis"
ref_dir  = r"LIVE-HDR_tiff/ref"

# Liste der Videos
# videos = [
#     "Bonfire", "CargoBoat", "CenterPanorama", "Chasing1",
#     "Chasing3", "Chasing4", "CourtYard", "Daylight1", "Furniture"
# ]

# videos = ["golf2", "Light2", "Light3", "Light4", "NighTraffic", "OfficeBuilding", "Porsche", "Skyscraper"]

# for video in videos:
#     ref_video  = os.path.join(ref_dir,  f"4k_ref_{video}")
#     dist_video = os.path.join(dist_dir, f"1080p_9M_{video}")
#     delta = run_dEipt_folder_hdr(dist_video, ref_video)
#     print(f"DeltaE IPT {os.path.basename(dist_video)}: {delta:.4f}")

# delta = run_dEipt_folder_hdr(dist_dir, ref_dir)
# #     print(f"DeltaE IPT {os.path.basename(dist_video)}: {delta:.4f}")", ref_video)
# print(f"DeltaE IPT: {delta:.4f}")

results = run_dEipt_folder_hdr(dist_dir, ref_dir)
for fname, d in results.items():
    print(f"{fname}: ΔE_ITP={d:.4f}")