# Documentação da Segunda Baseline — EfficientAD-M no MVTec AD

> **Objetivo deste documento:** registrar toda a reprodução, avaliação quantitativa e análise qualitativa da segunda baseline do projeto, além de indicar **o que deve ser incorporado ao relatório principal**, quais títulos usar, quais textos podem ser aproveitados e quais imagens são mais adequadas para ilustrar os resultados.

---

# 1. Identificação da baseline

## Método
**EfficientAD-M**

## Implementação utilizada
Implementação pública **não oficial** disponível no repositório `nelson1425/EfficientAD`.

## Commit utilizado
```text
fcab5146f84ae17597044ad5ddf1656ccf805401
```

## Dataset principal
**MVTec AD**

## Categorias avaliadas
Todas as 15 categorias do MVTec AD:

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

O EfficientAD-M foi executado em um ambiente Linux dedicado e separado do ambiente utilizado no PatchCore.

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
- **Teacher:** `teacher_medium.pth`
- **Configuração:** EfficientAD-M

## Observação metodológica

A implementação utilizada não é a implementação oficial dos autores do EfficientAD. O ambiente original indicado pelo repositório também não foi reproduzido literalmente, pois versões mais antigas de PyTorch não eram adequadas para a GPU utilizada. Dessa forma, foi preservado o código da implementação escolhida, mas executado em uma pilha moderna de Python/PyTorch compatível com a RTX 5060.

### Como escrever isso no relatório

> Para a reprodução do EfficientAD-M foi utilizada uma implementação pública não oficial, com o código mantido no commit `fcab5146f84ae17597044ad5ddf1656ccf805401`. O ambiente original da implementação foi adaptado para versões atuais de Python e PyTorch, necessárias para compatibilidade com o hardware utilizado. Todas as alterações de ambiente foram registradas para fins de reprodutibilidade.

---

# 3. Dataset externo para penalty loss

O EfficientAD utiliza imagens externas durante o treinamento para compor a **penalty loss**. Para manter a reprodução próxima do protocolo de referência, foi utilizado o conjunto de treinamento do ImageNet.

## Estrutura utilizada

```text
~/IC/datasets/imagenet/ILSVRC/Data/CLS-LOC/train
```

## Validação realizada

O diretório continha:

```text
1000 classes
aproximadamente 1,28 milhão de imagens
```

## Uso no experimento

O caminho foi fornecido ao treinamento com:

```text
--imagenet_train_path ~/IC/datasets/imagenet/ILSVRC/Data/CLS-LOC/train
```

### Texto sugerido para o relatório

> O treinamento do EfficientAD-M utilizou o conjunto de treinamento do ImageNet como fonte externa para a penalty loss, seguindo o protocolo de reprodução adotado pela implementação utilizada. O conjunto foi organizado em 1.000 classes e empregado apenas como fonte de imagens externas ao domínio industrial, sem utilização de seus rótulos no processo de detecção de anomalias.

---

# 4. Configuração experimental

## Hiperparâmetros principais

| Parâmetro | Valor |
|---|---:|
| Variante | EfficientAD-M |
| Teacher | `teacher_medium.pth` |
| Número de passos | 70.000 |
| Penalty dataset | ImageNet train |
| Dataset principal | MVTec AD |
| Avaliação de detecção | Image AUROC |
| Avaliação de localização | AU-PRO, FPR ≤ 0,3 |

## Observação

Diferentemente do PatchCore, o EfficientAD executa treinamento convencional envolvendo Student e Autoencoder.

---

# 5. Experimento inicial — EA-001

## Objetivo
Executar um smoke test para validar:

```text
dataset
→ teacher
→ student
→ autoencoder
→ backpropagation
→ GPU
→ anomaly maps
→ AUROC
```

## Configuração

- Categoria: `bottle`
- Passos: 1.000
- ImageNet penalty: desabilitada
- Variante: EfficientAD-M

## Resultado

```text
Final Image AUROC: 97,7778%
Tempo total: 1m25,017s
```

## Interpretação

Esse resultado **não deve ser utilizado como baseline científica**, pois o experimento foi reduzido propositalmente e não utilizou a penalty loss do ImageNet.

### Texto sugerido para o relatório

