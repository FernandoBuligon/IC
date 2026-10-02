# Documentação da Primeira Baseline — PatchCore no MVTec AD

> **Objetivo deste documento:** registrar, de forma organizada, toda a reprodução e análise da primeira baseline do projeto, além de indicar **o que deve ser incorporado ao relatório principal**, quais títulos utilizar, quais textos podem ser aproveitados e quais imagens devem ser inseridas.

---

# 1. Identificação da baseline

## Método
**PatchCore**

## Implementação utilizada
Implementação oficial disponibilizada pela Amazon Science.

## Commit utilizado
```text
fcaa92f124fb1ad74a7acf56726decd4b27cbcad
```

## Dataset
**MVTec AD**

## Categorias avaliadas
Todas as 15 categorias:

```text
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
```

---

# 2. Ambiente experimental

O PatchCore foi executado em ambiente Linux dedicado, mantendo o código oficial do método e utilizando versões modernas das bibliotecas para garantir compatibilidade com o hardware disponível.

## Hardware

- **CPU:** Intel Core i5-14600K
- **RAM:** 32 GB
- **GPU:** NVIDIA GeForce RTX 5060
- **VRAM:** 8 GB
- **Sistema operacional:** Linux Mint 22.1

## Software principal

- **Python:** 3.11
- **PyTorch:** 2.13.0+cu130
- **Torchvision:** 0.28.0+cu130
- **CUDA utilizada pelo PyTorch:** 13.0
- **FAISS:** CPU
- **Backbone:** WideResNet50 pré-treinada no ImageNet

## Observação metodológica

A implementação oficial foi preservada, porém o ambiente original dos autores não foi reproduzido literalmente. Foi utilizado um stack atualizado de Python/PyTorch, necessário para compatibilidade com a GPU empregada. O FAISS foi executado em CPU, enquanto a extração de características foi realizada com suporte à GPU.

---

# 3. Configuração experimental

A configuração utilizada corresponde à baseline de resolução 224×224 do repositório oficial do PatchCore.

## Hiperparâmetros principais

| Parâmetro | Valor |
|---|---:|
| Backbone | WideResNet50 |
| Camadas utilizadas | layer2, layer3 |
| Resize | 256 |
| Tamanho final da imagem | 224×224 |
| Coreset | 10% |
| Dimensão pré-embedding | 1024 |
| Dimensão final do embedding | 1024 |
| Patch size | 3 |
| Número de vizinhos | 1 |
| Seed | 0 |
| FAISS | CPU |

---

# 4. Experimento inicial — PC-001

## Objetivo
Realizar um teste de funcionamento do pipeline usando somente a categoria `bottle`.

## Resultado

| Métrica | Resultado |
|---|---:|
| Image AUROC | 1.000 |
| Full Pixel AUROC | 0.9849 |
| Anomaly Pixel AUROC | 0.9796 |

## Interpretação

O experimento confirmou o funcionamento completo do pipeline:

```text
dataset
→ extração de features
→ construção do memory bank
→ inferência
→ anomaly score
→ anomaly map
→ cálculo de métricas
```

O resultado também foi reproduzido posteriormente durante a execução completa das 15 categorias, indicando consistência do pipeline.

---

# 5. Experimento completo — PC-002

## Objetivo
Executar o PatchCore sobre todas as 15 categorias do MVTec AD utilizando a mesma configuração validada no PC-001.

## Resultados por categoria

| Categoria | Image AUROC | Full Pixel AUROC | Anomaly Pixel AUROC |
|---|---:|---:|---:|
| bottle | 1.0000 | 0.9849 | 0.9796 |
| cable | 0.9979 | 0.9837 | 0.9748 |
| capsule | 0.9809 | 0.9895 | 0.9874 |
| carpet | 0.9852 | 0.9907 | 0.9881 |
| grid | 0.9774 | 0.9877 | 0.9834 |
| hazelnut | 1.0000 | 0.9867 | 0.9790 |
| leather | 1.0000 | 0.9928 | 0.9903 |
| metal_nut | 0.9980 | 0.9833 | 0.9791 |
| pill | 0.9681 | 0.9782 | 0.9762 |
| screw | 0.9805 | 0.9953 | 0.9939 |
| tile | 0.9960 | 0.9572 | 0.9408 |
| toothbrush | 1.0000 | 0.9858 | 0.9801 |
| transistor | 0.9996 | 0.9628 | 0.9294 |
| wood | 0.9904 | 0.9503 | 0.9370 |
| zipper | 0.9924 | 0.9888 | 0.9858 |
| **Média** | **0.9911** | **0.9812** | **0.9737** |

