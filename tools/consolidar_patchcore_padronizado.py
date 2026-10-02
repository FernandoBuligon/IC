#!/usr/bin/env python3

import csv
import json
from pathlib import Path
import os

IC_ROOT = Path(os.environ.get("IC_ROOT", Path(__file__).resolve().parents[1]))


ROOT = (
    IC_ROOT / "results/patchcore/standardized_eval"
)

METRICS = ROOT / "metrics"

OUTPUT = (
    ROOT /
    "patchcore_mvtec_ad_standardized.csv"
)

CATEGORIES = [
    "bottle",
    "cable",
    "capsule",
    "carpet",
    "grid",
    "hazelnut",
    "leather",
    "metal_nut",
    "pill",
    "screw",
    "tile",
    "toothbrush",
    "transistor",
    "wood",
    "zipper",
]


def flatten(obj, prefix=""):
    result = {}

    if isinstance(obj, dict):
        for key, value in obj.items():
            name = (
                f"{prefix}.{key}"
                if prefix
                else str(key)
            )

            result.update(
                flatten(value, name)
            )

    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            result.update(
                flatten(
                    value,
                    f"{prefix}[{i}]",
                )
            )

    else:
        result[prefix] = obj

    return result


def find_metrics(data):
    flat = flatten(data)

    image_auc = None
    aupro = None

    for key, value in flat.items():
        if not isinstance(
            value,
            (int, float),
        ):
            continue

        k = key.lower()

        if (
            aupro is None
            and "pro" in k
            and (
                "auc" in k
                or "area" in k
                or "au" in k
            )
        ):
            aupro = float(value)

        if (
            image_auc is None
            and "roc" in k
            and (
                "image" in k
                or "classification" in k
            )
        ):
            image_auc = float(value)

    return image_auc, aupro


rows = []

for category in CATEGORIES:
    path = (
        METRICS /
        category /
        "metrics.json"
    )

    if not path.exists():
        raise FileNotFoundError(path)

    data = json.loads(
        path.read_text()
    )

    image_auc, aupro = find_metrics(
        data
    )

    rows.append(
        {
            "category": category,
            "image_auroc": image_auc,
            "aupro_fpr_0.3": aupro,
        }
    )


mean_image = sum(
    row["image_auroc"]
    for row in rows
) / len(rows)

mean_aupro = sum(
    row["aupro_fpr_0.3"]
    for row in rows
) / len(rows)


with open(
    OUTPUT,
    "w",
    newline="",
) as f:

    writer = csv.writer(f)

    writer.writerow(
        [
            "category",
            "image_auroc",
            "aupro_fpr_0.3",
        ]
    )

    for row in rows:
        writer.writerow(
            [
                row["category"],
                f'{row["image_auroc"]:.6f}',
                f'{row["aupro_fpr_0.3"]:.6f}',
            ]
        )

    writer.writerow(
        [
            "Mean",
            f"{mean_image:.6f}",
            f"{mean_aupro:.6f}",
        ]
    )


print()
print("PatchCore — avaliação padronizada")
print("=" * 50)

for row in rows:
    print(
        f'{row["category"]:12s} '
        f'Image AUROC='
        f'{row["image_auroc"]:.4f} '
        f'AU-PRO='
        f'{row["aupro_fpr_0.3"]:.4f}'
    )

print()
print(
    f"Mean Image AUROC: "
    f"{mean_image:.6f}"
)

print(
    f"Mean AU-PRO: "
    f"{mean_aupro:.6f}"
)

print()
print("CSV:")
print(OUTPUT)
