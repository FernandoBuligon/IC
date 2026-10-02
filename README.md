# Baselines de detecção de anomalias industriais — IC

Iniciação Científica sobre detecção e localização de anomalias industriais com **MVTec AD** e **MVTec LOCO AD**, usando PatchCore e EfficientAD-M. Este repositório reúne os scripts do projeto, protocolos, métricas e relatórios.

## Etapas já concluídas

- Estudo dos datasets: categorias, organização, anotações e métricas.
- Reprodução do PatchCore no MVTec AD.
- Reprodução do EfficientAD-M no MVTec AD.
- Avaliação padronizada e comparação entre os métodos.
- Adaptação e execução do PatchCore no MVTec LOCO AD.
- Execução do EfficientAD-M no MVTec LOCO AD.
- Comparação de anomalias **logical × structural**.

## Estrutura do repositório

```text
README.md
relatorio_baselines_visao_computacional_final.md
*_baseline_analysis.md / comparacao_patchcore_efficientad.md
 tools/          scripts de adaptação, exportação, avaliação e análise
 docs/           reprodução, auditoria e origem das implementações
 environments/   dependências derivadas dos registros de ambiente
 logs/           commits, snapshots de ambiente, notas e patch do avaliador
 results/        CSVs finais, JSONs dos avaliadores e hashes de integridade
```

`datasets/` e `baselines/` são diretórios **locais, ignorados pelo Git**. As implementações externas são obtidas separadamente. Os resultados mantêm os caminhos das execuções originais para preservar referências e rastreabilidade.

## Datasets