## Tempo de execução

```text
real    11m50,846s
user    35m11,855s
sys     7m3,790s
```

Para o relatório, registrar como tempo principal:

> **Tempo total de execução: aproximadamente 11 min 51 s.**

O valor `real` representa o tempo de parede. Os valores `user` e `sys` podem ultrapassar o tempo total devido à execução multithread/multiprocesso.

---

# 6. Comparação com a baseline oficial

A configuração oficial reporta aproximadamente:

| Métrica | Oficial | Reprodução local | Diferença |
|---|---:|---:|---:|
| Image AUROC | 0.9920 | 0.9911 | -0.0009 |
| Pixel AUROC | 0.9810 | 0.9812 | +0.0002 |

## Interpretação

A diferença entre os resultados oficiais e os obtidos localmente é mínima. Portanto, a reprodução pode ser considerada bem-sucedida.

### Texto sugerido para o relatório

> A implementação oficial do PatchCore foi reproduzida sobre as 15 categorias do MVTec AD utilizando a configuração de resolução 224×224 proposta pelos autores. A média obtida foi de 0,9911 de AUROC em nível de imagem e 0,9812 em nível de pixel. Esses valores são muito próximos aos resultados reportados pela implementação oficial, de aproximadamente 0,992 e 0,981, respectivamente. A diferença observada foi inferior a 0,1 ponto percentual para Image AUROC e inferior a 0,02 ponto percentual para Pixel AUROC, indicando uma reprodução consistente da baseline.

---

# 7. Principais observações quantitativas

Os resultados mostram que o PatchCore apresenta desempenho muito alto no MVTec AD, mas também evidenciam que **detecção em nível de imagem e localização em nível de pixel não são equivalentes**.

## Exemplos importantes

### `transistor`
- Image AUROC: **0.9996**
- Anomaly Pixel AUROC: **0.9294**

O método identifica com grande confiança que a imagem é anômala, mas apresenta menor precisão para localizar exatamente os pixels da região defeituosa.

### `screw`
- Image AUROC: **0.9805**
- Anomaly Pixel AUROC: **0.9939**

O comportamento é quase inverso: a detecção em nível de imagem é ligeiramente menos forte, enquanto a localização é extremamente precisa.

### `pill`
- Image AUROC: **0.9681**
- menor Image AUROC entre as categorias

### `wood`
- Full Pixel AUROC: **0.9503**
- menor Full Pixel AUROC entre as categorias

### `leather`
- Image AUROC: **1.000**
- Full Pixel AUROC: **0.9928**

Representa um caso de desempenho elevado tanto em detecção quanto em localização.

---

# 8. Estratégia da análise qualitativa

A análise qualitativa não foi feita escolhendo imagens aleatórias. Foram selecionadas categorias que representassem diferentes comportamentos observados quantitativamente.

| Categoria | Motivo da seleção |
|---|---|
| transistor | detecção quase perfeita, mas localização inferior |
| wood | menor Full Pixel AUROC |
| tile | localização relativamente fraca em textura repetitiva |
| pill | menor Image AUROC |
| leather | controle positivo em categoria de textura |
| screw | controle positivo em categoria de objeto |

Essa estratégia permite discutir tanto os casos de falha quanto os casos de sucesso.

---

# 9. Análise qualitativa — `transistor`

## Caso analisado
Anomalias do tipo `misplaced`.

## Resultado observado

Nos exemplos analisados, o ground truth cobre grande parte do transistor, enquanto o anomaly map do PatchCore apresenta ativações mais concentradas em:

- bordas;
- terminais metálicos;
- regiões de maior contraste;
- partes específicas do componente.

