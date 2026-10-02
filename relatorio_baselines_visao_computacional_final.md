# Desenvolvimento de baselines de Visão Computacional com MVTec AD e MVTec LOCO AD

## 1. Objetivo

Esta etapa teve como objetivo desenvolver e validar baselines de Visão Computacional para detecção e localização de anomalias industriais, utilizando os datasets MVTec AD e MVTec LOCO AD. Foram avaliados dois métodos, **PatchCore** e **EfficientAD-M**, buscando estabelecer referências quantitativas e qualitativas para as etapas posteriores do projeto.

O estudo dos datasets — organização, categorias, tipos de anomalia, anotações e métricas — foi realizado na etapa anterior. Por isso, este relatório concentra-se na **reprodução dos métodos, configuração experimental, padronização da avaliação, resultados e procedimentos necessários para reprodução**.

---

## 2. Ambiente experimental

Os experimentos foram executados no seguinte ambiente principal:

| Componente | Configuração |
|---|---|
| Sistema operacional | Linux Mint 22.1 |
| CPU | Intel Core i5-14600K |
| Memória RAM | 32 GB |
| GPU | NVIDIA GeForce RTX 5060 |
| VRAM | 8 GB |
| Python | 3.11 |
| PyTorch | 2.13.0+cu130 |
| Torchvision | 0.28.0+cu130 |
| CUDA utilizada pelo PyTorch | 13.0 |
| Gerenciamento de ambiente | Conda/Miniconda |

As versões do código e os parâmetros dos experimentos foram mantidos registrados para permitir a reprodução dos resultados.

---

## 3. Baselines utilizadas

### 3.1. PatchCore

Foi utilizada a implementação oficial da Amazon Science.

**Commit utilizado:**

```text
fcaa92f124fb1ad74a7acf56726decd4b27cbcad
```

**Configuração principal:**

| Parâmetro | Valor |
|---|---|
| Backbone | WideResNet50 |
| Camadas utilizadas | `layer2` e `layer3` |
| Resize | 256 |
| CenterCrop | 224 |
| Dimensão pré-embedding | 1024 |
| Dimensão final do embedding | 1024 |
| Patch size | 3 |
| Vizinhos | 1-NN |
| Coreset | Approximate greedy, 10% |
| Seed | 0 |
| FAISS | CPU |

O PatchCore utiliza uma rede pré-treinada para extração de características e constrói um *memory bank* com representações das imagens normais. Não há treinamento convencional da rede principal para cada categoria.

### 3.2. EfficientAD-M

Foi utilizada a implementação pública `nelson1425/EfficientAD`.

**Commit utilizado:**

```text
fcab5146f84ae17597044ad5ddf1656ccf805401
```

**Configuração principal:**

| Parâmetro | Valor |
|---|---|
| Variante | EfficientAD-M |
| Teacher | `teacher_medium.pth` |
| Treinamento | 70.000 passos por categoria |
| Penalty dataset | ImageNet train |
| Penalty loss | Habilitada |

No MVTec LOCO AD foi utilizado também o *split* oficial de validação do dataset.

---

## 4. Experimentos no MVTec AD

### 4.1. Procedimento

Os dois métodos foram executados sobre as 15 categorias do MVTec AD. Como as implementações originalmente utilizavam métricas de localização diferentes, foi necessário padronizar a avaliação antes da comparação final.

A comparação adotou:

```text
Image AUROC
AU-PRO @ FPR ≤ 0,3
```

Para o EfficientAD-M foi utilizado o avaliador oficial da MVTec. Para o PatchCore, os modelos já treinados foram reutilizados e seus *anomaly maps* foram exportados para o mesmo formato de avaliação.

### 4.2. Correção geométrica dos mapas do PatchCore

O pré-processamento do PatchCore utiliza `Resize(256)` seguido de `CenterCrop(224)`. Portanto, o *anomaly map* produzido pelo modelo corresponde apenas à região central observada após o *crop*.