**MVTec AD e MVTec LOCO AD não estão incluídos.** Obtenha-os nas páginas oficiais: [MVTec AD](https://www.mvtec.com/research-teaching/datasets/mvtec-ad) e [MVTec LOCO AD](https://www.mvtec.com/research-teaching/datasets/mvtec-loco-ad), que também disponibilizam seus avaliadores. Observe os termos de uso na origem. O ImageNet utilizado na penalty loss também deve ser obtido separadamente.

Estrutura local esperada, a partir da raiz do projeto:

```text
datasets/
├── mvtec_ad/<categoria>/{train,test,ground_truth}/
├── mvtec_loco_ad/<categoria>/{train,validation,test,ground_truth}/
└── imagenet/ILSVRC/Data/CLS-LOC/train/<classe>/
```

Preserve todos os arquivos auxiliares oficiais do LOCO, incluindo configurações das anotações. O adapter gerado em `datasets/mvtec_loco_patchcore_adapter/` contém symlinks e máscaras derivadas e também fica fora do Git.

## Ambiente

| Componente | Ambiente experimental registrado |
|---|---|
| SO | Linux Mint 22.1 |
| CPU | Intel i5-14600K |
| RAM | 32 GB |
| GPU | NVIDIA RTX 5060, 8 GB |
| Python | 3.11 (3.11.16 nos exports Conda) |
| PyTorch | 2.13.0+cu130 |
| Torchvision | 0.28.0+cu130 |
| CUDA do PyTorch | 13.0 |
| FAISS | CPU, 1.15.1 |

Fontes: [ambiente PatchCore](logs/patchcore_conda_environment.yml), [ambiente EfficientAD](logs/efficientad_conda_environment.yml) e [relatório](relatorio_baselines_visao_computacional_final.md). Os snapshots originais foram preservados; as listas derivadas e seus limites estão em [environments/README.md](environments/README.md). A preparação para publicação não repetiu o treinamento nem validou uma instalação limpa de todas as dependências.

## PatchCore

Implementação da [Amazon Science](https://github.com/amazon-science/patchcore-inspection), commit `fcaa92f124fb1ad74a7acf56726decd4b27cbcad`.

WideResNet50, `layer2 + layer3`, Resize 256, CenterCrop 224, embedding 1024 → 1024, patch size 3, 1-NN, approximate greedy coreset de 10%, seed 0 e FAISS CPU. O backbone usa GPU quando disponível. O código rastreado do clone não foi modificado; o adapter e os exportadores estão em [tools/](tools/).

## EfficientAD-M

Implementação [nelson1425/EfficientAD](https://github.com/nelson1425/EfficientAD), commit `fcab5146f84ae17597044ad5ddf1656ccf805401` (implementação pública não oficial).

Variante medium, `teacher_medium.pth`, **70.000 passos por categoria**, ImageNet penalty habilitada e seed 42 definida pela implementação. No LOCO, usa o split oficial de validação; no AD, separa 10% do treino para validação. O código rastreado do clone não foi modificado. O teacher e os checkpoints não são redistribuídos neste repositório.

## Avaliação

- **MVTec AD:** Image AUROC e AU-PRO @ FPR ≤ 0.3, avaliador MVTec v1.0.
- **MVTec LOCO AD:** Image AUROC e AUC-sPRO @ FPR ≤ 0.05, avaliador MVTec v2.0; resultados separados em logical, structural e mean. `mean` é a média dos dois tipos, seguida da média entre categorias.

Os exportadores `*_geometry_fixed.py` reconstroem a posição do CenterCrop no espaço Resize(256), preenchem a região não observada com o menor score do mapa e só então interpolam para a resolução original. Os exportadores anteriores foram preservados como histórico e **não devem gerar os resultados finais**.

O [patch LOCO](logs/mvtec_loco_evaluator_patch.diff) fixa a amostragem com `np.random.RandomState(0)` e remove apenas thresholds iniciais exatamente duplicados, preservando sua ordem antes do `binary_refinement`. O ground truth original multicanal é utilizado na avaliação; as máscaras OR do adapter servem apenas ao loader do PatchCore. Veja a [origem e os hashes dos avaliadores](docs/external_sources.json).

## Resultados

| Dataset | Método | Image AUROC | Localização |
|---|---|---:|---:|
| MVTec AD | PatchCore | 0.990959 | 0.925413 (AU-PRO@0.3) |
| MVTec AD | EfficientAD-M | 0.990052 | 0.936177 (AU-PRO@0.3) |
| MVTec LOCO AD | PatchCore | 0.737883 | 0.501778 (AUC-sPRO@0.05) |
| MVTec LOCO AD | EfficientAD-M | 0.894370 | 0.798023 (AUC-sPRO@0.05) |

As linhas LOCO são médias de `mean` entre as cinco categorias. Resultados completos:

- [PatchCore — AD](results/patchcore/patchcore_mvtec_ad_geometry_fixed_summary.csv).
- [EfficientAD-M — AD](results/efficientad/efficientad_mvtec_ad_results.csv).
- [PatchCore — LOCO](results/patchcore_loco/patchcore_loco_summary_geometry_fixed.csv).
- [EfficientAD-M — LOCO](results/efficientad_loco/efficientad_loco_summary.csv).
- [Comparação LOCO, incluindo logical e structural](results/loco_patchcore_vs_efficientad.csv).
- [Rastreabilidade dos 40 JSONs de avaliação](results/README.md).

A precisão original dos CSVs foi preservada. Os números das notas históricas podem usar a exportação antiga ou a métrica interna do método; a tabela acima e o relatório final usam a avaliação padronizada com geometria corrigida.

## Reprodução

O [guia de reprodução](docs/REPRODUCIBILITY.md) apresenta o procedimento completo: obter os datasets, configurar caminhos e ambientes, clonar os commits registrados, executar as quatro combinações método/dataset, exportar os mapas, aplicar o patch, avaliar e comparar os resultados. Os comandos foram conferidos contra os scripts e os registros locais.

Para conferir os artefatos publicados e imprimir as comparações usando apenas Python padrão:

```bash
python3 tools/verificar_resultados.py
```

Os scripts de caminho fixo passaram a aceitar a variável `IC_ROOT`; sem ela usam a raiz que contém `tools/`. Os exportadores e scripts qualitativos já recebem caminhos por argumentos. As particularidades dos scripts históricos estão documentadas no guia.

## Relatório

[Relatório final desta etapa](relatorio_baselines_visao_computacional_final.md).

Registros históricos: [PatchCore](patchcore_baseline_analysis.md), [EfficientAD](efficientad_baseline_analysis.md) e [comparação no AD](comparacao_patchcore_efficientad.md). O estudo inicial é mencionado nesses registros, mas não foi localizado um relatório separado dessa etapa na auditoria.
