from pathlib import Path
import os

import hashlib

import numpy as np
import tifffile
from PIL import Image

IC_ROOT = Path(os.environ.get("IC_ROOT", Path(__file__).resolve().parents[1]))


DATASET_TEST = (
    IC_ROOT / "datasets/mvtec_loco_ad/breakfast_box/test"
)

OUTPUT_TEST = (
    IC_ROOT / "results/loco_eval_smoke/anomaly_maps/breakfast_box/test"
)

VALID_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}

def stable_seed(relative_path):
    digest = hashlib.md5(str(relative_path).encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


count = 0

for defect_type in [
    "good",
    "logical_anomalies",
    "structural_anomalies",
]:
    input_dir = DATASET_TEST / defect_type
    output_dir = OUTPUT_TEST / defect_type
    output_dir.mkdir(parents=True, exist_ok=True)

    images = sorted(
        p for p in input_dir.iterdir()
        if p.is_file() and p.suffix.lower() in VALID_EXTENSIONS
    )

    for image_path in images:
        with Image.open(image_path) as img:
            width, height = img.size

        relative_path = image_path.relative_to(DATASET_TEST)

        rng = np.random.RandomState(stable_seed(relative_path))

        # Mapa sintético apenas para validar o avaliador.
        anomaly_map = rng.random_sample((height, width)).astype(np.float32)

        output_path = output_dir / f"{image_path.stem}.tiff"

        tifffile.imwrite(
            str(output_path),
            anomaly_map,
        )

        count += 1

    print(
        f"{defect_type:22s}: "
        f"{len(images):3d} anomaly maps gerados"
    )

print()
print(f"TOTAL: {count} anomaly maps")
print(f"Saída: {OUTPUT_TEST}")