Uma primeira exportação redimensionava diretamente o mapa de 224×224 para a resolução original, o que distorcia sua posição espacial. O procedimento final foi corrigido para:

```text
anomaly map 224×224
→ reposicionar na região correspondente ao CenterCrop(224) no espaço Resize(256)
→ preencher as regiões não observadas com o menor anomaly score do mapa
→ redimensionar o canvas completo para a resolução original
→ salvar em TIFF float32
→ avaliar com o código oficial da MVTec
```

Foram regenerados e validados **1.725 mapas**, todos com resolução compatível com suas imagens originais.

A correção não alterou o Image AUROC, mas modificou a avaliação de localização:

| Métrica PatchCore | Exportação anterior | Geometria corrigida |
|---|---:|---:|
| Image AUROC médio | 0.990959 | 0.990959 |
| AU-PRO médio | 0.912930 | 0.925413 |

O valor de AU-PRO da exportação antiga foi mantido apenas como registro histórico e não é utilizado nas comparações finais.

### 4.3. Resultados por categoria

A tabela a seguir apresenta os resultados finais dos dois métodos após a padronização do protocolo de avaliação e, no caso do PatchCore, após a correção geométrica da exportação dos *anomaly maps*.

| Categoria | PatchCore Image AUROC | EfficientAD-M Image AUROC | PatchCore AU-PRO | EfficientAD-M AU-PRO |
|---|---:|---:|---:|---:|
| bottle | 1.000000 | 1.000000 | 0.955331 | 0.957444 |
| cable | 0.998126 | 0.933846 | 0.948016 | 0.914445 |
| capsule | 0.975668 | 0.976865 | 0.961193 | 0.970248 |
| carpet | 0.985152 | 0.994382 | 0.938868 | 0.929671 |
| grid | 0.979114 | 1.000000 | 0.859306 | 0.890507 |
| hazelnut | 1.000000 | 1.000000 | 0.963897 | 0.951261 |
| leather | 1.000000 | 1.000000 | 0.969231 | 0.982097 |
| metal_nut | 0.999022 | 0.996579 | 0.947849 | 0.942391 |
| pill | 0.969722 | 0.991271 | 0.963217 | 0.964890 |
| screw | 0.980529 | 0.964952 | 0.960937 | 0.965948 |
| tile | 0.991342 | 0.999639 | 0.793117 | 0.884586 |
| toothbrush | 1.000000 | 1.000000 | 0.915059 | 0.932548 |
| transistor | 1.000000 | 1.000000 | 0.918091 | 0.912075 |
| wood | 0.991228 | 0.995614 | 0.863452 | 0.903694 |
| zipper | 0.994485 | 0.997637 | 0.923633 | 0.940856 |
| **Média** | **0.990959** | **0.990052** | **0.925413** | **0.936177** |

Os resultados por categoria mostram que as médias globais não descrevem todo o comportamento dos métodos. Em `tile`, por exemplo, o EfficientAD-M apresentou AU-PRO de 0.884586, contra 0.793117 do PatchCore. Em `cable`, ocorreu o comportamento inverso, com AU-PRO de 0.948016 para o PatchCore e 0.914445 para o EfficientAD-M.

### 4.4. Resultados médios e comparação

| Método | Image AUROC médio | AU-PRO médio |
|---|---:|---:|
| PatchCore | **0.990959** | 0.925413 |
| EfficientAD-M | 0.990052 | **0.936177** |

A diferença de Image AUROC foi inferior a 0,1 ponto percentual, indicando comportamento muito próximo em detecção em nível de imagem. Na localização, o EfficientAD-M apresentou AU-PRO médio aproximadamente **1,08 ponto percentual** superior sob o protocolo padronizado utilizado.