Os mapas são relativamente difusos e não cobrem de forma homogênea toda a região indicada pelo ground truth.

## Interpretação

O PatchCore consegue perceber claramente que o objeto está fora do padrão normal, porém não delimita com igual precisão toda a região anômala.

Isso ajuda a explicar o contraste entre:

```text
Image AUROC = 0.9996
Anomaly Pixel AUROC = 0.9294
```

## Texto sugerido para o relatório

> Na categoria `transistor`, a análise qualitativa indica que o PatchCore apresenta excelente capacidade de detecção de anomalias em nível de imagem, porém menor precisão na localização em nível de pixel. Nas amostras da classe `misplaced`, o mapa de anomalia concentra ativações principalmente sobre o transistor e seus terminais, evidenciando que o método reconhece o desvio em relação ao padrão normal. Entretanto, tais ativações tendem a ser difusas e parcialmente desalinhadas em relação à máscara de ground truth, o que reduz o desempenho de segmentação. Esse comportamento sugere que, embora o método seja eficaz para indicar a presença de uma anomalia, ele possui limitações para delimitar precisamente anomalias cuja natureza envolve alterações globais de posição ou orientação.

## Imagem recomendada para o relatório

Inserir **uma das imagens de `transistor/pior_localizacao`**, preferencialmente:

```text
01_misplaced_005.png
```

ou a terceira imagem, em que a rotação do transistor é visualmente evidente.

### Legenda sugerida

> **Figura X — Exemplo de anomalia do tipo `misplaced` na categoria `transistor`.** O PatchCore detecta fortemente a presença da anomalia, porém o mapa apresenta ativação difusa e parcialmente desalinhada em relação à máscara de referência.

---

# 10. Análise qualitativa — `wood`

## Caso analisado
Anomalias do tipo `scratch`.

## Resultado observado

Os defeitos são finos, lineares e inseridos em uma superfície cuja textura natural já possui:

- veios;
- linhas;
- mudanças de tonalidade;
- estruturas alongadas.

O PatchCore tende a gerar mapas mais largos e suavizados que os riscos reais.

## Interpretação

O método identifica regiões suspeitas da superfície, mas tem dificuldade em separar com precisão:

```text
risco real
versus
estrutura natural da madeira
```

Essa dificuldade é particularmente visível quando o defeito ocupa poucos pixels.

## Texto sugerido para o relatório

> Na categoria `wood`, a análise qualitativa indica que o PatchCore apresenta dificuldade para localizar com precisão anomalias do tipo `scratch`. Embora o método geralmente identifique a região da superfície onde o defeito está presente, os mapas de anomalia tendem a ser difusos e mais extensos que as máscaras de referência. Observa-se ainda que a textura natural da madeira, composta por veios e variações tonais, pode induzir ativações em regiões normais, reduzindo a seletividade espacial do método. Esse comportamento sugere que, para defeitos finos e lineares sobre superfícies texturizadas, o PatchCore mantém boa capacidade de indicar a presença de anomalia, porém com menor precisão na segmentação pixel a pixel.

## Imagem recomendada para o relatório

Inserir:

```text
02_scratch_001.png
```

Essa imagem é especialmente clara porque o ground truth marca uma estrutura extremamente fina, enquanto o anomaly map aparece mais amplo e difuso.

### Legenda sugerida

> **Figura X — Exemplo de dificuldade de localização na categoria `wood`.** O defeito real é estreito e linear, enquanto o mapa de anomalia apresenta resposta espacial mais ampla e menos precisa.

---

# 11. Análise qualitativa — `tile`

## Casos analisados
- `gray_stroke`
- `glue_strip`

## Resultado observado

Nos exemplos `gray_stroke`, os mapas do PatchCore mostraram-se pouco discriminativos, apresentando ativações suaves e espalhadas sobre praticamente toda a superfície.

Em `glue_strip`, a região alterada é mais extensa e o modelo responde melhor, embora tenda a enfatizar as transições e bordas da região anômala.

## Interpretação

A textura repetitiva e granulada da categoria `tile` dificulta a distinção entre pequenas alterações defeituosas e variações normais da superfície.

## Texto sugerido para o relatório

