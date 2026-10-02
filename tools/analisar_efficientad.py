#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tifffile
from PIL import Image
from sklearn.metrics import roc_auc_score


def normalize(x, minimum, maximum):
    if maximum <= minimum:
        return np.zeros_like(x, dtype=np.float32)

    return np.clip(
        (x.astype(np.float32) - minimum) /
        (maximum - minimum),
        0,
        1,
    )


def find_images(folder):
    extensions = {
        ".png", ".jpg", ".jpeg",
        ".bmp", ".tif", ".tiff"
    }

    return sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in extensions
    )


def save_visualization(
    record,
    global_map_min,
    global_map_max,
    output_path,
):
    image = np.asarray(
        Image.open(record["image_path"]).convert("RGB")
    )

    anomaly_map = tifffile.imread(
        record["map_path"]
    ).astype(np.float32)

    anomaly_map_vis = normalize(
        anomaly_map,
        global_map_min,
        global_map_max,
    )

    if record["is_anomaly"]:
        gt = np.asarray(
            Image.open(record["mask_path"]).convert("L")
        )
        gt = (gt > 0).astype(np.uint8)
    else:
        gt = np.zeros(
            image.shape[:2],
            dtype=np.uint8,
        )

    fig, axes = plt.subplots(
        1, 4,
        figsize=(13, 3.5),
    )

    axes[0].imshow(image)
    axes[0].set_title("Imagem")

    axes[1].imshow(
        gt,
        cmap="gray",
        vmin=0,
        vmax=1,
    )
    axes[1].set_title("Ground truth")

    axes[2].imshow(
        anomaly_map_vis,
        cmap="inferno",
        vmin=0,
        vmax=1,
    )
    axes[2].set_title("Anomaly map")

    axes[3].imshow(image)
    axes[3].imshow(
        anomaly_map_vis,
        cmap="inferno",
        alpha=0.45,
        vmin=0,
        vmax=1,
    )
    axes[3].set_title("Sobreposição")

    for ax in axes:
        ax.axis("off")

    if np.isnan(record["pixel_auroc"]):
        pixel_text = "-"
    else:
        pixel_text = (
            f'{record["pixel_auroc"]:.3f}'
        )

    fig.suptitle(
        f'{record["category"]} / '
        f'{record["anomaly_type"]} | '
        f'score={record["score_normalized"]:.3f} | '
        f'pixel-AUROC={pixel_text}'
    )

    fig.tight_layout()

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output_path,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--category",
        required=True,
    )

    parser.add_argument(
        "--dataset",
        required=True,
    )

    parser.add_argument(
        "--run",
        required=True,
        help="Diretório EA003_<categoria>_full",
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    parser.add_argument(
        "--n",
        type=int,
        default=3,
    )

    args = parser.parse_args()

    category = args.category

    dataset_root = Path(args.dataset)
    run_root = Path(args.run)
    output_root = Path(args.output)

    test_root = (
        dataset_root /
        category /
        "test"
    )

    gt_root = (
        dataset_root /
        category /
        "ground_truth"
    )

    maps_root = (
        run_root /
        "anomaly_maps" /
        "mvtec_ad" /
        category /
        "test"
    )

    if not maps_root.exists():
        raise FileNotFoundError(
            f"Anomaly maps não encontrados: "
            f"{maps_root}"
        )

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ----------------------------------------
    # Descobrir escala global dos anomaly maps
    # ----------------------------------------

    print("Calculando escala global dos maps...")

    global_min = float("inf")
    global_max = float("-inf")

    map_files = sorted(
        maps_root.rglob("*.tiff")
    )

    for path in map_files:
        anomaly_map = tifffile.imread(path)

        global_min = min(
            global_min,
            float(np.min(anomaly_map)),
        )

        global_max = max(
            global_max,
            float(np.max(anomaly_map)),
        )

    print(
        f"Map range: "
        f"{global_min:.6f} "
        f"→ {global_max:.6f}"
    )

    # ----------------------------------------
    # Coletar resultados por imagem
    # ----------------------------------------

    records = []

    for anomaly_dir in sorted(
        p for p in test_root.iterdir()
        if p.is_dir()
    ):
        anomaly_type = anomaly_dir.name

        for image_path in find_images(
            anomaly_dir
        ):
            stem = image_path.stem

            map_path = (
                maps_root /
                anomaly_type /
                f"{stem}.tiff"
            )

            if not map_path.exists():
                print(
                    "AVISO: map ausente:",
                    map_path,
                )
                continue

            anomaly_map = tifffile.imread(
                map_path
            ).astype(np.float32)

            # O código EfficientAD usa o máximo
            # do anomaly map como image score.
            score_raw = float(
                np.max(anomaly_map)
            )

            is_anomaly = (
                anomaly_type != "good"
            )

            pixel_auc = np.nan
            mask_path = ""

            if is_anomaly:
                candidate = (
                    gt_root /
                    anomaly_type /
                    f"{stem}_mask.png"
                )

                if candidate.exists():
                    mask_path = str(candidate)

                    gt = np.asarray(
                        Image.open(
                            candidate
                        ).convert("L")
                    )

                    gt = (
                        gt > 0
                    ).astype(np.uint8)

                    if np.unique(gt).size == 2:
                        pixel_auc = roc_auc_score(
                            gt.reshape(-1),
                            anomaly_map.reshape(-1),
                        )

            records.append(
                {
                    "category": category,
                    "anomaly_type":
                        anomaly_type,
                    "is_anomaly":
                        int(is_anomaly),
                    "image_path":
                        str(image_path),
                    "map_path":
                        str(map_path),
                    "mask_path":
                        mask_path,
                    "score_raw":
                        score_raw,
                    "score_normalized":
                        0.0,
                    "pixel_auroc":
                        float(pixel_auc),
                }
            )

    # ----------------------------------------
    # Normalização dos image scores
    # somente para facilitar visualização
    # ----------------------------------------

    raw_scores = np.asarray(
        [
            r["score_raw"]
            for r in records
        ],
        dtype=np.float32,
    )

    score_min = float(
        raw_scores.min()
    )

    score_max = float(
        raw_scores.max()
    )

    for record in records:
        if score_max > score_min:
            record["score_normalized"] = (
                record["score_raw"]
                - score_min
            ) / (
                score_max
                - score_min
            )

    # ----------------------------------------
    # CSV
    # ----------------------------------------

    csv_path = (
        output_root /
        "scores_por_imagem.csv"
    )

    with open(
        csv_path,
        "w",
        newline="",
    ) as f:
        fieldnames = [
            "category",
            "anomaly_type",
            "is_anomaly",
            "image_path",
            "map_path",
            "mask_path",
            "score_raw",
            "score_normalized",
            "pixel_auroc",
        ]

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(records)

    # ----------------------------------------
    # Seleção de casos
    # ----------------------------------------

    anomalies = [
        r for r in records
        if r["is_anomaly"] == 1
    ]

    normals = [
        r for r in records
        if r["is_anomaly"] == 0
    ]

    localization = [
        r for r in anomalies
        if not np.isnan(
            r["pixel_auroc"]
        )
    ]

    groups = {
        "anomalias_menor_score":
            sorted(
                anomalies,
                key=lambda x:
                    x["score_raw"],
            )[:args.n],

        "anomalias_maior_score":
            sorted(
                anomalies,
                key=lambda x:
                    x["score_raw"],
                reverse=True,
            )[:args.n],

        "normais_maior_score":
            sorted(
                normals,
                key=lambda x:
                    x["score_raw"],
                reverse=True,
            )[:args.n],

        "pior_localizacao":
            sorted(
                localization,
                key=lambda x:
                    x["pixel_auroc"],
            )[:args.n],

        "melhor_localizacao":
            sorted(
                localization,
                key=lambda x:
                    x["pixel_auroc"],
                reverse=True,
            )[:args.n],
    }

    # ----------------------------------------
    # Gerar figuras
    # ----------------------------------------

    for group_name, selected in groups.items():

        group_dir = (
            output_root /
            group_name
        )

        for position, record in enumerate(
            selected,
            start=1,
        ):
            original = Path(
                record["image_path"]
            ).stem

            filename = (
                f"{position:02d}_"
                f"{record['anomaly_type']}_"
                f"{original}.png"
            )

            save_visualization(
                record,
                global_min,
                global_max,
                group_dir / filename,
            )

    print()
    print("Análise concluída.")
    print("CSV:", csv_path)
    print("Imagens:", output_root)


if __name__ == "__main__":
    main()