> Inicialmente foi realizado um smoke test com 1.000 passos na categoria `bottle`, sem penalty loss do ImageNet, com o objetivo exclusivo de validar o pipeline de treinamento e inferência. Como essa execução não corresponde ao protocolo completo do método, seus resultados não foram utilizados na comparação final.

---

# 6. Experimento completo de validação — EA-002

## Objetivo
Executar o protocolo completo do EfficientAD-M na categoria `bottle` antes de escalar para todas as classes.

## Configuração

- Categoria: `bottle`
- Passos: 70.000
- ImageNet penalty: habilitada
- Teacher: `teacher_medium.pth`

## Resultado de detecção

```text
Image AUROC: 1,0000
```

## Resultado da avaliação oficial da MVTec

```text
AU-PRO @ FPR ≤ 0,3: 0,957444
Image-level AUROC: 1,0000
```

## Tempo total

```text
127m6,782s
```

ou aproximadamente:

```text
2h 07m 07s
```

## Interpretação

O EA-002 validou o pipeline completo:

```text
treinamento
→ geração dos anomaly maps
→ avaliação oficial da MVTec
→ métricas de detecção e localização
```

---

# 7. Experimento completo — EA-003

## Objetivo
Executar o EfficientAD-M nas 14 categorias restantes do MVTec AD, utilizando exatamente o mesmo protocolo do EA-002.

## Resultado consolidado

| Categoria | Image AUROC | AU-PRO (FPR ≤ 0,3) | Tempo |
|---|---:|---:|---:|
| bottle | 1.000000 | 0.957444 | 2h 07m 07s |
| cable | 0.933846 | 0.914445 | 2h 06m 10s |
| capsule | 0.976865 | 0.970248 | 2h 04m 42s |
| carpet | 0.994382 | 0.929671 | 2h 03m 14s |
| grid | 1.000000 | 0.890507 | 2h 01m 33s |
| hazelnut | 1.000000 | 0.951261 | 2h 01m 53s |
| leather | 1.000000 | 0.982097 | 2h 02m 04s |
| metal_nut | 0.996579 | 0.942391 | 2h 01m 58s |
| pill | 0.991271 | 0.964890 | 2h 01m 54s |
| screw | 0.964952 | 0.965948 | 1h 59m 30s |
| tile | 0.999639 | 0.884586 | 2h 00m 04s |
| toothbrush | 1.000000 | 0.932548 | 2h 06m 47s |
| transistor | 1.000000 | 0.912075 | 2h 01m 25s |
| wood | 0.995614 | 0.903694 | 1h 59m 15s |
| zipper | 0.997637 | 0.940856 | 2h 03m 48s |
| **Média** | **0.990052** | **0.936177** | — |

## Tempo total acumulado

Somando as 15 execuções:

```text
aproximadamente 30h 41m 22s
```

## Observação

Esse valor representa o tempo acumulado das execuções individuais. Ele é útil para caracterizar o custo experimental da baseline.

---

# 8. Comparação com o valor de referência da implementação

A implementação utilizada reporta aproximadamente:

```text
Image AUROC médio: 0,991
```

A reprodução local obteve:

```text
Image AUROC médio: 0,990052
```

Diferença aproximada:

```text
-0,000948
```

ou cerca de:

```text
-0,095 ponto percentual
```

## Interpretação

A diferença é pequena e indica que a reprodução ficou muito próxima do valor de referência divulgado pela implementação utilizada.

### Texto sugerido para o relatório

> A reprodução do EfficientAD-M obteve Image AUROC médio de 0,9901 no MVTec AD, valor muito próximo ao resultado de aproximadamente 0,991 reportado pela implementação utilizada como referência. A diferença ficou abaixo de 0,1 ponto percentual, indicando consistência entre a reprodução local e o desempenho esperado do método.

## Atenção
No relatório, deixar explícito que a comparação é com a **implementação pública não oficial utilizada na reprodução**, e não afirmar que o repositório é oficial dos autores.

---

# 9. Principais observações quantitativas

## Pior detecção em nível de imagem

### `cable`

```text
Image AUROC = 0,933846
AU-PRO = 0,914445
```

Foi a menor Image AUROC entre as 15 categorias.

---

## Detecção relativamente baixa, mas localização forte

### `screw`