> Na categoria `tile`, a análise qualitativa indica que o PatchCore apresenta limitações na segmentação de anomalias sobre superfícies com textura repetitiva. Nos exemplos analisados, especialmente do tipo `gray_stroke`, os mapas de anomalia mostraram-se difusos e pouco discriminativos, com baixa correspondência espacial em relação às máscaras de ground truth. Tal comportamento sugere que a forte variabilidade local da textura dificulta a distinção entre padrões normais e regiões defeituosas. Em contrapartida, em anomalias mais extensas, como `glue_strip`, o método consegue identificar de forma aproximada a região anômala, embora ainda privilegie bordas e transições em vez de segmentar uniformemente toda a área alterada.

## Imagens recomendadas para o relatório

Inserir duas imagens lado a lado:

```text
01_gray_stroke_012.png
03_glue_strip_003.png
```

A primeira representa um caso de falha severa; a segunda mostra uma situação em que a anomalia maior é melhor localizada.

### Legenda sugerida

> **Figura X — Comparação entre anomalias de pequena e grande extensão na categoria `tile`.** À esquerda, um caso de `gray_stroke` com baixa correspondência espacial; à direita, um caso de `glue_strip`, no qual a região anômala é identificada de forma mais clara.

---

# 12. Análise qualitativa — `pill`

## Casos analisados
Foram comparados:

```text
anomalias_menor_score
```

com:

```text
normais_maior_score
```

Essa análise teve como objetivo estudar diretamente o motivo da redução no Image AUROC.

## Scores observados

### Imagens anômalas com menor score

| Tipo | Score |
|---|---:|
| crack | 0.059 |
| crack | 0.074 |
| color | 0.075 |

### Imagens normais com maior score

| Tipo | Score |
|---|---:|
| good | 0.211 |
| good | 0.181 |
| good | 0.173 |

## Interpretação

Algumas imagens normais recebem scores maiores do que algumas imagens realmente anômalas.

Isso revela uma sobreposição entre as distribuições de scores de normais e anômalas, reduzindo o Image AUROC.

A amostra `color` é particularmente importante:

```text
Image score = 0.075
Pixel AUROC = 0.999
```

Ou seja, a pequena alteração é localizada quase perfeitamente, mas o score global da imagem permanece baixo.

Esse caso demonstra que:

> uma localização espacial precisa não implica necessariamente uma forte separação da imagem no nível global.

## Texto sugerido para o relatório

> Na categoria `pill`, observou-se um comportamento distinto daquele identificado nas categorias com maior dificuldade de localização. Embora o desempenho em nível de pixel permaneça elevado, a categoria apresentou o menor Image AUROC entre as 15 classes avaliadas. A inspeção dos casos com menores scores de anomalia revelou defeitos de pequena extensão, como `crack` e `color`, aos quais o modelo atribuiu scores globais reduzidos. Em contraste, algumas imagens normais receberam scores superiores, aparentemente em decorrência da variabilidade natural da superfície da pílula, incluindo partículas, manchas e irregularidades locais. Esse comportamento evidencia uma maior sobreposição entre as distribuições de scores de imagens normais e anômalas. Particularmente, uma amostra do tipo `color` apresentou Pixel AUROC de 0,999 apesar de um score de imagem de apenas 0,075, demonstrando que uma localização espacial precisa não implica necessariamente elevada confiança na detecção em nível de imagem.

## Observação metodológica recomendada

> Os exemplos analisados correspondem aos extremos de menor score entre as imagens anômalas e maior score entre as imagens normais, tendo sido selecionados para investigar qualitativamente as regiões de maior sobreposição entre as duas distribuições. Portanto, não devem ser interpretados como representativos de todas as amostras da categoria.

## Imagens recomendadas para o relatório

Inserir lado a lado:

```text
03_color_000.png
01_good_023.png
```

A primeira é uma anomalia com score baixo e Pixel AUROC quase perfeito.
A segunda é uma imagem normal com score consideravelmente maior.

### Legenda sugerida

> **Figura X — Comparação entre uma imagem anômala de baixo score e uma imagem normal de alto score na categoria `pill`.** O exemplo evidencia a sobreposição entre as distribuições de scores de imagens normais e anômalas.

