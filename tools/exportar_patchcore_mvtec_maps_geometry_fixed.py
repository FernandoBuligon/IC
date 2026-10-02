#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path

import numpy as np
import tifffile
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

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

RESIZE = 256


def restore_center_crop_map(
    anomaly_map,
    image_path,
):
    anomaly_map = np.asarray(
        anomaly_map,
        dtype=np.float32,
    )

    if anomaly_map.ndim != 2:
        raise RuntimeError(
            f"Mapa deveria ser 2D, recebido {anomaly_map.shape}"
        )

    crop_height, crop_width = anomaly_map.shape

    resize_transform = transforms.Resize(RESIZE)

    with Image.open(image_path) as image:
        original_width, original_height = image.size

        # Usa exatamente a transformação torchvision do loader.
        resized_image = resize_transform(image)
        resized_width, resized_height = resized_image.size

    # Mesmo posicionamento usado por torchvision CenterCrop.
    crop_top = int(round(
        (resized_height - crop_height) / 2.0
    ))

    crop_left = int(round(
        (resized_width - crop_width) / 2.0
    ))

    if (
        crop_top < 0
        or crop_left < 0
        or crop_top + crop_height > resized_height
        or crop_left + crop_width > resized_width
    ):
        raise RuntimeError(
            "O anomaly map não cabe na geometria redimensionada: "
            f"map={anomaly_map.shape}, "
            f"resize={(resized_height, resized_width)}, "
            f"image={image_path}"
        )

    # A região fora do CenterCrop não foi observada pelo PatchCore.
    # Mantemos nela o menor anomaly score observado no mapa.
    fill_score = float(anomaly_map.min())

    canvas = np.full(
        (resized_height, resized_width),
        fill_score,
        dtype=np.float32,
    )

    canvas[
        crop_top:crop_top + crop_height,
        crop_left:crop_left + crop_width
    ] = anomaly_map

    tensor = torch.from_numpy(
        canvas
    )[None, None]

    restored = F.interpolate(
        tensor,
        size=(original_height, original_width),
        mode="bilinear",
        align_corners=False,
    )

    restored = (
        restored[0, 0]
        .numpy()
        .astype(np.float32)
    )

    return {
        "map": restored,
        "original_width": original_width,
        "original_height": original_height,
        "resized_width": resized_width,
        "resized_height": resized_height,
        "crop_left": crop_left,
        "crop_top": crop_top,
        "fill_score": fill_score,
    }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        required=True,
    )

    parser.add_argument(
        "--models",
        required=True,
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

    total_maps = 0

    for category in CATEGORIES:
        print()
        print("=" * 60)
        print("Categoria:", category)
        print("=" * 60)

        model_path = (
            models_root
            / f"mvtec_{category}"
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

            restored = restore_center_crop_map(
                anomaly_map,
                image_path,
            )

            restored_map = restored["map"]

            map_dir = (
                output_root
                / "anomaly_maps"
                / "mvtec_ad"
                / category
                / "test"
                / anomaly_type
            )

            map_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            map_path = (
                map_dir
                / f"{image_path.stem}.tiff"
            )

            tifffile.imwrite(
                str(map_path),
                restored_map,
            )

            csv_rows.append({
                "category": category,
                "anomaly_type": anomaly_type,
                "image_path": str(image_path),
                "map_path": str(map_path),
                "is_anomaly": int(label),
                "patchcore_image_score": float(score),
                "map_max_score": float(restored_map.max()),
                "original_width": restored["original_width"],
                "original_height": restored["original_height"],
                "resized_width": restored["resized_width"],
                "resized_height": restored["resized_height"],
                "crop_left": restored["crop_left"],
                "crop_top": restored["crop_top"],
                "fill_score": restored["fill_score"],
            })

        score_dir = (
            output_root
            / "scores"
        )

        score_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        csv_path = (
            score_dir
            / f"{category}.csv"
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

        first = csv_rows[0]

        print(
            "Geometria exemplo: "
            f"original="
            f"{first['original_width']}x"
            f"{first['original_height']} "
            f"resize="
            f"{first['resized_width']}x"
            f"{first['resized_height']} "
            f"crop origin="
            f"({first['crop_left']},"
            f"{first['crop_top']})"
        )

        total_maps += len(maps)

        del model
        del dataloader
        del dataset

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    print()
    print("Exportação concluída.")
    print("Total de mapas:", total_maps)
    print(
        "Anomaly maps:",
        output_root / "anomaly_maps"
    )


if __name__ == "__main__":
    main()
