# Resultados finais e rastreabilidade

Os cinco CSVs finais e os 40 JSONs de avaliação são mantidos nos caminhos originais, sem alterar bytes ou precisão. O arquivo [provenance.json](provenance.json) registra caminho, tamanho e SHA-256 de cada um. Não contém datasets, mapas ou pesos.

| Resumo | Fonte dos resultados por categoria |
|---|---|
| `patchcore/patchcore_mvtec_ad_geometry_fixed_summary.csv` | `patchcore/standardized_eval_geometry_fixed/metrics/<categoria>/metrics.json` |
| `efficientad/efficientad_mvtec_ad_results.csv` | `efficientad/EA002_bottle_full/metrics/mvtec_ad/metrics.json` para bottle; `efficientad/EA003_<categoria>_full/metrics/mvtec_ad/metrics.json` para as outras 14 |
| `patchcore_loco/patchcore_loco_summary_geometry_fixed.csv` | `patchcore_loco/PCL001/standardized_eval_geometry_fixed/metrics/mvtec_loco/<categoria>/metrics.json` |
| `efficientad_loco/efficientad_loco_summary.csv` | `efficientad_loco/EAL_full_evaluation/metrics/mvtec_loco/<categoria>/metrics.json` |
| `loco_patchcore_vs_efficientad.csv` | Junção dos dois resumos LOCO por categoria, com diferenças EfficientAD − PatchCore |

No AD, os campos JSON são `classification_au_roc` e `au_pro` (limite FPR 0.3). No LOCO, são `classification.auc_roc` e `localization.auc_spro.<tipo>["0.05"]`. As médias no README são médias aritméticas entre categorias; `Mean` no CSV EfficientAD AD não é uma categoria adicional. Esse CSV foi originalmente arredondado a seis casas e contém tempo de treino; o tempo de bottle está ausente e não foi preenchido artificialmente.

Execute, na raiz, `python3 tools/verificar_resultados.py` para validar hashes, cobertura de categorias, correspondência CSV × JSON, diferenças LOCO e médias do relatório. O comando imprime também a comparação AD por categoria, sem recalcular os modelos nem regravar as métricas. Para comparar novas execuções, use os mesmos campos dos novos JSONs; o manifesto representa exclusivamente as execuções publicadas.

As saídas preliminares, smoke tests, índices FAISS, mapas TIFF e imagens qualitativas ficam locais e ignorados. Novos resultados finais devem ser selecionados explicitamente no `.gitignore`, após revisar seu conteúdo e sua proveniência.
