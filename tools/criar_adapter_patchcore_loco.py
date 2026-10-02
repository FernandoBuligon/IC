#!/usr/bin/env python3

from pathlib import Path
import os

import shutil

import numpy as np
from PIL import Image

IC_ROOT = Path(os.environ.get("IC_ROOT", Path(__file__).resolve().parents[1]))


SOURCE = IC_ROOT / "datasets/mvtec_loco_ad"
TARGET = IC_ROOT / "datasets/mvtec_loco_patchcore_adapter"

CATEGORIES = [
    "breakfast_box",
    "juice_bottle",
    "pushpins",
    "screw_bag",
    "splicing_connectors",
]

ANOMALY_TYPES = [
    "logical_anomalies",
    "structural_anomalies",
]


def make_symlink(source: Path, target: Path):
    if target.exists() or target.is_symlink():
        target.unlink()

    target.symlink_to(source, target_is_directory=True)


def combine_masks(mask_dir: Path) -> np.ndarray:
    mask_files = sorted(mask_dir.glob("*.png"))

    if not mask_files:
        raise RuntimeError(f"Nenhuma máscara em {mask_dir}")

    combined = None

    for mask_file in mask_files:
        with Image.open(mask_file) as img:
            arr = np.asarray(img)

        if arr.ndim != 2:
            raise RuntimeError(
                f"Máscara não é 2D: {mask_file} -> {arr.shape}"
            )

        current = arr > 0

        if combined is None:
            combined = current
        else:
            if current.shape != combined.shape:
                raise RuntimeError(
                    f"Shapes incompatíveis em {mask_dir}"
                )
            combined |= current

    return (combined.astype(np.uint8) * 255)


def main():
    if TARGET.exists():
        shutil.rmtree(TARGET)

    TARGET.mkdir(parents=True)

    print("Origem :", SOURCE)
    print("Adapter:", TARGET)
    print()

    for category in CATEGORIES:
        print("=" * 60)
        print(category)
        print("=" * 60)

        src_cat = SOURCE / category
        dst_cat = TARGET / category

        dst_cat.mkdir(parents=True)

        # Imagens não são copiadas.
        make_symlink(
            src_cat / "train",
            dst_cat / "train",
        )

        make_symlink(
            src_cat / "test",
            dst_cat / "test",
        )

        # Apenas para deixar o adapter completo.
        make_symlink(
            src_cat / "validation",
            dst_cat / "validation",
        )

        gt_target = dst_cat / "ground_truth"
        gt_target.mkdir()

        for anomaly_type in ANOMALY_TYPES:
            src_gt = src_cat / "ground_truth" / anomaly_type
            dst_gt = gt_target / anomaly_type
            dst_gt.mkdir()

            image_dirs = sorted(
                p for p in src_gt.iterdir()
                if p.is_dir()
            )

            for image_dir in image_dirs:
                combined = combine_masks(image_dir)

                output = dst_gt / f"{image_dir.name}.png"

                Image.fromarray(combined).save(output)

            test_count = len(
                list(
                    (src_cat / "test" / anomaly_type)
                    .glob("*.png")
                )
            )

            mask_count = len(
                list(dst_gt.glob("*.png"))
            )

            print(
                f"{anomaly_type:22s}: "
                f"test={test_count:3d} "
                f"masks={mask_count:3d}"
            )

            if test_count != mask_count:
                raise RuntimeError(
                    f"Contagem incompatível em "
                    f"{category}/{anomaly_type}"
                )

        print()

    print("Adapter criado com sucesso.")


if __name__ == "__main__":
    main()