---

# 13. Análise qualitativa — `leather`

## Objetivo
Utilizar uma categoria de alto desempenho como controle positivo.

## Resultado observado

Mesmo os piores exemplos individuais de localização apresentam Pixel AUROC próximo de 0.98.

Os mapas se concentram claramente sobre:

- cortes;
- dobras;
- regiões localmente alteradas.

Há pouca ativação significativa em regiões normais.

## Comparação com `wood`

Embora ambas sejam categorias de textura, o comportamento é diferente:

### `wood`
Os defeitos finos podem se confundir com os próprios veios da superfície.

### `leather`
Cortes e dobras produzem alterações locais mais claramente distintas do padrão normal.

## Texto sugerido para o relatório

> Na categoria `leather`, utilizada como caso de referência devido ao elevado desempenho quantitativo, verificou-se que mesmo as amostras com menor Pixel AUROC apresentaram forte correspondência entre os mapas de anomalia e as máscaras de referência. Nos defeitos dos tipos `cut` e `fold`, o PatchCore concentrou suas maiores ativações nas regiões efetivamente alteradas, com reduzida resposta em áreas normais da textura. Embora os mapas apresentem suavização espacial e sejam mais extensos que as máscaras de ground truth, a localização permanece consistente. Esse comportamento contrasta com categorias como `wood` e `tile`, sugerindo que o método apresenta maior facilidade quando a anomalia produz alterações locais visualmente distintas em relação ao padrão normal da superfície.

Complemento:

> A comparação entre `leather` e `wood` indica ainda que a presença de uma superfície texturizada, isoladamente, não determina a dificuldade do método. Enquanto riscos finos na madeira podem se confundir com os veios naturais do material, cortes e dobras no couro introduzem padrões locais mais distintos, favorecendo a discriminação pelo PatchCore.

## Imagem recomendada para o relatório

Inserir:

```text
03_fold_004.png
```

É o exemplo visualmente mais claro de boa correspondência entre anomaly map e ground truth.

### Legenda sugerida

> **Figura X — Exemplo de localização bem-sucedida na categoria `leather`.** O mapa de anomalia acompanha de forma consistente a região da dobra indicada pelo ground truth.

---

# 14. Análise qualitativa — `screw`

## Objetivo
Utilizar uma categoria de objeto com excelente desempenho de localização como segundo controle positivo.

## Resultado observado

Os defeitos `thread_side` ocupam regiões muito pequenas da imagem.

Apesar disso, mesmo os piores exemplos individuais apresentaram:

```text
Pixel AUROC entre 0.933 e 0.958
```

Os anomaly maps são mais largos do que as pequenas máscaras do ground truth.

## Interpretação

O PatchCore consegue atribuir scores relativamente altos às regiões defeituosas, porém a representação espacial permanece suavizada.

Esse caso evidencia uma característica importante do Pixel AUROC:

> uma métrica elevada não exige correspondência perfeita de contorno entre anomaly map e ground truth.

## Texto sugerido para o relatório

> Na categoria `screw`, que apresentou um dos melhores desempenhos de localização do experimento, os piores casos individuais ainda mantiveram Pixel AUROC superior a 0,93. Nas amostras do tipo `thread_side`, as regiões anotadas como anômalas ocupam áreas reduzidas da imagem, enquanto os mapas produzidos pelo PatchCore apresentam respostas espacialmente mais amplas e suavizadas. Apesar dessa diferença geométrica, os elevados valores de AUROC indicam que os pixels pertencentes aos defeitos tendem a receber scores superiores aos pixels normais. Esse resultado evidencia que uma elevada métrica de Pixel AUROC não implica necessariamente uma delimitação precisa dos contornos da anomalia, uma vez que a métrica avalia principalmente a capacidade de discriminação entre pixels normais e anômalos.

## Imagem recomendada para o relatório

Inserir:

```text
01_thread_side_000.png
```

### Legenda sugerida

> **Figura X — Exemplo de anomalia pequena na categoria `screw`.** Apesar do elevado Pixel AUROC, o mapa de anomalia apresenta resposta mais ampla que a região anotada no ground truth.

---

