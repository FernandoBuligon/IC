# Reprodução das baselines

## 1. Dados, diretórios e implementações

Execute os exemplos em Bash. Na raiz deste repositório:

```bash
export IC_ROOT="$PWD"
mkdir -p "$IC_ROOT/baselines"
git clone https://github.com/amazon-science/patchcore-inspection.git "$IC_ROOT/baselines/patchcore-inspection"
git -C "$IC_ROOT/baselines/patchcore-inspection" checkout fcaa92f124fb1ad74a7acf56726decd4b27cbcad
git clone https://github.com/nelson1425/EfficientAD.git "$IC_ROOT/baselines/efficientad"
git -C "$IC_ROOT/baselines/efficientad" checkout fcab5146f84ae17597044ad5ddf1656ccf805401
```

Esses comandos destinam-se a uma instalação nova. Se os clones já existem, confira `git status` e `git rev-parse HEAD` antes de trocar de revisão, preservando alterações locais.

Obtenha MVTec AD e LOCO AD nas [fontes oficiais](../README.md#datasets), extraia na estrutura descrita no README e obtenha o ImageNet train separadamente. Confira os 1.000 diretórios de classes de ImageNet e não use `--imagenet_train_path none`, pois isso desabilita a penalty utilizada nos experimentos.

Baixe também os avaliadores oficiais e extraia-os em:

```text
baselines/efficientad/mvtec_ad_evaluation/        # v1.0
baselines/efficientad/mvtec_loco_ad_evaluation/   # v2.0
```

Os nomes referem-se a diretórios cujo nível superior contém `evaluate_experiment.py`. O clone EfficientAD contém instruções para obter o teacher; confirme a presença de `baselines/efficientad/models/teacher_medium.pth` antes do treino. PatchCore também depende dos pesos pré-treinados de WideResNet50 obtidos pela torchvision; a chamada original equivale a `Wide_ResNet50_2_Weights.IMAGENET1K_V1` conforme o log da execução.

Aplique o patch apenas sobre o avaliador LOCO original:

```bash
patch --dry-run -d "$IC_ROOT/baselines/efficientad/mvtec_loco_ad_evaluation" -p0 < "$IC_ROOT/logs/mvtec_loco_evaluator_patch.diff"
patch -d "$IC_ROOT/baselines/efficientad/mvtec_loco_ad_evaluation" -p0 < "$IC_ROOT/logs/mvtec_loco_evaluator_patch.diff"
```

Não reaplique sobre uma cópia já corrigida. A [origem dos avaliadores](external_sources.json) registra o hash do arquivo compactado LOCO; [evaluator_checksums.json](evaluator_checksums.json) registra os arquivos Python utilizados, incluindo o patch aplicado. O arquivo compactado original do avaliador AD não foi encontrado, portanto seus hashes documentam a cópia local, sem alegar comparação com um original preservado.

## 2. Ambientes

Prepare os dois ambientes conforme [environments/README.md](../environments/README.md). Ative `ic-patchcore` para executar PatchCore/exportadores/adapter e `ic-efficientad` para EfficientAD e os avaliadores. Os nomes originais eram `patchcore` e `efficientad`. Reexporte `IC_ROOT` ao abrir outro terminal.

Antes de uma nova execução, separe as saídas dos JSONs já publicados. Depois de preparar dados, clones e ambientes, crie uma raiz de execução nova (troque `reproduction-01` a cada repetição):

```bash
export IC_SOURCE_ROOT="$IC_ROOT"
export IC_ROOT="$IC_SOURCE_ROOT/runs/reproduction-01"
mkdir -p "$IC_ROOT"
ln -s "$IC_SOURCE_ROOT/baselines" "$IC_ROOT/baselines"
ln -s "$IC_SOURCE_ROOT/datasets" "$IC_ROOT/datasets"
ln -s "$IC_SOURCE_ROOT/tools" "$IC_ROOT/tools"
```

`runs/` é ignorado pelo Git. Os comandos seguintes gravam modelos, métricas e logs nessa raiz nova. Os links apontam para suas cópias locais, sem duplicar datasets; o adapter continua sendo criado no diretório local de datasets. A raiz de execução deve estar vazia antes da preparação. O verificador resolve o caminho real de `tools/` e confere os resultados publicados na raiz de origem.

## 3. PatchCore no MVTec AD

A linha abaixo deriva do [comando registrado PC-002](patchcore_mvtec_ad_command.txt), substituindo apenas o prefixo local por `IC_ROOT`. Use um destino de experimento novo para novas execuções: a implementação pode adicionar sufixos quando a pasta existe; nesse caso ajuste o caminho de modelos no passo seguinte.

```bash
conda activate ic-patchcore
cd "$IC_ROOT/baselines/patchcore-inspection"
PYTHONPATH=src python bin/run_patchcore.py \
  --gpu 0 --seed 0 --save_patchcore_model \
  --log_group PC002_IM224_WR50_L2-3_P01_D1024-1024_PS-3_AN-1_S0 \
  --log_project MVTecAD_Results "$IC_ROOT/results/patchcore" \
  patch_core -b wideresnet50 -le layer2 -le layer3 \
  --pretrain_embed_dimension 1024 --target_embed_dimension 1024 \
  --anomaly_scorer_num_nn 1 --patchsize 3 \
  sampler -p 0.1 approx_greedy_coreset \
  dataset --resize 256 --imagesize 224 \
  -d bottle -d cable -d capsule -d carpet -d grid -d hazelnut \
  -d leather -d metal_nut -d pill -d screw -d tile -d toothbrush \
  -d transistor -d wood -d zipper mvtec "$IC_ROOT/datasets/mvtec_ad"

PYTHONPATH=src python "$IC_ROOT/tools/exportar_patchcore_mvtec_maps_geometry_fixed.py" \
  --dataset "$IC_ROOT/datasets/mvtec_ad" \
  --models "$IC_ROOT/results/patchcore/MVTecAD_Results/PC002_IM224_WR50_L2-3_P01_D1024-1024_PS-3_AN-1_S0/models" \
  --output "$IC_ROOT/results/patchcore/standardized_eval_geometry_fixed"
```

Avaliação com os mapas corrigidos:

```bash
conda activate ic-efficientad
for category in bottle cable capsule carpet grid hazelnut leather metal_nut pill screw tile toothbrush transistor wood zipper; do
  python "$IC_ROOT/baselines/efficientad/mvtec_ad_evaluation/evaluate_experiment.py" \
    --dataset_base_dir "$IC_ROOT/datasets/mvtec_ad" \
    --anomaly_maps_dir "$IC_ROOT/results/patchcore/standardized_eval_geometry_fixed/anomaly_maps/mvtec_ad" \
    --output_dir "$IC_ROOT/results/patchcore/standardized_eval_geometry_fixed/metrics/$category" \
    --evaluated_objects "$category" --pro_integration_limit 0.3
done
```

Os campos `classification_au_roc` e `au_pro` do objeto correspondente à categoria em cada `metrics.json` dão as duas métricas finais. O Image AUROC final é o do avaliador dos mapas; o resultado interno do PatchCore registrado no PC-002 usa seu score de imagem e pode diferir.

## 4. EfficientAD-M no MVTec AD

O script histórico de lote começa em `cable`, pois `bottle` foi executada separadamente como EA-002. Execute primeiro bottle, conforme os parâmetros de [EA-002](../logs/experiments/EA-002.txt), e depois o lote das outras 14 categorias:

```bash
conda activate ic-efficientad
cd "$IC_ROOT/baselines/efficientad"
python efficientad.py --dataset mvtec_ad --subdataset bottle \
  --output_dir "$IC_ROOT/results/efficientad/EA002_bottle_full" \
  --model_size medium --weights models/teacher_medium.pth \
  --imagenet_train_path "$IC_ROOT/datasets/imagenet/ILSVRC/Data/CLS-LOC/train" \
  --mvtec_ad_path "$IC_ROOT/datasets/mvtec_ad" --train_steps 70000
python mvtec_ad_evaluation/evaluate_experiment.py \
  --dataset_base_dir "$IC_ROOT/datasets/mvtec_ad" \
  --anomaly_maps_dir "$IC_ROOT/results/efficientad/EA002_bottle_full/anomaly_maps/mvtec_ad" \
  --output_dir "$IC_ROOT/results/efficientad/EA002_bottle_full/metrics/mvtec_ad" \
  --evaluated_objects bottle --pro_integration_limit 0.3
bash "$IC_ROOT/tools/run_efficientad_mvtec_all.sh"
```

EfficientAD já exporta TIFFs na resolução original durante a execução. O script de lote avalia cada categoria ao terminar e pula pastas que já possuem métricas. Em uma reprodução integral, use uma cópia de trabalho com pastas de saída novas, para não pular os JSONs publicados ou sobrescrever evidências existentes.

`tools/consolidar_efficientad.py` é o consolidador histórico: lê também logs de tempo e regrava o CSV/resumo no diretório de resultados. Para apenas inspecionar os resultados publicados, use o verificador da seção 7.

## 5. PatchCore no MVTec LOCO AD

O adapter mantém imagens por symlink e combina máscaras por OR apenas para o loader. **O script original recria o diretório de adapter, removendo uma versão existente.** Execute-o em uma instalação nova ou preserve o adapter existente antes de refazê-lo. Nenhum adapter foi refeito durante a preparação para publicação.

```bash
conda activate ic-patchcore
python "$IC_ROOT/tools/criar_adapter_patchcore_loco.py"
cd "$IC_ROOT/baselines/patchcore-inspection"
PYTHONPATH=src python bin/run_patchcore.py \
  --gpu 0 --seed 0 --save_patchcore_model \
  --log_project PCL001 --log_group IM224_WR50_L2-3_P01_D1024-1024_PS-3_AN-1_S0 \
  "$IC_ROOT/results/patchcore_loco" \
  patch_core -b wideresnet50 -le layer2 -le layer3 \
  --pretrain_embed_dimension 1024 --target_embed_dimension 1024 \
  --anomaly_scorer_num_nn 1 --patchsize 3 --faiss_num_workers 4 \
  sampler -p 0.1 approx_greedy_coreset \
  dataset --resize 256 --imagesize 224 \
  -d breakfast_box -d juice_bottle -d pushpins -d screw_bag -d splicing_connectors \
  mvtec "$IC_ROOT/datasets/mvtec_loco_patchcore_adapter"

PYTHONPATH=src python "$IC_ROOT/tools/exportar_patchcore_loco_maps_geometry_fixed.py" \
  --dataset "$IC_ROOT/datasets/mvtec_loco_patchcore_adapter" \
  --models "$IC_ROOT/results/patchcore_loco/PCL001/IM224_WR50_L2-3_P01_D1024-1024_PS-3_AN-1_S0/models" \
  --output "$IC_ROOT/results/patchcore_loco/PCL001/standardized_eval_geometry_fixed"
```

O [comando PCL-001](patchcore_loco_command.txt) documenta a execução original. Avalie usando o **dataset LOCO original**:

```bash
conda activate ic-efficientad
for category in breakfast_box juice_bottle pushpins screw_bag splicing_connectors; do
  python "$IC_ROOT/baselines/efficientad/mvtec_loco_ad_evaluation/evaluate_experiment.py" \
    --dataset_base_dir "$IC_ROOT/datasets/mvtec_loco_ad" \
    --anomaly_maps_dir "$IC_ROOT/results/patchcore_loco/PCL001/standardized_eval_geometry_fixed/anomaly_maps/mvtec_loco" \
    --output_dir "$IC_ROOT/results/patchcore_loco/PCL001/standardized_eval_geometry_fixed/metrics/mvtec_loco/$category" \
    --object_name "$category"
done
```

O argumento `output_dir` inclui explicitamente a categoria, pois o avaliador grava `metrics.json` diretamente no diretório recebido. A métrica usada neste projeto é a entrada `"0.05"` de `localization.auc_spro`; o avaliador também calcula outros limites.

## 6. EfficientAD-M no MVTec LOCO AD

O loop abaixo reúne a interface existente de `efficientad.py` com os nomes das cinco execuções completas preservadas. O split `validation` oficial é selecionado pelo próprio código ao usar `--dataset mvtec_loco`.

```bash
conda activate ic-efficientad
cd "$IC_ROOT/baselines/efficientad"
for run in EAL002_breakfast_box_full EAL003_juice_bottle_full EAL004_pushpins_full EAL005_screw_bag_full EAL006_splicing_connectors_full; do
  category="${run#*_}"
  category="${category%_full}"
  python efficientad.py --dataset mvtec_loco --subdataset "$category" \
    --output_dir "$IC_ROOT/results/efficientad_loco/$run" \
    --model_size medium --weights models/teacher_medium.pth \
    --imagenet_train_path "$IC_ROOT/datasets/imagenet/ILSVRC/Data/CLS-LOC/train" \
    --mvtec_loco_path "$IC_ROOT/datasets/mvtec_loco_ad" --train_steps 70000
  python mvtec_loco_ad_evaluation/evaluate_experiment.py \
    --dataset_base_dir "$IC_ROOT/datasets/mvtec_loco_ad" \
    --anomaly_maps_dir "$IC_ROOT/results/efficientad_loco/$run/anomaly_maps/mvtec_loco" \
    --output_dir "$IC_ROOT/results/efficientad_loco/EAL_full_evaluation/metrics/mvtec_loco/$category" \
    --object_name "$category"
done
```

O loop avalia diretamente os mapas de cada execução, sem exigir cópias adicionais dos mapas. `EAL001` foi um smoke test e não entra nos resultados finais.

## 7. Conferência e comparação

```bash
cd "$IC_ROOT"
python3 tools/verificar_resultados.py
```

Esse script novo usa apenas a biblioteca padrão e não escreve nos resultados. Confere os 45 hashes, as 15 categorias AD e cinco LOCO por método, compara os CSVs com os JSONs finais, verifica a comparação LOCO e imprime a comparação AD por categoria e as médias. A tolerância de 0.00000051 se aplica ao CSV EfficientAD AD originalmente arredondado a seis casas; os demais CSVs são comparados com tolerância de 1e-12.

Para novas execuções, extraia os campos descritos em [results/README.md](../results/README.md), junte por categoria e calcule a média aritmética entre categorias. No LOCO, preserve logical e structural e confira `mean = (logical + structural) / 2`. Compare as novas métricas com os CSVs publicados antes de atualizar qualquer resumo. O verificador valida o snapshot publicado e intencionalmente rejeita resultados que substituam seus arquivos.

## 8. Scripts históricos e limites

- `exportar_patchcore_mvtec_maps.py` e `exportar_patchcore_loco_maps.py` usam a exportação anterior: mantenha-os apenas para rastrear a correção.
- `evaluate_patchcore_mvtec.sh` e `consolidar_patchcore_padronizado.py` ainda apontam para `standardized_eval`, a avaliação anterior à correção. Use os comandos da seção 3 para a comparação final.
- `rodar_analise_qualitativa.sh` está configurado para `screw`. Os scripts `analisar_*.py` recebem os caminhos e a categoria por argumentos. As imagens produzidas contêm dados do dataset e não são publicadas aqui.
- `smoke_test_loco_evaluator.py` gera mapas sintéticos determinísticos para `breakfast_box`; suas saídas não são métricas de baseline.
- A única mudança de portabilidade nos scripts existentes substitui a raiz fixa `~/IC` por `IC_ROOT` ou pela raiz do próprio script. Os cálculos, parâmetros, nomes de execuções e comportamento de reexecução foram preservados.
- Não foram refeitos treinamentos nem avaliações sobre todos os mapas durante a publicação. As validações cobrem a integridade e consistência dos artefatos existentes, a sintaxe, a aplicação do patch e a mudança dos caminhos.
