#!/usr/bin/env bash

set -e

IC_ROOT="${IC_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"

REPO="$IC_ROOT/baselines/patchcore-inspection"
DATASET="$IC_ROOT/datasets/mvtec_ad"

EXPERIMENT="$IC_ROOT/results/patchcore/MVTecAD_Results/PC002_IM224_WR50_L2-3_P01_D1024-1024_PS-3_AN-1_S0"

OUTPUT="$IC_ROOT/results/patchcore/qualitative"

SCRIPT="$IC_ROOT/tools/analisar_patchcore.py"

CATEGORIES=(
    screw
)

cd "$REPO"

for CATEGORY in "${CATEGORIES[@]}"
do
    echo
    echo "========================================"
    echo "Analisando categoria: $CATEGORY"
    echo "========================================"

    PYTHONPATH=src python "$SCRIPT" \
        --category "$CATEGORY" \
        --dataset "$DATASET" \
        --model "$EXPERIMENT/models/mvtec_$CATEGORY" \
        --output "$OUTPUT/$CATEGORY" \
        --n 3

    echo
    echo "Categoria $CATEGORY concluída."
done

echo
echo "========================================"
echo "Todas as análises foram concluídas."
echo "Resultados em:"
echo "$OUTPUT"
echo "========================================"