```text
Image AUROC = 0,964952
AU-PRO = 0,965948
```

A categoria mostra um contraste importante entre desempenho global e capacidade de localização.

---

## Detecção praticamente perfeita, mas localização inferior

### `tile`

```text
Image AUROC = 0,999639
AU-PRO = 0,884586
```

Foi o menor AU-PRO entre as categorias.

### `grid`

```text
Image AUROC = 1,000000
AU-PRO = 0,890507
```

### `transistor`

```text
Image AUROC = 1,000000
AU-PRO = 0,912075
```

Esses casos demonstram que classificar corretamente uma imagem como anômala não implica necessariamente segmentar bem a região da anomalia.

---

## Controle positivo

### `leather`

```text
Image AUROC = 1,000000
AU-PRO = 0,982097
```

Representa um dos melhores resultados conjuntos de detecção e localização.

---

# 10. Estratégia da análise qualitativa

A análise qualitativa foi dirigida pelos resultados quantitativos, evitando escolha arbitrária de exemplos.

| Categoria | Motivo da seleção |
|---|---|
| tile | pior AU-PRO |
| grid | Image AUROC perfeito, mas AU-PRO baixo |
| cable | pior Image AUROC |
| screw | Image AUROC menor, mas AU-PRO elevado |
| leather | controle positivo |

## Critérios usados

Foram analisados:

```text
pior_localizacao
anomalias_menor_score
normais_maior_score
```

dependendo do fenômeno investigado.

---

# 11. Análise qualitativa — `tile`

## Resultado quantitativo

```text
Image AUROC = 0,999639
AU-PRO = 0,884586
```

## Casos analisados
`gray_stroke`

## Observação principal

O EfficientAD-M normalmente identifica a região correta, porém tende a gerar mapas **menores que a região anotada**, cobrindo apenas a parte mais discriminativa da anomalia.

Esse comportamento caracteriza:

```text
subsegmentação
```

## Padrão observado

- região correta identificada;
- ativação espacialmente compacta;
- cobertura parcial do ground truth;
- boa detecção em nível de imagem;
- menor precisão na extensão da anomalia.

## Texto sugerido para o relatório

> Na categoria `tile`, o EfficientAD-M apresentou elevada capacidade de detecção em nível de imagem, com Image AUROC próximo de 1,0, porém desempenho inferior em localização, com AU-PRO de 0,8846. A análise qualitativa das amostras do tipo `gray_stroke` mostra que o método geralmente identifica a região onde a anomalia está presente, mas tende a produzir mapas mais compactos que as máscaras de referência. Em diversos casos, apenas uma parcela da região anotada recebe elevada resposta de anomalia, indicando subsegmentação do defeito. Esse comportamento ajuda a explicar a diferença entre a quase perfeita capacidade de classificação da imagem e o desempenho mais limitado de localização espacial.

## Comparação com PatchCore

> Em comparação ao PatchCore, que apresentou mapas mais difusos nessa mesma categoria, o EfficientAD-M produz respostas visualmente mais concentradas, porém frequentemente cobre apenas as regiões mais discriminativas da anomalia. Assim, ambos apresentam limitações em `tile`, mas com padrões qualitativamente diferentes.

## Imagem recomendada para o relatório

```text
tile/pior_localizacao/01_gray_stroke_002.png
```

### Legenda sugerida

> **Figura X — Exemplo de subsegmentação do EfficientAD-M na categoria `tile`.** O método identifica corretamente parte da região anômala, porém o mapa cobre uma área significativamente menor que o ground truth.

---

# 12. Análise qualitativa — `grid`

## Resultado quantitativo

```text
Image AUROC = 1,000000
AU-PRO = 0,890507
```

## Casos analisados
- `glue`
- `broken`

## Padrões observados

### Subsegmentação
O método pode cobrir apenas parte da região anotada.

### Detecção parcial
Quando há múltiplas regiões defeituosas desconectadas, algumas podem ser ignoradas.

### Ativações secundárias
A textura repetitiva da grade pode produzir respostas fora do defeito principal.

## Texto sugerido para o relatório

