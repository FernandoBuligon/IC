#!/usr/bin/env bash

set -euo pipefail

IC_ROOT="${IC_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"

DATASET="$IC_ROOT/datasets/mvtec_ad"

MAPS="$IC_ROOT/results/patchcore/standardized_eval/anomaly_maps/mvtec_ad"

OUTPUT="$IC_ROOT/results/patchcore/standardized_eval/metrics"

EVALUATOR="$IC_ROOT/baselines/efficientad/mvtec_ad_evaluation/evaluate_experiment.py"

CATEGORIES=(
    bottle
    cable
    capsule
    carpet
    grid
    hazelnut
    leather
    metal_nut
    pill
    screw
    tile
    toothbrush
    transistor
    wood
    zipper
)

mkdir -p "$OUTPUT"

for CATEGORY in "${CATEGORIES[@]}"
do
    echo
    echo "========================================"
    echo "Avaliando: $CATEGORY"
    echo "========================================"

    CATEGORY_OUTPUT="$OUTPUT/$CATEGORY"

    mkdir -p "$CATEGORY_OUTPUT"

    python "$EVALUATOR" \
        --dataset_base_dir "$DATASET" \
        --anomaly_maps_dir "$MAPS" \
        --output_dir "$CATEGORY_OUTPUT" \
        --evaluated_objects "$CATEGORY"
done

echo
echo "Todas as categorias avaliadas."
