# Auditoria para publicação — 2026-10-02

## Estado inicial

Raiz: `~/IC`; branch `main`, sem commits, sem arquivos rastreados e sem remote. Todos os arquivos estavam não rastreados. Não havia histórico para reescrever. O destino informado pelo autor foi `https://github.com/FernandoBuligon/IC`; a consulta inicial ao remoto não encontrou referências.

Volumes locais aproximados: datasets 167 GB, resultados 57 GB, logs 121 MB e implementações externas 87 MB. Foram encontrados índices FAISS acima de 100 MB, TIFFs, checkpoints, caches, um adapter com symlinks e imagens qualitativas derivadas dos datasets. Esses artefatos permanecem no disco e estão excluídos do Git.

PatchCore e EfficientAD são clones independentes nos commits registrados em [external_sources.json](external_sources.json), sem alterações no código rastreado. Os avaliadores foram adicionados localmente ao clone EfficientAD. O diretório `.git` dentro do avaliador AD estava vazio e não representava um terceiro histórico independente. Não foram importados clones como submódulos ou cópias de código externo.

## Seleção e preservação

- Cinco CSVs finais e 40 JSONs de métricas selecionados, totalizando 197.116 bytes. Os [hashes](../results/provenance.json) registram os bytes originais, preservados também pelo `.gitattributes`.
- Todos os 13 scripts existentes de `tools/` preservados. Sete scripts receberam apenas configuração da raiz por `IC_ROOT`, com fallback para a raiz do projeto. Foram removidas linhas vazias excedentes no fim de três scripts. Nenhum cálculo experimental foi alterado.
- Um verificador novo confere os artefatos publicados sem regravá-los.
- Relatório final mantido integralmente na raiz. Análises e comparação históricas preservadas; removido apenas um espaço em branco ao fim de uma linha da análise PatchCore.
- Snapshots Conda/pip, commits, notas curtas dos experimentos e patch LOCO preservados. As listas de instalação derivadas corrigem somente a referência local de `packaging` usando a versão confirmada no export Conda.
- `context_handoff_ic.md` permanece local: é um handoff de trabalho com contexto e resultados intermediários; o relatório final e as análises preservadas contêm a documentação científica selecionada.
- Não foi localizado um relatório separado do estudo inicial dos datasets. Não se criou um texto retroativo para representar um documento inexistente.

## Verificações

Os CSVs foram comparados aos JSONs dos avaliadores, incluindo os deltas LOCO, a cobertura de categorias e as médias do relatório. Os scripts passaram por análise de sintaxe Python/Bash. O patch foi aplicado a uma cópia temporária do arquivo original do pacote LOCO e produziu bytes idênticos ao arquivo utilizado. Os links relativos da documentação nova foram conferidos.

A revisão dos arquivos selecionados procura nomes de credenciais, arquivos `.env`, chaves privadas, formatos comuns de tokens e atribuições suspeitas. Nenhum segredo foi identificado no material selecionado. Isso não representa uma auditoria dos conteúdos dos datasets ou de arquivos binários excluídos.

O treinamento, a inferência e a avaliação integral dos mapas não foram repetidos para publicar. As dependências foram documentadas com base nos snapshots existentes, sem alegar instalação limpa validada. A licença do código próprio não foi escolhida em nome do autor; implementações e datasets externos mantêm os termos de suas fontes.