> Na categoria `grid`, o EfficientAD-M apresentou Image AUROC de 1,0, indicando separação perfeita entre imagens normais e anômalas, porém obteve AU-PRO de 0,8905, revelando maior dificuldade na localização espacial. A análise qualitativa mostra que o método pode identificar somente parte das regiões anotadas como anômalas, principalmente quando o defeito é composto por múltiplas áreas desconectadas. Também foram observadas respostas secundárias em regiões normais da textura repetitiva da grade. Dessa forma, a presença de uma evidência anômala suficientemente forte para a classificação da imagem não implica necessariamente cobertura completa da região defeituosa.

Complemento:

> Assim como em `tile`, observou-se tendência à subsegmentação. Entretanto, em `grid` também ocorreram casos em que apenas uma entre múltiplas regiões anômalas foi destacada, além de ativações secundárias distribuídas sobre a textura normal.

## Imagem recomendada para o relatório

```text
grid/pior_localizacao/02_broken_002.png
```

### Legenda sugerida

> **Figura X — Exemplo de localização parcial do EfficientAD-M na categoria `grid`.** O ground truth contém múltiplas regiões defeituosas, enquanto o anomaly map concentra sua resposta em apenas uma delas.

---

# 13. Análise qualitativa — `cable`

## Resultado quantitativo

```text
Image AUROC = 0,933846
AU-PRO = 0,914445
```

## Objetivo
Investigar por que `cable` apresentou a menor Image AUROC.

## Scores analisados

### Anomalias com menor score normalizado

| Tipo | Score |
|---|---:|
| poke_insulation | 0,049 |
| missing_wire | 0,064 |
| poke_insulation | 0,069 |

### Imagens normais com maior score normalizado

| Tipo | Score |
|---|---:|
| good | 1,000 |
| good | 0,309 |
| good | 0,211 |

## Observação principal

Algumas imagens normais recebem scores significativamente maiores do que determinadas imagens anômalas.

Como a normalização aplicada para inspeção preserva a ordem dos scores, isso revela inversões reais no ranking.

## Localização das anomalias

Apesar dos baixos scores globais, as amostras anômalas apresentaram Pixel AUROC individual elevado:

```text
0,950
0,983
0,946
```

Isso mostra que o modelo consegue localizar o defeito sem necessariamente atribuir à imagem um score global elevado.

## Interpretação

A categoria apresenta grande variabilidade visual interna:

- revestimento externo;
- três isolamentos coloridos;
- fios metálicos;
- reflexos;
- diferenças de posição;
- variações de brilho.

Nos casos analisados, algumas dessas variações normais receberam forte resposta do modelo.

## Texto sugerido para o relatório

> Na categoria `cable`, que apresentou o menor Image AUROC do EfficientAD-M (0,9338), a análise qualitativa revelou uma sobreposição relevante entre os scores atribuídos a imagens normais e anômalas. Algumas anomalias dos tipos `poke_insulation` e `missing_wire` receberam scores globais reduzidos, apesar de apresentarem elevada discriminação em nível de pixel, com Pixel AUROC individual entre 0,946 e 0,983. Em contraste, algumas imagens normais receberam scores consideravelmente superiores, incluindo uma amostra com o maior score normalizado da categoria. Os anomaly maps dessas imagens normais apresentaram ativações principalmente em regiões de fios metálicos, reflexos e transições locais de aparência, sugerindo sensibilidade do modelo à variabilidade visual legítima do cabo. Esses casos ajudam a explicar a redução do desempenho em nível de imagem, uma vez que o AUROC é afetado por inversões no ranking entre amostras normais e anômalas.

Complemento:

> Os exemplos também demonstram que localização e classificação global devem ser analisadas separadamente. Em particular, uma amostra `missing_wire` apresentou Pixel AUROC de 0,983 apesar de um score global normalizado de apenas 0,064, indicando que uma anomalia pode ser espacialmente bem localizada sem necessariamente receber elevada confiança em nível de imagem.

## Imagens recomendadas para o relatório

```text
cable/anomalias_menor_score/02_missing_wire_000.png
cable/normais_maior_score/01_good_042.png
```

### Legenda sugerida

> **Figura X — Sobreposição de scores entre amostras normais e anômalas na categoria `cable`.** À esquerda, uma imagem `missing_wire` com baixo score global apesar da elevada localização do defeito; à direita, uma imagem normal que recebeu elevada resposta de anomalia em uma região visualmente variável do condutor.