A diferença de localização não foi uniforme entre categorias. O EfficientAD-M apresentou AU-PRO superior em 10 das 15 categorias, enquanto o PatchCore apresentou valor superior em `cable`, `carpet`, `hazelnut`, `metal_nut` e `transistor`. O maior contraste favorável ao EfficientAD-M ocorreu em `tile`, e o maior contraste favorável ao PatchCore ocorreu em `cable`.

### 4.5. Observações qualitativas relevantes

A inspeção dos *anomaly maps* mostrou comportamentos diferentes entre os métodos. Nos casos analisados, o PatchCore frequentemente produziu mapas mais suaves ou difusos, enquanto o EfficientAD-M apresentou respostas mais concentradas, por vezes cobrindo apenas a parte mais discriminativa da região anômala.

Alguns exemplos foram particularmente úteis:

- em `tile`, o PatchCore apresentou respostas difusas sobre a textura repetitiva, enquanto o EfficientAD-M produziu mapas mais concentrados;
- em `wood`, defeitos finos mostraram maior dificuldade para o PatchCore, especialmente quando se confundiam com a textura natural;
- em `screw`, ambos localizaram defeitos pequenos adequadamente, embora a confiança em nível de imagem não acompanhasse necessariamente a qualidade da localização;
- em `leather`, ambos apresentaram desempenho elevado, porém com mapas espacialmente diferentes.

Esses casos reforçam que **detecção em nível de imagem e localização da anomalia devem ser analisadas separadamente**.

### 4.6. Custo experimental

No ambiente utilizado, a execução do PatchCore nas 15 categorias levou aproximadamente **11 min 51 s**. O treinamento acumulado do EfficientAD-M nas mesmas categorias levou aproximadamente **30 h 41 min**.

Esses valores representam o custo de preparação/treinamento das baselines no ambiente utilizado e **não devem ser interpretados como comparação de tempo de inferência por imagem**.

---

## 5. Experimentos no MVTec LOCO AD

### 5.1. Protocolo de avaliação

No MVTec LOCO AD foi utilizado o avaliador oficial versão 2.0. As métricas principais foram:

```text
Image AUROC
AUC-sPRO @ FPR ≤ 0,05
```

As métricas foram calculadas separadamente para:

```text
logical_anomalies
structural_anomalies
mean = média entre logical e structural
```

Essa separação é essencial no LOCO, pois o objetivo do dataset é avaliar tanto alterações visuais locais quanto violações de relações e restrições esperadas na cena.

### 5.2. Ajustes no avaliador LOCO

Durante a execução foram necessárias duas correções mínimas e documentadas no avaliador:

1. remoção de *thresholds* iniciais exatamente duplicados antes do `binary_refinement`;
2. uso de RNG local fixo com `np.random.RandomState(0)` na amostragem interna dos *thresholds*.

A primeira alteração foi necessária porque alguns mapas continham grandes platôs com o mesmo valor de *score*, gerando *queries* duplicadas. A segunda tornou a avaliação determinística. Antes da fixação da seed, a variação observada na AUC-sPRO era da ordem de 10⁻⁷; após a alteração, execuções repetidas produziram resultados idênticos.

### 5.3. Adaptação do PatchCore ao LOCO

Para utilizar o *loader* original do PatchCore sem modificar o repositório oficial, foi criado um *adapter* do MVTec LOCO AD.

O adapter utiliza links simbólicos para os conjuntos originais de `train`, `validation` e `test`. Máscaras obtidas por operação OR foram criadas apenas para satisfazer a interface interna do PatchCore. **Essas máscaras simplificadas não foram utilizadas na avaliação científica.**

A avaliação final utiliza exclusivamente o *ground truth* original multi-canal do LOCO.

A exportação dos mapas também aplicou a reconstrução correta da geometria `Resize(256) + CenterCrop(224)` antes do retorno à resolução original. A correção foi especialmente importante no LOCO: o sPRO médio do PatchCore passou de aproximadamente 0,287 na exportação incorreta para aproximadamente 0,502 após a correção.

