import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
from PIL import Image
from sklearn.metrics import roc_auc_score
from torchvision import transforms

import patchcore.common
import patchcore.patchcore
from patchcore.datasets.mvtec import MVTecDataset, DatasetSplit


def normalize_global(x):
    x = np.asarray(x, dtype=np.float32)
    minimum = float(x.min())
    maximum = float(x.max())

    if maximum <= minimum:
        return np.zeros_like(x)

    return (x - minimum) / (maximum - minimum)


def save_visualization(record, segmentation, gt_mask, output_path):
    visual_transform = transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(224),
        ]
    )

    image = Image.open(record["image_path"]).convert("RGB")
    image = np.asarray(visual_transform(image))

    fig, axes = plt.subplots(1, 4, figsize=(13, 3.5))

    axes[0].imshow(image)
    axes[0].set_title("Imagem")

    axes[1].imshow(gt_mask, cmap="gray", vmin=0, vmax=1)
    axes[1].set_title("Ground truth")

    axes[2].imshow(segmentation, cmap="inferno", vmin=0, vmax=1)
    axes[2].set_title("Anomaly map")

    axes[3].imshow(image)
    axes[3].imshow(
        segmentation,
        cmap="inferno",
        alpha=0.45,
        vmin=0,
        vmax=1,
    )
    axes[3].set_title("Sobreposição")

    for ax in axes:
        ax.axis("off")

    pixel_auc = record["pixel_auroc"]

    if np.isnan(pixel_auc):
        pixel_text = "-"
    else:
        pixel_text = f"{pixel_auc:.3f}"

    fig.suptitle(
        f'{record["category"]} / {record["anomaly_type"]} | '
        f'score={record["score_normalized"]:.3f} | '
        f'pixel-AUROC={pixel_text}'
    )

    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--category", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--n", type=int, default=3)

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    device = torch.device(
        "cuda:0" if torch.cuda.is_available() else "cpu"
    )

    print("Device:", device)
    print("Categoria:", args.category)

    nn_method = patchcore.common.FaissNN(
        on_gpu=False,
        num_workers=4,
    )

    model = patchcore.patchcore.PatchCore(device)

    model.load_from_path(
        load_path=args.model,
        device=device,
        nn_method=nn_method,
    )

    dataset = MVTecDataset(
        source=args.dataset,
        classname=args.category,
        resize=256,
        imagesize=224,
        split=DatasetSplit.TEST,
    )

    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size=2,
        shuffle=False,
        num_workers=4,
        pin_memory=True,
    )

    print("Executando inferência...")

    scores, segmentations, labels_gt, masks_gt = model.predict(dataloader)

    scores = np.asarray(scores, dtype=np.float32)
    segmentations = np.asarray(segmentations, dtype=np.float32)
    masks_gt = np.asarray(masks_gt, dtype=np.float32)

    if masks_gt.ndim == 4:
        masks_gt = masks_gt[:, 0]

    # Mesma ideia de normalização global usada pelo script oficial.
    scores_normalized = normalize_global(scores)
    segmentations_normalized = normalize_global(segmentations)

    records = []

    for i, metadata in enumerate(dataset.data_to_iterate):
        category, anomaly_type, image_path, mask_path = metadata

        gt = (masks_gt[i] > 0.5).astype(np.uint8)

        if (
            anomaly_type != "good"
            and np.unique(gt).size == 2
        ):
            pixel_auc = roc_auc_score(
                gt.reshape(-1),
                segmentations_normalized[i].reshape(-1),
            )
        else:
            pixel_auc = np.nan

        records.append(
            {
                "index": i,
                "category": category,
                "anomaly_type": anomaly_type,
                "is_anomaly": int(anomaly_type != "good"),
                "image_path": image_path,
                "mask_path": mask_path or "",
                "score_raw": float(scores[i]),
                "score_normalized": float(scores_normalized[i]),
                "pixel_auroc": float(pixel_auc),
            }
        )

    csv_path = output_dir / "scores_por_imagem.csv"

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=records[0].keys(),
        )
        writer.writeheader()
        writer.writerows(records)

    anomalies = [
        r for r in records if r["is_anomaly"] == 1
    ]

    good = [
        r for r in records if r["is_anomaly"] == 0
    ]

    valid_localization = [
        r for r in anomalies if not np.isnan(r["pixel_auroc"])
    ]

    groups = {
        "anomalias_maior_score": sorted(
            anomalies,
            key=lambda x: x["score_normalized"],
            reverse=True,
        )[: args.n],

        "anomalias_menor_score": sorted(
            anomalies,
            key=lambda x: x["score_normalized"],
        )[: args.n],

        "normais_maior_score": sorted(
            good,
            key=lambda x: x["score_normalized"],
            reverse=True,
        )[: args.n],

        "pior_localizacao": sorted(
            valid_localization,
            key=lambda x: x["pixel_auroc"],
        )[: args.n],

        "melhor_localizacao": sorted(
            valid_localization,
            key=lambda x: x["pixel_auroc"],
            reverse=True,
        )[: args.n],
    }

    for group_name, selected in groups.items():
        group_dir = output_dir / group_name

        for position, record in enumerate(selected, start=1):
            idx = record["index"]

            original_name = Path(record["image_path"]).stem

            filename = (
                f"{position:02d}_"
                f"{record['anomaly_type']}_"
                f"{original_name}.png"
            )

            save_visualization(
                record,
                segmentations_normalized[idx],
                masks_gt[idx],
                group_dir / filename,
            )

    print()
    print("Concluído.")
    print("CSV:", csv_path)
    print("Visualizações:", output_dir)


if __name__ == "__main__":
    main()