## Observação metodológica

Evitar chamar diretamente esses casos de falso positivo ou falso negativo, pois não foi definido um threshold operacional de decisão.

Usar:

```text
anomalia de menor score
imagem normal de maior score
```

---

# 14. Análise qualitativa — `screw`

## Resultado quantitativo

```text
Image AUROC = 0,964952
AU-PRO = 0,965948
```

## Casos analisados
Anomalias `thread_side` de pequena extensão.

## Scores analisados

### Anomalias com menor score normalizado

| Tipo | Score |
|---|---:|
| thread_side | 0,016 |
| thread_side | 0,018 |
| thread_side | 0,029 |

### Imagens normais com maior score normalizado

| Tipo | Score |
|---|---:|
| good | 0,139 |
| good | 0,106 |
| good | 0,057 |

## Pixel AUROC individual

```text
0,957
0,975
0,931
```

## Interpretação

Os defeitos são pequenos e recebem evidência absoluta reduzida, mas os pixels defeituosos ainda são bem ordenados em relação aos pixels normais.

Isso caracteriza outro caso de:

```text
boa localização
+
score global reduzido
```

## Texto sugerido para o relatório

> Na categoria `screw`, o EfficientAD-M apresentou AU-PRO elevado (0,9659), apesar de um Image AUROC comparativamente inferior (0,9650). A análise das amostras anômalas com menores scores revelou defeitos do tipo `thread_side` de pequena extensão espacial. Embora essas amostras apresentem Pixel AUROC individual entre 0,931 e 0,975, seus scores globais normalizados permaneceram entre 0,016 e 0,029. Em contraste, algumas imagens normais receberam scores entre 0,057 e 0,139. Esse comportamento evidencia inversões no ranking entre amostras normais e anômalas e ajuda a explicar a redução do Image AUROC. Os resultados mostram que o método pode discriminar adequadamente os pixels defeituosos dentro de uma imagem sem necessariamente atribuir à imagem um score global elevado.

Complemento:

> Assim, `screw` constitui outro exemplo de desacoplamento entre localização e classificação global: pequenos defeitos podem ser espacialmente identificados de forma consistente, mas produzir evidência absoluta insuficiente para separar todas as amostras anômalas das variações normais da categoria.

## Imagens recomendadas

```text
screw/anomalias_menor_score/02_thread_side_004.png
screw/normais_maior_score/01_good_004.png
```

### Legenda sugerida

> **Figura X — Contraste entre localização e detecção global na categoria `screw`.** À esquerda, uma pequena anomalia `thread_side` é bem discriminada espacialmente apesar do baixo score global; à direita, uma imagem normal recebe score superior devido a respostas locais do modelo.

---

# 15. Análise qualitativa — `leather`

## Resultado quantitativo

```text
Image AUROC = 1,000000
AU-PRO = 0,982097
```

## Objetivo
Utilizar uma categoria de alto desempenho como controle positivo.

## Casos analisados
`fold`

## Padrão observado

Mesmo nos piores casos individuais, o modelo normalmente encontra a região correta.

A principal limitação observada é:

```text
subsegmentação
```

ou seja, a resposta se concentra nas partes mais discriminativas da dobra em vez de cobrir toda a extensão anotada.

## Texto sugerido para o relatório

> Na categoria `leather`, utilizada como caso de alto desempenho, o EfficientAD-M apresentou Image AUROC de 1,0 e AU-PRO de 0,9821. A análise dos piores casos individuais de localização mostrou que o método identifica corretamente a região geral das anomalias do tipo `fold`, porém tende a concentrar a resposta nas partes mais discriminativas da dobra, cobrindo apenas parcialmente sua extensão total. Esse comportamento caracteriza uma forma de subsegmentação, ainda que a correspondência espacial permaneça elevada quando comparada às categorias mais difíceis. Os resultados indicam que, mesmo em uma categoria com excelente desempenho agregado, a inspeção qualitativa pode revelar diferenças entre detectar a região da anomalia e reproduzir precisamente seu contorno.

## Imagem recomendada

```text
leather/pior_localizacao/03_fold_009.png
```

### Legenda sugerida

