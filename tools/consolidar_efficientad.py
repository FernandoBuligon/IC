#!/usr/bin/env python3

import csv
import json
import re
from pathlib import Path
import os

IC_ROOT = Path(os.environ.get("IC_ROOT", Path(__file__).resolve().parents[1]))

RESULT_ROOT = IC_ROOT / "results/efficientad"
LOG_ROOT = IC_ROOT / "logs/experiments"

OUTPUT_CSV = RESULT_ROOT / "efficientad_mvtec_ad_results.csv"
OUTPUT_SUMMARY = RESULT_ROOT / "efficientad_mvtec_ad_summary.txt"


def flatten_json(obj, prefix=""):
    result = {}

    if isinstance(obj, dict):
        for key, value in obj.items():
            new_key = f"{prefix}.{key}" if prefix else str(key)
            result.update(flatten_json(value, new_key))

    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            new_key = f"{prefix}[{i}]"
            result.update(flatten_json(value, new_key))

    else:
        result[prefix] = obj

    return result


def normalize_key(key):
    return (
        key.lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace(".", " ")
    )


def find_metric(flat, kind):
    candidates = []

    for key, value in flat.items():
        if not isinstance(value, (int, float)):
            continue

        k = normalize_key(key)

        if kind == "aupro":
            if "pro" in k and (
                "auc" in k
                or "area" in k
                or "au pro" in k
            ):
                candidates.append((key, float(value)))

        elif kind == "image_auroc":
            if "roc" in k:
                if (
                    "image" in k
                    or "classification" in k
                    or "image level" in k
                ):
                    candidates.append((key, float(value)))

    if candidates:
        return candidates[0][1], candidates[0][0]

    # Fallbacks
    if kind == "aupro":
        for key, value in flat.items():
            if isinstance(value, (int, float)):
                if "pro" in normalize_key(key):
                    return float(value), key

    if kind == "image_auroc":
        for key, value in flat.items():
            if isinstance(value, (int, float)):
                k = normalize_key(key)
                if "roc" in k and "pixel" not in k:
                    return float(value), key

    return None, None


def extract_runtime(category):
    possible_logs = []

    if category == "bottle":
        possible_logs.append(LOG_ROOT / "EA-002-console.log")
    else:
        possible_logs.append(LOG_ROOT / f"EA003_{category}.log")

    for path in possible_logs:
        if not path.exists():
            continue

        text = path.read_text(errors="ignore")

        matches = re.findall(
            r"^real\s+(\d+)m([\d.,]+)s",
            text,
            flags=re.MULTILINE
        )

        if matches:
            minutes, seconds = matches[-1]
            seconds = float(seconds.replace(",", "."))

            total_seconds = int(minutes) * 60 + seconds
            return total_seconds

    return None


def format_runtime(seconds):
    if seconds is None:
        return ""

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60

    if hours:
        return f"{hours}h {minutes:02d}m {secs:04.1f}s"

    return f"{minutes}m {secs:04.1f}s"


rows = []

metric_files = sorted(
    RESULT_ROOT.glob(
        "EA*_*/metrics/mvtec_ad/metrics.json"
    )
)

for metrics_path in metric_files:
    run_name = metrics_path.parents[2].name

    match = re.match(
        r"EA\d+_(.+?)_(?:full|smoke)$",
        run_name
    )

    if not match:
        print("Ignorando:", run_name)
        continue

    category = match.group(1)

    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    flat = flatten_json(metrics)

    image_auroc, image_key = find_metric(
        flat, "image_auroc"
    )

    aupro, aupro_key = find_metric(
        flat, "aupro"
    )

    runtime_seconds = extract_runtime(category)

    rows.append(
        {
            "category": category,
            "image_auroc": image_auroc,
            "aupro_0.3": aupro,
            "runtime_seconds": runtime_seconds,
            "runtime": format_runtime(runtime_seconds),
            "_image_key": image_key,
            "_aupro_key": aupro_key,
        }
    )


order = [
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

order_map = {
    category: i
    for i, category in enumerate(order)
}

rows.sort(
    key=lambda x: order_map.get(
        x["category"], 999
    )
)


missing = set(order) - {
    row["category"] for row in rows
}

if missing:
    print(
        "ATENÇÃO: categorias ausentes:",
        sorted(missing)
    )


valid_image = [
    row["image_auroc"]
    for row in rows
    if row["image_auroc"] is not None
]

valid_aupro = [
    row["aupro_0.3"]
    for row in rows
    if row["aupro_0.3"] is not None
]

valid_runtime = [
    row["runtime_seconds"]
    for row in rows
    if row["runtime_seconds"] is not None
]


mean_image = (
    sum(valid_image) / len(valid_image)
    if valid_image else None
)

mean_aupro = (
    sum(valid_aupro) / len(valid_aupro)
    if valid_aupro else None
)

total_runtime = (
    sum(valid_runtime)
    if valid_runtime else None
)


with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow(
        [
            "category",
            "image_auroc",
            "aupro_fpr_0.3",
            "runtime_seconds",
            "runtime",
        ]
    )

    for row in rows:
        writer.writerow(
            [
                row["category"],
                (
                    f'{row["image_auroc"]:.6f}'
                    if row["image_auroc"] is not None
                    else ""
                ),
                (
                    f'{row["aupro_0.3"]:.6f}'
                    if row["aupro_0.3"] is not None
                    else ""
                ),
                (
                    f'{row["runtime_seconds"]:.3f}'
                    if row["runtime_seconds"] is not None
                    else ""
                ),
                row["runtime"],
            ]
        )

    writer.writerow(
        [
            "Mean",
            (
                f"{mean_image:.6f}"
                if mean_image is not None
                else ""
            ),
            (
                f"{mean_aupro:.6f}"
                if mean_aupro is not None
                else ""
            ),
            "",
            "",
        ]
    )


summary = []

summary.append(
    "EfficientAD-M — MVTec AD"
)

summary.append(
    "=" * 60
)

summary.append("")

summary.append(
    f"Categorias avaliadas: {len(rows)}"
)

if mean_image is not None:
    summary.append(
        f"Mean Image AUROC: {mean_image:.6f}"
    )

if mean_aupro is not None:
    summary.append(
        f"Mean AU-PRO @ FPR<=0.3: {mean_aupro:.6f}"
    )

if total_runtime is not None:
    summary.append(
        "Tempo acumulado de treinamento: "
        + format_runtime(total_runtime)
    )

summary.append("")
summary.append("Resultados por categoria:")
summary.append("")

for row in rows:
    image_text = (
        f'{row["image_auroc"]:.4f}'
        if row["image_auroc"] is not None
        else "N/A"
    )

    aupro_text = (
        f'{row["aupro_0.3"]:.4f}'
        if row["aupro_0.3"] is not None
        else "N/A"
    )

    summary.append(
        f'{row["category"]:12s} '
        f'Image AUROC={image_text} '
        f'AU-PRO={aupro_text} '
        f'Tempo={row["runtime"]}'
    )


OUTPUT_SUMMARY.write_text(
    "\n".join(summary)
)


print()
print("\n".join(summary))
print()
print("CSV:")
print(OUTPUT_CSV)
print()
print("Resumo:")
print(OUTPUT_SUMMARY)

print()
print("Chaves detectadas:")
for row in rows[:3]:
    print(
        row["category"],
        "| Image:",
        row["_image_key"],
        "| AU-PRO:",
        row["_aupro_key"],
    )
