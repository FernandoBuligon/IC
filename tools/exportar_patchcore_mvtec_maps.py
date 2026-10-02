#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path

import numpy as np
import tifffile
import torch
import torch.nn.functional as F
from PIL import Image

import patchcore.common
import patchcore.patchcore
from patchcore.datasets.mvtec import MVTecDataset, DatasetSplit


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


def resize_map(anomaly_map, height, width):
    tensor = torch.from_numpy(
        np.asarray(anomaly_map, dtype=np.float32)
    )[None, None]

    resized = F.interpolate(
        tensor,
        size=(height, width),
        mode="bilinear",
        align_corners=False,
    )

    return resized[0, 0].numpy().astype(np.float32)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        required=True,
    )

    parser.add_argument(
        "--models",
        required=True,
        help="Diretório contendo mvtec_bottle, mvtec_cable, etc.",
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=2,
    )

    args = parser.parse_args()

    dataset_root = Path(args.dataset)
    models_root = Path(args.models)
    output_root = Path(args.output)

    device = torch.device(
        "cuda:0"
        if torch.cuda.is_available()
        else "cpu"
    )

    print("Device:", device)

    for category in CATEGORIES:
        print()
        print("=" * 60)
        print("Categoria:", category)
        print("=" * 60)

        model_path = (
            models_root /
            f"mvtec_{category}"
        )

        if not model_path.exists():
            raise FileNotFoundError(
                f"Modelo não encontrado: {model_path}"
            )

        nn_method = patchcore.common.FaissNN(
            on_gpu=False,
            num_workers=4,
        )

        model = patchcore.patchcore.PatchCore(
            device
        )

        model.load_from_path(
            load_path=str(model_path),
            device=device,
            nn_method=nn_method,
        )

        dataset = MVTecDataset(
            source=str(dataset_root),
            classname=category,
            resize=256,
            imagesize=224,
            split=DatasetSplit.TEST,
        )

        dataloader = torch.utils.data.DataLoader(
            dataset,
            batch_size=args.batch_size,
            shuffle=False,
            num_workers=4,
            pin_memory=True,
        )

        print(
            "Imagens de teste:",
            len(dataset),
        )

        scores, maps, labels, _ = model.predict(
            dataloader
        )

        if len(maps) != len(dataset.data_to_iterate):
            raise RuntimeError(
                "Número de mapas diferente "
                "do número de imagens."
            )

        csv_rows = []

        for metadata, score, anomaly_map, label in zip(
            dataset.data_to_iterate,
            scores,
            maps,
            labels,
        ):
            (
                classname,
                anomaly_type,
                image_path,
                mask_path,
            ) = metadata

            image_path = Path(image_path)

            with Image.open(image_path) as image:
                width, height = image.size

            resized_map = resize_map(
                anomaly_map,
                height,
                width,
            )

            map_dir = (
                output_root /
                "anomaly_maps" /
                "mvtec_ad" /
                category /
                "test" /
                anomaly_type
            )

            map_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            map_path = (
                map_dir /
                f"{image_path.stem}.tiff"
            )

            tifffile.imwrite(
                map_path,
                resized_map,
            )

            csv_rows.append(
                {
                    "category": category,
                    "anomaly_type": anomaly_type,
                    "image_path": str(image_path),
                    "map_path": str(map_path),
                    "is_anomaly": int(label),
                    "patchcore_image_score": float(score),
                    "map_max_score": float(
                        resized_map.max()
                    ),
                }
            )

        score_dir = (
            output_root /
            "scores"
        )

        score_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        csv_path = (
            score_dir /
            f"{category}.csv"
        )

        with open(
            csv_path,
            "w",
            newline="",
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=csv_rows[0].keys(),
            )

            writer.writeheader()
            writer.writerows(csv_rows)

        print(
            f"{category}: "
            f"{len(maps)} mapas salvos."
        )

        del model
        del dataloader
        del dataset

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    print()
    print("Exportação concluída.")
    print(
        "Anomaly maps:",
        output_root / "anomaly_maps"
    )


if __name__ == "__main__":
    main()