> **Figura X — Exemplo de subsegmentação do EfficientAD-M na categoria `leather`.** O método identifica corretamente a região da dobra, porém concentra a resposta na porção visualmente mais discriminativa da anomalia, cobrindo apenas parcialmente a máscara de referência.

---

# 16. Discussão consolidada da análise qualitativa

A análise qualitativa mostrou que as limitações do EfficientAD-M variam conforme a natureza do problema.

| Categoria | Fenômeno principal |
|---|---|
| tile | subsegmentação de regiões anômalas |
| grid | subsegmentação, regiões parcialmente ignoradas e ativações secundárias |
| cable | sobreposição de scores normais e anômalos |
| screw | boa localização com score global baixo |
| leather | localização forte, mas ainda com subsegmentação nos piores casos |

## Texto sugerido para o relatório

> A análise qualitativa do EfficientAD-M revelou dois grupos principais de limitações. O primeiro está associado à localização espacial: em categorias como `tile` e `grid`, o método frequentemente identifica a região correta, mas cobre apenas a parte mais discriminativa da anomalia ou ignora algumas regiões defeituosas. O segundo está associado à detecção em nível de imagem: em `cable` e `screw`, foram observadas anomalias com baixo score global apesar de boa localização, além de imagens normais com scores superiores. Esses resultados reforçam que detecção e localização são tarefas relacionadas, porém não equivalentes.

Complemento:

> O caso de `leather` demonstra que, quando o defeito apresenta características locais claramente distintas do padrão normal, o EfficientAD-M consegue manter simultaneamente elevado desempenho de classificação e localização. Entretanto, mesmo nessa categoria, os piores exemplos evidenciam que o mapa pode enfatizar somente uma parcela da região anotada.

---

# 17. Comparação qualitativa preliminar com PatchCore

Essa comparação deve ser tratada como **qualitativa** até que as métricas sejam padronizadas entre os dois métodos.

## `tile`

### PatchCore
- mapas mais difusos;
- baixa seletividade espacial;
- dificuldade em distinguir defeito da textura.

### EfficientAD-M
- mapas mais focados;
- tendência a subsegmentar;
- cobre apenas a região mais discriminativa.

## `screw`

### PatchCore
- mapas mais amplos e suavizados;
- Pixel AUROC alto.

### EfficientAD-M
- mapas muito discretos em defeitos pequenos;
- boa discriminação interna, mas score global baixo.

## `leather`

Ambos apresentam bom desempenho, mas:

- PatchCore tende a produzir mapas mais suaves;
- EfficientAD-M tende a concentrar resposta nas partes mais distintivas.

## Texto sugerido

> A comparação visual preliminar sugere que PatchCore e EfficientAD-M podem apresentar falhas espaciais de naturezas diferentes. Em algumas categorias texturizadas, o PatchCore produz mapas mais difusos, enquanto o EfficientAD-M tende a gerar respostas mais concentradas e, em certos casos, subsegmentadas. Essa diferença reforça a importância de padronizar as métricas de localização antes de realizar uma comparação quantitativa direta entre as baselines.

---

# 18. Importante: métricas ainda não padronizadas entre as baselines

Até este ponto:

## PatchCore
Foi analisado inicialmente com:

```text
Image AUROC
Full Pixel AUROC
Anomaly Pixel AUROC
```

## EfficientAD-M
Foi avaliado oficialmente com:

```text
Image AUROC
AU-PRO @ FPR ≤ 0,3
```

Portanto, ainda **não deve ser feita uma comparação quantitativa direta de localização** usando Pixel AUROC de um lado e AU-PRO do outro.

## Próximo passo necessário

Gerar anomaly maps do PatchCore no formato aceito pelo avaliador oficial da MVTec e calcular:

```text
AU-PRO @ FPR ≤ 0,3
```

para as 15 categorias.

Depois disso, será possível comparar:

| Método | Image AUROC | AU-PRO |
|---|---:|---:|
| PatchCore | ... | ... |
| EfficientAD-M | 0,9901 | 0,9362 |

---

# 19. Conclusões da segunda baseline

## Principais conclusões