### 5.4. Resultados por categoria — EfficientAD-M

| Categoria | Image logical | Image structural | Image mean | sPRO logical | sPRO structural | sPRO mean |
|---|---:|---:|---:|---:|---:|---:|
| breakfast_box | 0.859083 | 0.885839 | 0.872461 | 0.565576 | 0.734952 | 0.650264 |
| juice_bottle | 0.968535 | 0.997284 | 0.982909 | 0.915173 | 0.926740 | 0.920957 |
| pushpins | 0.956601 | 0.949096 | 0.952849 | 0.960370 | 0.762990 | 0.861680 |
| screw_bag | 0.507598 | 0.895642 | 0.701620 | 0.509966 | 0.830627 | 0.670297 |
| splicing_connectors | 0.940632 | 0.983391 | 0.962011 | 0.863115 | 0.910718 | 0.886916 |
| **Média** | **0.846490** | **0.942250** | **0.894370** | **0.762840** | **0.833205** | **0.798023** |

### 5.5. Resultados por categoria — PatchCore

| Categoria | Image logical | Image structural | Image mean | sPRO logical | sPRO structural | sPRO mean |
|---|---:|---:|---:|---:|---:|---:|
| breakfast_box | 0.793763 | 0.723638 | 0.758701 | 0.428091 | 0.552393 | 0.490242 |
| juice_bottle | 0.831660 | 0.867134 | 0.849397 | 0.543480 | 0.578103 | 0.560792 |
| pushpins | 0.609253 | 0.798622 | 0.703938 | 0.286457 | 0.448645 | 0.367551 |
| screw_bag | 0.560309 | 0.887945 | 0.724127 | 0.439264 | 0.731031 | 0.585147 |
| splicing_connectors | 0.631964 | 0.674543 | 0.653253 | 0.617230 | 0.393086 | 0.505158 |
| **Média** | **0.685390** | **0.790377** | **0.737883** | **0.462904** | **0.540652** | **0.501778** |

### 5.6. Comparação das baselines no LOCO

| Métrica média | PatchCore | EfficientAD-M | Diferença EA − PC |
|---|---:|---:|---:|
| Image AUROC logical | 0.685390 | 0.846490 | +0.161100 |
| Image AUROC structural | 0.790377 | 0.942250 | +0.151874 |
| **Image AUROC mean** | **0.737883** | **0.894370** | **+0.156487** |
| AUC-sPRO@0.05 logical | 0.462904 | 0.762840 | +0.299936 |
| AUC-sPRO@0.05 structural | 0.540652 | 0.833205 | +0.292554 |
| **AUC-sPRO@0.05 mean** | **0.501778** | **0.798023** | **+0.296245** |

Nesta reprodução, o EfficientAD-M apresentou médias superiores nas métricas de detecção e localização do LOCO. Para os dois métodos, o desempenho médio em anomalias estruturais foi superior ao desempenho médio em anomalias lógicas.

Os resultados por categoria, porém, mostram que essa tendência não é uniforme. Em `pushpins`, o EfficientAD-M obteve AUC-sPRO de **0.960370** para anomalias lógicas e **0.762990** para estruturais, constituindo um exemplo em que as anomalias lógicas apresentaram resultado superior. Em `screw_bag`, por outro lado, o EfficientAD-M apresentou Image AUROC logical de apenas **0.507598**, enquanto o valor structural foi **0.895642**.

Também houve exceções na comparação direta entre métodos. Em `screw_bag`, o PatchCore apresentou Image AUROC médio de **0.724127**, acima dos **0.701620** do EfficientAD-M, embora o EfficientAD-M tenha mantido sPRO médio superior nessa categoria (**0.670297** contra **0.585147**). A maior diferença de sPRO médio ocorreu em `pushpins`, com aproximadamente **0.4941** a favor do EfficientAD-M. Em `splicing_connectors`, as diferenças também foram expressivas, tanto em detecção quanto em localização.

