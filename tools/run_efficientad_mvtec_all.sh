#!/usr/bin/env bash

set -euo pipefail

IC_ROOT="${IC_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"

REPO="$IC_ROOT/baselines/efficientad"
DATASET="$IC_ROOT/datasets/mvtec_ad"
IMAGENET="$IC_ROOT/datasets/imagenet/ILSVRC/Data/CLS-LOC/train"

RESULT_ROOT="$IC_ROOT/results/efficientad"
LOG_ROOT="$IC_ROOT/logs/experiments"

TEACHER="$REPO/models/teacher_medium.pth"
EVAL_SCRIPT="$REPO/mvtec_ad_evaluation/evaluate_experiment.py"

CATEGORIES=(
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

mkdir -p "$RESULT_ROOT"
mkdir -p "$LOG_ROOT"

cd "$REPO"

for CATEGORY in "${CATEGORIES[@]}"
do
    OUTPUT="$RESULT_ROOT/EA003_${CATEGORY}_full"
    LOG="$LOG_ROOT/EA003_${CATEGORY}.log"

    echo
    echo "================================================="
    echo "EfficientAD-M — $CATEGORY"
    echo "================================================="

    if [ -f "$OUTPUT/metrics/mvtec_ad/metrics.json" ]; then
        echo "Categoria já concluída: $CATEGORY"
        echo "Pulando."
        continue
    fi

    if [ -e "$OUTPUT" ]; then
        echo
        echo "ERRO:"
        echo "A pasta abaixo já existe, mas não possui metrics.json:"
        echo "$OUTPUT"
        echo
        echo "Isso indica uma execução incompleta."
        echo "Remova ou renomeie essa pasta antes de continuar."
        exit 1
    fi

    echo "Iniciando treinamento..."

    {
        time python efficientad.py \
            --dataset mvtec_ad \
            --subdataset "$CATEGORY" \
            --output_dir "$OUTPUT" \
            --model_size medium \
            --weights "$TEACHER" \
            --imagenet_train_path "$IMAGENET" \
            --mvtec_ad_path "$DATASET" \
            --train_steps 70000
    } 2>&1 | tee "$LOG"

    echo
    echo "Treinamento concluído."
    echo "Executando avaliação oficial..."

    python "$EVAL_SCRIPT" \
        --dataset_base_dir "$DATASET" \
        --anomaly_maps_dir "$OUTPUT/anomaly_maps/mvtec_ad" \
        --output_dir "$OUTPUT/metrics/mvtec_ad" \
        --evaluated_objects "$CATEGORY" \
        2>&1 | tee -a "$LOG"

    echo
    echo "Categoria $CATEGORY concluída."
done

echo
echo "================================================="
echo "Todas as categorias foram processadas."
echo "================================================="