1. O EfficientAD-M foi executado com sucesso nas 15 categorias do MVTec AD.
2. O protocolo completo incluiu 70.000 passos e penalty loss com ImageNet.
3. O Image AUROC médio obtido foi **0,9901**.
4. O AU-PRO médio obtido foi **0,9362**.
5. O tempo acumulado de treinamento ficou em aproximadamente **30h 41m**.
6. O resultado médio de Image AUROC ficou muito próximo do valor de referência da implementação utilizada.
7. `cable` apresentou a maior dificuldade de detecção global.
8. `tile` e `grid` apresentaram forte contraste entre detecção quase perfeita e localização inferior.
9. `screw` evidenciou boa localização mesmo em anomalias de baixo score global.
10. `leather` funcionou como caso de alto desempenho conjunto.
11. A inspeção qualitativa confirmou que detecção e localização devem ser analisadas separadamente.

## Texto sugerido para o relatório

> A reprodução do EfficientAD-M apresentou desempenho elevado no MVTec AD, com Image AUROC médio de 0,9901 e AU-PRO médio de 0,9362. Os resultados ficaram próximos do valor de referência da implementação utilizada e confirmaram a viabilidade da reprodução no ambiente experimental disponível. A análise por categoria, entretanto, mostrou comportamentos distintos entre detecção e localização. Enquanto `tile` e `grid` apresentaram classificação praticamente perfeita das imagens, seus mapas de anomalia mostraram limitações de cobertura espacial. Em `cable` e `screw`, observou-se maior sobreposição entre scores de imagens normais e anômalas, mesmo quando os defeitos eram localizados de forma consistente. Esses resultados evidenciam a importância de complementar métricas agregadas com análise qualitativa e avaliação por categoria.

---

# 20. Estrutura recomendada para o relatório

Uma estrutura completa pode ser:

```text
X. Baseline de Visão Computacional — EfficientAD-M

X.1. Método e implementação utilizada
X.2. Ambiente experimental
X.3. Uso do ImageNet na penalty loss
X.4. Configuração de treinamento
X.5. Validação inicial
X.6. Reprodução no MVTec AD
X.7. Resultados quantitativos
X.8. Comparação com o valor de referência
X.9. Análise qualitativa
    X.9.1. Tile
    X.9.2. Grid
    X.9.3. Cable
    X.9.4. Screw
    X.9.5. Leather
X.10. Discussão
X.11. Conclusões da baseline
```

Se o relatório precisar ser mais compacto:

```text
X. Baseline EfficientAD-M
X.1. Configuração experimental
X.2. Resultados quantitativos
X.3. Análise qualitativa
X.4. Discussão
```

---

# 21. Imagens recomendadas para o relatório final

Não é necessário inserir todas as imagens analisadas.

## Figura 1 — `tile`

```text
tile/pior_localizacao/01_gray_stroke_002.png
```

Objetivo:
mostrar subsegmentação.

---

## Figura 2 — `grid`

```text
grid/pior_localizacao/02_broken_002.png
```

Objetivo:
mostrar detecção de apenas parte de uma anomalia composta.

---

## Figura 3 — `cable`

```text
cable/anomalias_menor_score/02_missing_wire_000.png
cable/normais_maior_score/01_good_042.png
```

Objetivo:
mostrar inversão de ranking entre anômala de baixo score e normal de alto score.

---

## Figura 4 — `screw`

```text
screw/anomalias_menor_score/02_thread_side_004.png
screw/normais_maior_score/01_good_004.png
```

Objetivo:
mostrar boa localização com baixo score global.

---

## Figura 5 — `leather`

```text
leather/pior_localizacao/03_fold_009.png
```

Objetivo:
mostrar um controle positivo de alta localização, ainda com subsegmentação nos casos mais difíceis.

---

# 22. Tabelas recomendadas para o relatório

## Tabela principal

Inserir as 15 categorias com:

```text
Image AUROC
AU-PRO
```

Tempo pode ser incluído em uma tabela separada ou em coluna opcional.

## Tabela resumida para discussão

| Categoria | Image AUROC | AU-PRO | Principal observação |
|---|---:|---:|---|
| cable | 0.9338 | 0.9144 | maior dificuldade de detecção |
| screw | 0.9650 | 0.9659 | boa localização, score global mais fraco |
| tile | 0.9996 | 0.8846 | pior localização |
| grid | 1.0000 | 0.8905 | classificação perfeita, localização inferior |
| leather | 1.0000 | 0.9821 | controle positivo |