# 15. Discussão consolidada da análise qualitativa

Os casos analisados mostram que não existe uma única limitação responsável por todos os erros do PatchCore.

Foram identificados diferentes padrões:

| Categoria | Fenômeno principal |
|---|---|
| transistor | anomalia global/estrutural detectada, mas localizada de forma menos precisa |
| wood | defeitos finos confundidos com a textura natural |
| tile | baixa discriminação em textura repetitiva |
| pill | sobreposição entre scores de normais e anômalas |
| leather | forte separabilidade local entre normal e defeito |
| screw | boa discriminação de pequenos defeitos, mas mapas espacialmente suavizados |

## Texto sugerido para o relatório

> A análise qualitativa revelou que as limitações do PatchCore variam conforme a natureza da categoria e do defeito. Em `transistor`, o método apresenta forte detecção global, mas menor precisão espacial em anomalias associadas à posição e orientação do objeto. Em `wood` e `tile`, as principais dificuldades estão relacionadas à textura da superfície, seja pela semelhança entre defeitos finos e padrões naturais, seja pela alta repetitividade visual. Em `pill`, observou-se maior sobreposição entre os scores de imagens normais e anômalas, afetando a capacidade de detecção em nível de imagem. Por outro lado, categorias como `leather` e `screw` demonstraram elevada separabilidade entre padrões normais e defeituosos, resultando em mapas de anomalia mais consistentes.

Complemento:

> Esses resultados reforçam a importância de avaliar simultaneamente métricas em nível de imagem e em nível de pixel, bem como complementar a avaliação quantitativa com inspeção visual dos mapas de anomalia. Casos como `pill` demonstram que uma boa localização pode coexistir com baixo score global, enquanto `transistor` evidencia o comportamento inverso. Além disso, exemplos de `screw` mostram que um Pixel AUROC elevado não implica necessariamente uma segmentação geometricamente precisa do defeito.

---

# 16. Conclusões da primeira baseline

## Principais conclusões

1. A implementação oficial do PatchCore foi reproduzida com sucesso.
2. Os resultados quantitativos ficaram muito próximos dos valores oficiais.
3. O método apresentou excelente desempenho médio no MVTec AD.
4. Detecção em nível de imagem e localização em nível de pixel apresentaram comportamentos distintos em algumas categorias.
5. Defeitos finos, texturas repetitivas e variações locais naturais podem reduzir a precisão dos mapas.
6. Categorias com alterações locais fortemente diferenciadas do padrão normal apresentaram os melhores resultados.
7. A análise qualitativa mostrou limitações que não são evidentes apenas pelas médias globais.

## Texto sugerido para o relatório

> A reprodução do PatchCore confirmou sua elevada capacidade de detecção e localização de anomalias no MVTec AD. Os resultados obtidos foram consistentes com os valores reportados na implementação oficial, validando o ambiente experimental utilizado. Entretanto, a análise por categoria e a inspeção dos mapas de anomalia mostraram que o desempenho médio elevado não elimina limitações específicas. O método apresenta maior dificuldade em situações envolvendo defeitos muito pequenos, padrões texturais complexos ou alterações de caráter mais global. Em contrapartida, quando a anomalia produz uma diferença local clara em relação às características normais armazenadas no memory bank, a localização tende a ser altamente precisa.

---

# 17. Estrutura recomendada para o relatório

A seção da baseline PatchCore pode ser organizada da seguinte forma:

```text
X. Baseline de Visão Computacional — PatchCore

X.1. Método e configuração experimental
X.2. Ambiente de execução
X.3. Reprodução no MVTec AD
X.4. Resultados quantitativos
X.5. Comparação com os resultados oficiais
X.6. Análise qualitativa
    X.6.1. Transistor
    X.6.2. Wood
    X.6.3. Tile
    X.6.4. Pill
    X.6.5. Leather
    X.6.6. Screw
X.7. Discussão
X.8. Conclusões da baseline
```

Se o relatório precisar ser mais curto, utilizar:

```text
X. Baseline PatchCore
X.1. Configuração experimental
X.2. Resultados quantitativos
X.3. Análise qualitativa
X.4. Discussão
```

---