Esses resultados indicam que a dificuldade das anomalias lógicas depende tanto do método quanto das relações visuais específicas de cada categoria. Portanto, não é adequado concluir que anomalias lógicas são sempre mais difíceis ou que um dos métodos “compreende” relações lógicas.

---

## 6. Comparação com resultados publicados

Os resultados obtidos foram comparados com os valores reportados nos trabalhos originais e nas configurações de referência disponibilizadas pelos autores. Essa comparação deve considerar o protocolo experimental: resultados só são diretamente comparáveis quando configuração, pré-processamento e métrica são equivalentes.

### 6.1. PatchCore no MVTec AD

O artigo do PatchCore reporta Image AUROC de até **99,6%** no MVTec AD, porém esse valor corresponde à melhor configuração estudada pelos autores e não é a referência mais adequada para a execução deste trabalho. A configuração utilizada aqui corresponde à baseline **IM224** da implementação oficial: WideResNet50, `layer2 + layer3`, coreset de 10%, embedding 1024→1024, *patch size* 3, 1-NN e seed 0.

Para essa configuração, a implementação oficial reporta aproximadamente:

```text
Image AUROC = 99,2%
Pixel AUROC = 98,1%
PRO         = 94,4%
```

A reprodução local obteve Image AUROC de **99,11%** e Full Pixel AUROC de **98,12%** na execução original. Na avaliação padronizada e com a geometria corrigida, o AU-PRO foi **92,54%**.

| Métrica | Referência IM224 | Reprodução local | Diferença |
|---|---:|---:|---:|
| Image AUROC | 99,20% | 99,11% | -0,09 p.p. |
| Pixel AUROC | 98,10% | 98,12% | +0,02 p.p. |
| PRO / AU-PRO | 94,40% | 92,54% | -1,86 p.p. |

Os resultados de detecção e Pixel AUROC ficaram muito próximos da configuração de referência. A diferença residual em localização permaneceu após a correção geométrica dos mapas e deve ser tratada como um *caveat* de reprodução, pois detalhes de versão, interpolação e protocolo de avaliação podem afetar a métrica regional.