---

# 23. O que evitar no relatório

Evitar frases absolutas como:

```text
"O EfficientAD não consegue segmentar corretamente."
"O EfficientAD sempre subsegmenta."
"O EfficientAD falha com texturas."
```

Preferir:

```text
"Nos exemplos analisados..."
"Foi observada tendência à..."
"Os casos inspecionados sugerem..."
"A categoria apresentou maior dificuldade em..."
```

Também evitar chamar imagens de:

```text
falso positivo
falso negativo
```

sem antes definir um threshold operacional.

Usar:

```text
imagem normal de maior score
imagem anômala de menor score
```

---

# 24. Observação sobre Pixel AUROC individual

Durante a análise qualitativa, foi calculado Pixel AUROC por imagem para facilitar a seleção de exemplos.

Esse valor:

- não substitui o AU-PRO oficial;
- não deve ser usado como métrica principal da baseline;
- serve apenas para organizar e inspecionar casos de localização.

A métrica oficial de localização considerada na reprodução é:

```text
AU-PRO @ FPR ≤ 0,3
```

---

# 25. Arquivos de resultados importantes

## Resultado consolidado

```text
~/IC/results/efficientad/efficientad_mvtec_ad_results.csv
```

## Resumo

```text
~/IC/results/efficientad/efficientad_mvtec_ad_summary.txt
```

## Métricas por categoria

```text
~/IC/results/efficientad/EA00X_<categoria>_full/metrics/mvtec_ad/metrics.json
```

## Anomaly maps

```text
~/IC/results/efficientad/EA00X_<categoria>_full/anomaly_maps/mvtec_ad/
```

## Análise qualitativa

```text
~/IC/results/efficientad/qualitative/
```

## Logs

```text
~/IC/logs/experiments/
```

---

# 26. Estado da baseline

```text
EfficientAD-M
├── Ambiente configurado            ✅
├── Teacher validado                ✅
├── ImageNet preparado              ✅
├── Smoke test                      ✅
├── Bottle completo                 ✅
├── 15 categorias executadas        ✅
├── Avaliação oficial MVTec         ✅
├── Resultados consolidados         ✅
├── Análise qualitativa             ✅
└── Documentação                    ✅
```

## Situação

A segunda baseline pode ser considerada:

```text
reproduzida
+
avaliada
+
analisada
+
documentada
```

---

# 27. Próximo passo do estudo

Antes de iniciar uma terceira baseline ou avançar para VLMs, o passo mais importante é **padronizar a comparação PatchCore × EfficientAD-M**.

## Fazer agora

Calcular para PatchCore:

```text
Image AUROC
AU-PRO @ FPR ≤ 0,3
```

usando o mesmo avaliador oficial da MVTec utilizado no EfficientAD-M.

## Depois

Montar uma tabela comparativa:

| Categoria | PatchCore Image AUROC | PatchCore AU-PRO | EfficientAD Image AUROC | EfficientAD AU-PRO |
|---|---:|---:|---:|---:|
| bottle | ... | ... | 1.0000 | 0.9574 |
| cable | ... | ... | 0.9338 | 0.9144 |
| ... | ... | ... | ... | ... |
| **Média** | ... | ... | **0.9901** | **0.9362** |

## Objetivo

Comparar os métodos sob o mesmo protocolo de avaliação antes de tirar conclusões sobre qual apresenta melhor detecção ou localização.

---

# 28. Conclusão final desta etapa

A reprodução do EfficientAD-M foi concluída com sucesso e produziu resultados consistentes com a referência adotada. A principal contribuição desta etapa não foi apenas obter um valor médio elevado, mas identificar **em quais situações o método apresenta comportamento diferente entre detecção e localização**.

Os resultados mostram que:

```text
detectar que há uma anomalia
≠
localizar toda a região anômala
```

e também que:

```text
localizar bem um pequeno defeito
≠
atribuir alto score global à imagem
```

Essas observações serão particularmente importantes nas etapas futuras do projeto, quando as baselines tradicionais de Visão Computacional forem comparadas a VLMs e, posteriormente, a uma abordagem integrada de Visão Computacional + VLM.