# 18. Imagens recomendadas para o relatório final

Não é necessário inserir todas as imagens analisadas.

Uma seleção equilibrada seria:

## Figura 1 — `transistor`
Arquivo:

```text
transistor/pior_localizacao/01_misplaced_005.png
```

Objetivo:
mostrar detecção forte, mas localização menos precisa.

## Figura 2 — `wood`
Arquivo:

```text
wood/pior_localizacao/02_scratch_001.png
```

Objetivo:
mostrar dificuldade com defeito fino.

## Figura 3 — `tile`
Arquivos:

```text
tile/pior_localizacao/01_gray_stroke_012.png
tile/pior_localizacao/03_glue_strip_003.png
```

Objetivo:
comparar anomalia pequena/difícil com anomalia grande/mais evidente.

## Figura 4 — `pill`
Arquivos:

```text
pill/anomalias_menor_score/03_color_000.png
pill/normais_maior_score/01_good_023.png
```

Objetivo:
mostrar sobreposição entre scores normais e anômalos.

## Figura 5 — `leather`
Arquivo:

```text
leather/pior_localizacao/03_fold_004.png
```

Objetivo:
mostrar um caso de localização bem-sucedida.

## Figura 6 — `screw`
Arquivo:

```text
screw/pior_localizacao/01_thread_side_000.png
```

Objetivo:
mostrar que Pixel AUROC elevado não significa contorno perfeito.

---

# 19. Tabelas recomendadas para o relatório

## Tabela principal
Inserir a tabela completa com as 15 categorias e as três métricas.

## Tabela resumida opcional
Se o relatório estiver ficando muito extenso, incluir também uma tabela menor na discussão:

| Categoria | Image AUROC | Pixel AUROC | Principal observação |
|---|---:|---:|---|
| transistor | 0.9996 | 0.9628 | detecção excelente, localização inferior |
| wood | 0.9904 | 0.9503 | dificuldade com scratches finos |
| tile | 0.9960 | 0.9572 | textura repetitiva |
| pill | 0.9681 | 0.9782 | maior sobreposição normal/anômalo |
| leather | 1.0000 | 0.9928 | controle positivo |
| screw | 0.9805 | 0.9953 | localização muito forte |

---

# 20. O que não deve ser afirmado de forma absoluta

Evitar frases como:

```text
"O PatchCore não entende contexto."
"O PatchCore falha em anomalias globais."
"O PatchCore sempre se confunde com textura."
```

Essas afirmações seriam fortes demais para o conjunto de observações realizado.

Preferir:

```text
"Os exemplos analisados sugerem..."
"Foi observada maior dificuldade..."
"O comportamento indica uma possível limitação..."
"Nos casos inspecionados..."
```

Também evitar chamar diretamente os casos de `pill` de falso positivo ou falso negativo sem antes definir um threshold operacional.

---

# 21. Observações sobre as métricas

## Image AUROC
Avalia a capacidade de ordenar imagens anômalas acima de imagens normais.

## Pixel AUROC
Avalia a capacidade de atribuir scores superiores a pixels anômalos em relação aos pixels normais.

## Importante
Pixel AUROC elevado **não significa necessariamente boa sobreposição geométrica**.

Um mapa pode ser mais amplo que o ground truth e ainda apresentar AUROC alto.

Por isso, a inspeção qualitativa é importante.

---

# 22. Estado da baseline

## Situação atual

```text
PatchCore
├── Ambiente configurado        ✅
├── Código oficial registrado   ✅
├── Smoke test bottle           ✅
├── 15 categorias executadas    ✅
├── Resultados quantitativos    ✅
├── Comparação oficial          ✅
├── Análise qualitativa         ✅
└── Documentação                ✅
```

## Conclusão

A primeira baseline pode ser considerada **reproduzida, avaliada e documentada**.

O próximo passo experimental recomendado é iniciar a segunda baseline utilizando o mesmo protocolo de registro:

```text
configuração
→ reprodução
→ resultados quantitativos
→ comparação com valores reportados
→ análise qualitativa
→ discussão
```

Isso permitirá posteriormente realizar uma comparação controlada entre diferentes métodos de Visão Computacional.