Referências:
- Roth et al., *Towards Total Recall in Industrial Anomaly Detection*, CVPR 2022.
- Configuração IM224 da implementação oficial: [Amazon Science — PatchCore `sample_training.sh`](https://github.com/amazon-science/patchcore-inspection/blob/main/sample_training.sh).

### 6.2. EfficientAD-M no MVTec AD

No artigo do EfficientAD, a variante EfficientAD-M reporta **99,1% de Image AUROC** e **93,5% de AU-PRO@0.3** no MVTec AD. Nesta reprodução foram obtidos **99,01%** e **93,62%**, respectivamente.

| Métrica | EfficientAD-M publicado | Reprodução local | Diferença |
|---|---:|---:|---:|
| Image AUROC | 99,10% | 99,01% | -0,09 p.p. |
| AU-PRO@0.3 | 93,50% | 93,62% | +0,12 p.p. |

As diferenças são inferiores a 0,2 ponto percentual nas duas métricas, indicando forte concordância com os resultados publicados para o MVTec AD.

Referência:
- Batzner, Heckler e König, *EfficientAD: Accurate Visual Anomaly Detection at Millisecond-Level Latencies*, WACV 2024: [CVF Open Access](https://openaccess.thecvf.com/content/WACV2024/html/Batzner_EfficientAD_Accurate_Visual_Anomaly_Detection_at_Millisecond-Level_Latencies_WACV_2024_paper.html).

### 6.3. EfficientAD-M no MVTec LOCO AD

O artigo do EfficientAD reporta, no MVTec LOCO AD, Image AUROC médio de **90,7%**, com **86,8%** para anomalias lógicas e **94,7%** para estruturais. Para localização, o material suplementar reporta AUC-sPRO@0.05 médio de **79,8%**, com **76,5%** para anomalias lógicas e **83,2%** para estruturais.

A reprodução apresentou:

| Métrica | Publicado | Reprodução local | Diferença |
|---|---:|---:|---:|
| Image AUROC logical | 86,80% | 84,65% | -2,15 p.p. |
| Image AUROC structural | 94,70% | 94,23% | -0,48 p.p. |
| **Image AUROC mean** | **90,70%** | **89,44%** | **-1,26 p.p.** |
| AUC-sPRO@0.05 logical | 76,50% | 76,28% | -0,22 p.p. |
| AUC-sPRO@0.05 structural | 83,20% | 83,32% | +0,12 p.p. |
| **AUC-sPRO@0.05 mean** | **79,80%** | **79,80%** | **≈ 0,00 p.p.** |

A localização ficou praticamente coincidente com o valor publicado, especialmente na média de AUC-sPRO. A maior diferença ocorreu na detecção de anomalias lógicas, aproximadamente 2,15 pontos percentuais abaixo do artigo. Ainda assim, o comportamento global da reprodução permaneceu próximo ao reportado pelos autores.

### 6.4. PatchCore no MVTec LOCO AD

O PatchCore apresentado como baseline no artigo do EfficientAD obteve, no LOCO, Image AUROC médio de **80,3%** e AUC-sPRO@0.05 médio de **39,7%**. Os resultados separados foram **75,8% / 84,8%** de Image AUROC e **41,5% / 37,9%** de AUC-sPRO para anomalias lógicas e estruturais, respectivamente.

Nesta reprodução:

| Métrica | PatchCore no benchmark do EfficientAD | Reprodução local | Diferença |
|---|---:|---:|---:|
| Image AUROC logical | 75,80% | 68,54% | -7,26 p.p. |
| Image AUROC structural | 84,80% | 79,04% | -5,76 p.p. |
| **Image AUROC mean** | **80,30%** | **73,79%** | **-6,51 p.p.** |
| AUC-sPRO@0.05 logical | 41,50% | 46,29% | +4,79 p.p. |
| AUC-sPRO@0.05 structural | 37,90% | 54,07% | +16,17 p.p. |
| **AUC-sPRO@0.05 mean** | **39,70%** | **50,18%** | **+10,48 p.p.** |

Esses valores **não devem ser interpretados como uma tentativa de reprodução estrita do PatchCore usado no benchmark do EfficientAD**. O material suplementar de Batzner et al. informa que a variante de PatchCore usada por eles emprega **WideResNet101, coreset de 1%, imagens de 224×224 e center crop desabilitado**. Neste projeto foi preservada a configuração já validada no MVTec AD: **WideResNet50, coreset de 10% e `Resize(256) + CenterCrop(224)`**.

Portanto, a comparação serve para contextualizar os resultados, mas as diferenças não podem ser atribuídas exclusivamente à implementação ou ao dataset. No LOCO, o PatchCore deste trabalho deve ser entendido como **a aplicação da baseline definida no projeto ao novo dataset**, e não como reprodução da variante específica usada por Batzner et al.

### 6.5. Síntese da validação

A comparação com os resultados publicados permite separar duas situações:

- **MVTec AD:** as reproduções de PatchCore e EfficientAD-M ficaram próximas das referências correspondentes, validando o ambiente e o pipeline experimental;
- **MVTec LOCO AD — EfficientAD-M:** os resultados também ficaram próximos do artigo, com AUC-sPRO média praticamente idêntica;
- **MVTec LOCO AD — PatchCore:** não há equivalência direta de configuração com o benchmark do EfficientAD, portanto os valores devem ser tratados como uma baseline própria deste projeto.

Essa distinção é importante para evitar que diferenças causadas por configuração experimental sejam interpretadas como falhas de reprodução.

---

## 7. Procedimento recomendado para reprodução

Para reproduzir esta etapa, o fluxo mínimo é:

1. preparar os datasets MVTec AD e MVTec LOCO AD conforme a organização descrita no relatório da primeira etapa;
2. configurar o ambiente com as versões de Python, PyTorch, Torchvision e CUDA registradas neste relatório;
3. utilizar os commits registrados das implementações do PatchCore e EfficientAD-M;
4. executar o PatchCore com WideResNet50, `layer2 + layer3`, `Resize(256)`, `CenterCrop(224)`, coreset de 10%, 1-NN e seed 0;
5. executar o EfficientAD-M com `teacher_medium.pth`, 70.000 passos por categoria e *ImageNet penalty* habilitada;
6. no MVTec AD, avaliar os dois métodos com o mesmo avaliador e utilizar os mapas do PatchCore com a geometria do `CenterCrop` reconstruída antes do redimensionamento final;
7. no LOCO, utilizar o *split* oficial de validação, preservar o *ground truth* multi-canal e aplicar o avaliador v2.0 com as correções documentadas;
8. calcular separadamente as métricas para anomalias lógicas e estruturais;
9. registrar por execução os parâmetros, commit, seed, tempo, mapas exportados e arquivos de métricas.

Para validar a reprodução, devem ser comparados tanto os resultados por categoria quanto os valores médios apresentados neste relatório. Diferenças pequenas podem ocorrer por versões de bibliotecas, interpolação, ambiente e detalhes de implementação, devendo ser registradas quando observadas.

---

## 8. Arquivos e scripts utilizados no projeto

Os principais artefatos da execução foram mantidos nos seguintes caminhos:

```text
PatchCore:
~/IC/baselines/patchcore-inspection

EfficientAD:
~/IC/baselines/efficientad

Exportação corrigida do PatchCore — MVTec AD:
~/IC/tools/exportar_patchcore_mvtec_maps_geometry_fixed.py

Adapter PatchCore — MVTec LOCO AD:
~/IC/tools/criar_adapter_patchcore_loco.py

Exportação corrigida do PatchCore — LOCO:
~/IC/tools/exportar_patchcore_loco_maps_geometry_fixed.py

Resultados PatchCore — MVTec AD:
~/IC/results/patchcore/standardized_eval_geometry_fixed/

Resumo EfficientAD — LOCO:
~/IC/results/efficientad_loco/efficientad_loco_summary.csv

Resumo PatchCore — LOCO:
~/IC/results/patchcore_loco/patchcore_loco_summary_geometry_fixed.csv

Comparação LOCO:
~/IC/results/loco_patchcore_vs_efficientad.csv

Avaliador LOCO:
~/IC/baselines/efficientad/mvtec_loco_ad_evaluation/

Patch aplicado ao avaliador LOCO:
~/IC/logs/mvtec_loco_evaluator_patch.diff
```

Esses arquivos são importantes para rastreabilidade, principalmente porque a avaliação final do PatchCore depende da reconstrução geométrica correta dos mapas e a avaliação do LOCO utiliza as correções documentadas no avaliador.

### 8.1. Repositório público e acesso aos artefatos

O código, a documentação e os resultados consolidados desta etapa foram publicados no GitHub:

**Repositório:** [FernandoBuligon/IC](https://github.com/FernandoBuligon/IC)

A versão publicada contém o README principal, o relatório desta etapa, documentação de reprodução, ambientes, scripts auxiliares, registros selecionados e os arquivos de métricas necessários para conferência dos resultados.

Acesso direto aos principais grupos de artefatos:

| Conteúdo | Link |
|---|---|
| Repositório principal | [github.com/FernandoBuligon/IC](https://github.com/FernandoBuligon/IC) |
| Relatório desta etapa | [`relatorio_baselines_visao_computacional_final.md`](https://github.com/FernandoBuligon/IC/blob/main/relatorio_baselines_visao_computacional_final.md) |
| README e instruções de reprodução | [`README.md`](https://github.com/FernandoBuligon/IC/blob/main/README.md) |
| Resultados e métricas | [`results/`](https://github.com/FernandoBuligon/IC/tree/main/results) |
| Scripts desenvolvidos | [`tools/`](https://github.com/FernandoBuligon/IC/tree/main/tools) |
| Ambientes e dependências | [`environments/`](https://github.com/FernandoBuligon/IC/tree/main/environments) |
| Documentação complementar | [`docs/`](https://github.com/FernandoBuligon/IC/tree/main/docs) |
| Logs e patch do avaliador | [`logs/`](https://github.com/FernandoBuligon/IC/tree/main/logs) |

Scripts citados neste relatório:

- [`exportar_patchcore_mvtec_maps_geometry_fixed.py`](https://github.com/FernandoBuligon/IC/blob/main/tools/exportar_patchcore_mvtec_maps_geometry_fixed.py);
- [`criar_adapter_patchcore_loco.py`](https://github.com/FernandoBuligon/IC/blob/main/tools/criar_adapter_patchcore_loco.py);
- [`exportar_patchcore_loco_maps_geometry_fixed.py`](https://github.com/FernandoBuligon/IC/blob/main/tools/exportar_patchcore_loco_maps_geometry_fixed.py);
- [`mvtec_loco_evaluator_patch.diff`](https://github.com/FernandoBuligon/IC/blob/main/logs/mvtec_loco_evaluator_patch.diff).

Na organização publicada foram preservados **5 arquivos CSV e 40 arquivos JSON** de resultados/métricas, sem alteração de seus conteúdos. Os datasets MVTec, adapters contendo imagens ou links simbólicos, pesos, checkpoints, clones de implementações externas e *anomaly maps* em massa permaneceram fora do Git.

Dessa forma, os caminhos locais apresentados na seção anterior registram a organização utilizada durante os experimentos, enquanto o repositório público fornece acesso aos scripts, configurações, documentação e resultados necessários para auditoria e reprodução.

---

## 9. Conclusões

A etapa permitiu estabelecer duas referências de Visão Computacional para detecção e localização de anomalias.

No MVTec AD, PatchCore e EfficientAD-M apresentaram Image AUROC médio próximo de 0,99. Após a padronização do protocolo e a correção geométrica dos mapas do PatchCore, o EfficientAD-M apresentou AU-PRO médio de 0.9362 e o PatchCore 0.9254, uma diferença de aproximadamente 1,08 ponto percentual.

No MVTec LOCO AD, as diferenças entre os métodos foram maiores. O EfficientAD-M obteve médias de 0.8944 em Image AUROC e 0.7980 em AUC-sPRO@0.05, enquanto o PatchCore obteve 0.7379 e 0.5018, respectivamente. Os dois métodos apresentaram, em média, maior desempenho em anomalias estruturais do que em anomalias lógicas, embora esse comportamento varie conforme a categoria.

A comparação com os resultados publicados também forneceu uma validação externa do pipeline. No MVTec AD, as duas baselines apresentaram valores próximos às referências correspondentes. No LOCO, o EfficientAD-M manteve forte concordância com o artigo, incluindo AUC-sPRO média praticamente idêntica. Para o PatchCore no LOCO, a comparação com o artigo do EfficientAD foi tratada apenas como contextual, pois as configurações experimentais são diferentes.

Além dos valores quantitativos, a etapa mostrou que a avaliação de baselines de anomalia depende de detalhes de implementação que afetam diretamente a localização, como a reconstrução espacial dos *anomaly maps*, o uso correto das anotações do LOCO e a aplicação de um protocolo de avaliação comum. Esses cuidados são necessários para que os resultados sejam comparáveis e possam servir como referência confiável para as próximas etapas do projeto.

Os scripts, resultados consolidados e documentação de reprodução estão disponíveis no repositório público [FernandoBuligon/IC](https://github.com/FernandoBuligon/IC).