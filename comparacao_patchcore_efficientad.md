# Comparação entre as Baselines — PatchCore × EfficientAD-M no MVTec AD

> **Objetivo deste documento:** consolidar a comparação direta entre as duas primeiras baselines do projeto — PatchCore e EfficientAD-M — utilizando um protocolo de avaliação padronizado. O documento também indica **o que deve ser inserido no relatório principal**, quais títulos utilizar, quais tabelas e imagens são recomendadas e quais interpretações são metodologicamente seguras.

---

# 1. Objetivo da comparação

Após a reprodução e análise individual das duas baselines, foi necessário padronizar a avaliação para permitir uma comparação quantitativa direta.

Inicialmente:

- o **PatchCore** havia sido avaliado com:
  - Image AUROC;
  - Full Pixel AUROC;
  - Anomaly Pixel AUROC;

- o **EfficientAD-M** havia sido avaliado com:
  - Image AUROC;
  - AU-PRO com limite de FPR igual a 0,3.

Como essas métricas de localização não eram diretamente equivalentes, os anomaly maps do PatchCore foram exportados e submetidos ao **mesmo código oficial de avaliação da MVTec** utilizado para o EfficientAD-M.

Dessa forma, a comparação final utiliza:

```text
Image AUROC
AU-PRO @ FPR ≤ 0,3
```

para os dois métodos.

---

# 2. Métodos comparados

## PatchCore

- Implementação: oficial da Amazon Science
- Backbone: WideResNet50
- Camadas: `layer2` e `layer3`
- Resolução: 224 × 224
- Coreset: 10%
- Patch size: 3
- Número de vizinhos: 1
- Seed: 0
- FAISS: CPU
- Dataset: MVTec AD

## EfficientAD-M

- Implementação: pública não oficial (`nelson1425/EfficientAD`)
- Variante: EfficientAD-M
- Teacher: `teacher_medium.pth`
- Passos de treinamento: 70.000
- Penalty dataset: ImageNet train
- Dataset: MVTec AD
- Avaliação oficial da MVTec

---

# 3. Padronização da avaliação

## Procedimento aplicado ao PatchCore

Os modelos já treinados da execução PC-002 foram reutilizados.

Para cada categoria:

1. o modelo PatchCore salvo foi carregado;
2. foram gerados anomaly maps para todas as imagens de teste;
3. os mapas foram redimensionados para a resolução original das imagens;
4. os mapas foram salvos em formato TIFF;
5. o mesmo avaliador oficial da MVTec usado no EfficientAD-M foi aplicado.

## Resultado da padronização

A média de Image AUROC do PatchCore após essa avaliação foi:

```text
0,990959
```

O resultado original da execução PC-002 havia sido:

```text
0,991093
```

Diferença:

```text
0,000134
```

A diferença é mínima, o que indica que o processo de exportação e avaliação padronizada preservou de forma consistente o comportamento global do método.

---

# 4. Resultados quantitativos consolidados

## Tabela principal

| Categoria | PatchCore Image AUROC | EfficientAD-M Image AUROC | PatchCore AU-PRO | EfficientAD-M AU-PRO |
|---|---:|---:|---:|---:|
| bottle | 1.000000 | 1.000000 | 0.928318 | 0.957444 |
| cable | 0.998126 | 0.933846 | 0.912932 | 0.914445 |
| capsule | 0.975668 | 0.976865 | 0.933971 | 0.970248 |
| carpet | 0.985152 | 0.994382 | 0.930826 | 0.929671 |
| grid | 0.979114 | 1.000000 | 0.894652 | 0.890507 |
| hazelnut | 1.000000 | 1.000000 | 0.957846 | 0.951261 |
| leather | 1.000000 | 1.000000 | 0.960302 | 0.982097 |
| metal_nut | 0.999022 | 0.996579 | 0.854771 | 0.942391 |
| pill | 0.969722 | 0.991271 | 0.955237 | 0.964890 |
| screw | 0.980529 | 0.964952 | 0.958564 | 0.965948 |
| tile | 0.991342 | 0.999639 | 0.835064 | 0.884586 |
| toothbrush | 1.000000 | 1.000000 | 0.868093 | 0.932548 |
| transistor | 1.000000 | 1.000000 | 0.943609 | 0.912075 |
| wood | 0.991228 | 0.995614 | 0.835633 | 0.903694 |
| zipper | 0.994485 | 0.997637 | 0.924133 | 0.940856 |
| **Média** | **0.990959** | **0.990052** | **0.912930** | **0.936177** |

---

# 5. Comparação das médias

## Image AUROC

### PatchCore

```text
0.990959
```

### EfficientAD-M

```text
0.990052
```

Diferença:

```text
PatchCore - EfficientAD-M = 0.000907
```

ou aproximadamente:

```text
+0,09 ponto percentual
```

### Interpretação

Os métodos apresentaram desempenho praticamente equivalente em detecção em nível de imagem.

A diferença ficou abaixo de 0,1 ponto percentual.

---

## AU-PRO

### PatchCore

```text
0.912930
```

### EfficientAD-M

```text
0.936177
```

Diferença:

```text
EfficientAD-M - PatchCore = 0.023247
```

ou aproximadamente:

```text
+2,32 pontos percentuais
```

### Interpretação

Nesta reprodução, o EfficientAD-M apresentou maior AU-PRO médio, indicando melhor desempenho de localização sob o protocolo padronizado utilizado.

---

# 6. Texto sugerido para o relatório — comparação geral

> Para permitir uma comparação direta entre as baselines, os anomaly maps produzidos pelo PatchCore foram exportados e avaliados com o mesmo código oficial da MVTec utilizado para o EfficientAD-M. Com esse protocolo padronizado, o PatchCore apresentou Image AUROC médio de 0,9910 e AU-PRO médio de 0,9129, enquanto o EfficientAD-M obteve 0,9901 e 0,9362, respectivamente. Os resultados indicam desempenho praticamente equivalente em detecção em nível de imagem, com diferença inferior a 0,1 ponto percentual, enquanto o EfficientAD-M apresentou AU-PRO médio aproximadamente 2,32 pontos percentuais superior nesta reprodução.

---

# 7. Comparação por categoria — Image AUROC

## Categorias em que PatchCore apresentou valor superior

```text
cable
metal_nut
screw
```

## Categorias em que EfficientAD-M apresentou valor superior

```text
capsule
carpet
grid
pill
tile
wood
zipper
```

## Empates

```text
bottle
hazelnut
leather
toothbrush
transistor
```

## Contagem

```text
PatchCore superior: 3 categorias
EfficientAD-M superior: 7 categorias
Empate: 5 categorias
```

## Observação

A contagem por categoria é apenas descritiva.

Não deve ser usada isoladamente para declarar um método como “melhor” em detecção, porque:

- as diferenças variam em magnitude;
- várias categorias apresentam valores praticamente iguais;
- a média global é mais adequada para caracterizar o comportamento geral.

---

# 8. Comparação por categoria — AU-PRO

## EfficientAD-M apresentou AU-PRO superior em 11 categorias

```text
bottle
cable
capsule
leather
metal_nut
pill
screw
tile
toothbrush
wood
zipper
```

## PatchCore apresentou AU-PRO superior em 4 categorias

```text
carpet
grid
hazelnut
transistor
```

---

# 9. Maiores diferenças em AU-PRO

## Vantagens do EfficientAD-M

| Categoria | PatchCore | EfficientAD-M | Diferença |
|---|---:|---:|---:|
| metal_nut | 0.8548 | 0.9424 | **+0.0876** |
| wood | 0.8356 | 0.9037 | **+0.0681** |
| toothbrush | 0.8681 | 0.9325 | **+0.0645** |
| tile | 0.8351 | 0.8846 | **+0.0495** |
| capsule | 0.9340 | 0.9702 | **+0.0363** |
| bottle | 0.9283 | 0.9574 | **+0.0291** |
| leather | 0.9603 | 0.9821 | **+0.0218** |

## Vantagens do PatchCore

| Categoria | PatchCore | EfficientAD-M | Diferença |
|---|---:|---:|---:|
| transistor | 0.9436 | 0.9121 | **+0.0315** |
| hazelnut | 0.9578 | 0.9513 | **+0.0066** |
| grid | 0.8947 | 0.8905 | **+0.0041** |
| carpet | 0.9308 | 0.9297 | **+0.0012** |

## Interpretação

A vantagem média do EfficientAD-M em localização não é uniforme.

Em algumas categorias, como:

```text
metal_nut
wood
toothbrush
tile
```

a diferença é expressiva.

Por outro lado, o PatchCore apresenta melhor desempenho em:

```text
transistor
hazelnut
grid
carpet
```

com destaque para `transistor`.

---

# 10. Texto sugerido para o relatório — comparação por categoria

> A análise por categoria mostra que a diferença média de localização não é uniforme. O EfficientAD-M apresentou ganhos mais expressivos em classes como `metal_nut`, `wood`, `toothbrush` e `tile`, enquanto o PatchCore obteve AU-PRO superior em `transistor`, `hazelnut`, `grid` e `carpet`. O maior contraste favorável ao EfficientAD-M ocorreu em `metal_nut`, com diferença de aproximadamente 8,76 pontos percentuais, enquanto o maior contraste favorável ao PatchCore ocorreu em `transistor`, com aproximadamente 3,15 pontos percentuais.

---

# 11. Comparação qualitativa — padrões observados

As análises qualitativas individuais das duas baselines mostraram diferenças importantes no formato dos anomaly maps.

---

## 11.1. `tile`

### PatchCore

Nos piores casos:

- mapas difusos;
- baixa seletividade espacial;
- respostas espalhadas;
- dificuldade de separar pequenas alterações da textura repetitiva.

### EfficientAD-M

Nos piores casos:

- mapas mais concentrados;
- região correta frequentemente identificada;
- tendência à subsegmentação;
- cobertura apenas da parte mais discriminativa da anomalia.

### Interpretação

Os dois métodos apresentam dificuldade em `tile`, porém de formas diferentes.

```text
PatchCore:
difusão espacial

EfficientAD-M:
subsegmentação
```

### Texto sugerido

> Em `tile`, a comparação qualitativa mostra padrões distintos de erro. O PatchCore tende a produzir mapas mais difusos e pouco seletivos sobre a textura repetitiva, enquanto o EfficientAD-M concentra a resposta em regiões menores, frequentemente cobrindo apenas parte da anomalia. Assim, a perda de desempenho de localização ocorre por mecanismos qualitativamente diferentes nos dois métodos.

---

# 12. Comparação qualitativa — `wood`

## PatchCore

Foi observada:

- dificuldade com defeitos finos;
- mapas mais largos que scratches reais;
- confusão entre veios naturais da madeira e regiões defeituosas.

## EfficientAD-M

O AU-PRO foi significativamente maior:

```text
PatchCore = 0.8356
EfficientAD-M = 0.9037
```

Mesmo sem uma análise visual equivalente tão extensa para o EfficientAD-M em `wood`, a diferença quantitativa indica maior consistência de localização nesse protocolo.

### Texto sugerido

> Na categoria `wood`, o PatchCore apresentou dificuldade qualitativa para delimitar riscos finos sobre a textura natural da madeira. A avaliação padronizada reforça essa observação, uma vez que o método obteve AU-PRO de 0,8356, enquanto o EfficientAD-M alcançou 0,9037.

---

# 13. Comparação qualitativa — `screw`

## PatchCore

- mapas relativamente amplos;
- elevada discriminação pixel a pixel;
- suavização espacial.

## EfficientAD-M

- mapas discretos para defeitos pequenos;
- boa localização;
- alguns defeitos receberam score global muito baixo;
- maior sobreposição entre imagens normais e anômalas.

## Resultados

```text
PatchCore Image AUROC = 0.9805
PatchCore AU-PRO = 0.9586

EfficientAD-M Image AUROC = 0.9650
EfficientAD-M AU-PRO = 0.9659
```

### Interpretação

PatchCore apresentou melhor detecção global, enquanto EfficientAD-M apresentou AU-PRO ligeiramente maior.

### Texto sugerido

> Em `screw`, os dois métodos apresentaram comportamentos complementares. O PatchCore obteve maior Image AUROC, enquanto o EfficientAD-M apresentou AU-PRO ligeiramente superior. A análise qualitativa mostrou que o EfficientAD-M pode localizar adequadamente pequenos defeitos `thread_side` mesmo quando atribui baixo score global à imagem, evidenciando uma separação entre qualidade de localização e confiança de classificação.

---

# 14. Comparação qualitativa — `leather`

## PatchCore

- mapas suaves;
- forte correspondência com o defeito;
- bom desempenho mesmo nos piores casos.

## EfficientAD-M

- mapas mais concentrados;
- tendência à subsegmentação;
- desempenho quantitativo superior.

## Resultados

```text
PatchCore AU-PRO = 0.9603
EfficientAD-M AU-PRO = 0.9821
```

### Texto sugerido

> Em `leather`, ambos os métodos apresentaram desempenho elevado. O PatchCore produziu mapas espacialmente mais suaves, enquanto o EfficientAD-M concentrou a resposta nas regiões mais discriminativas da anomalia. Apesar dessa tendência à subsegmentação, o EfficientAD-M obteve AU-PRO superior, indicando melhor consistência geral de localização nessa categoria.

---

# 15. Comparação qualitativa — `transistor`

## PatchCore

- Image AUROC praticamente perfeito;
- dificuldade de cobrir integralmente anomalias `misplaced`;
- ativação em bordas, terminais e regiões de alto contraste.

## EfficientAD-M

Resultado padronizado:

```text
Image AUROC = 1,0000
AU-PRO = 0,9121
```

PatchCore:

```text
Image AUROC = 1,0000
AU-PRO = 0,9436
```

### Interpretação

`transistor` é a principal categoria em que PatchCore apresentou uma vantagem clara em localização.

### Texto sugerido

> A categoria `transistor` apresentou o maior contraste favorável ao PatchCore em AU-PRO. Ambos os métodos atingiram Image AUROC de 1,0, porém o PatchCore obteve AU-PRO de 0,9436, contra 0,9121 do EfficientAD-M. Isso indica que, apesar das limitações qualitativas observadas nos casos `misplaced`, o PatchCore preservou melhor desempenho de localização global nessa categoria.

---

# 16. Comparação de custo experimental

## PatchCore

Execução das 15 categorias:

```text
aproximadamente 11 min 51 s
```

## EfficientAD-M

Treinamento acumulado das 15 categorias:

```text
aproximadamente 30 h 41 min
```

## Diferença prática

O EfficientAD-M apresentou custo computacional de treinamento muito superior.

Isso acontece porque:

### PatchCore
- utiliza backbone pré-treinado;
- constrói memory bank;
- não faz treinamento convencional da rede principal.

### EfficientAD-M
- treina Student;
- treina Autoencoder;
- utiliza 70.000 passos;
- usa imagens externas do ImageNet durante a penalty loss.

## Texto sugerido para o relatório

> Uma diferença relevante entre as baselines está no custo experimental. A execução completa do PatchCore nas 15 categorias levou aproximadamente 11 minutos e 51 segundos, enquanto o treinamento acumulado do EfficientAD-M ultrapassou 30 horas. Essa diferença decorre das características dos métodos: o PatchCore utiliza um backbone pré-treinado como extrator de características e constrói um memory bank, enquanto o EfficientAD-M realiza treinamento iterativo de Student e Autoencoder ao longo de 70.000 passos por categoria.

## Importante

Não comparar diretamente esses tempos como “tempo de inferência”.

Eles representam:

```text
tempo de preparação/treinamento da baseline
```

e não necessariamente velocidade de inferência por imagem.

---

# 17. Resumo comparativo

| Aspecto | PatchCore | EfficientAD-M |
|---|---|---|
| Image AUROC médio | **0.9910** | 0.9901 |
| AU-PRO médio | 0.9129 | **0.9362** |
| Preparação/treinamento | muito rápido | muito mais custoso |
| Uso de ImageNet externo | backbone pré-treinado | penalty dataset durante treinamento |
| Comportamento dos mapas | frequentemente mais suaves/difusos | frequentemente mais concentrados |
| Tendência observada | boa detecção e memory-bank local | boa localização média, mas possível subsegmentação |
| Implementação usada | oficial | não oficial |

---

# 18. Texto sugerido para discussão geral

> Os resultados mostram que PatchCore e EfficientAD-M apresentam desempenho praticamente equivalente em detecção de anomalias em nível de imagem, com Image AUROC médio próximo de 0,99 em ambos os casos. A principal diferença quantitativa apareceu na localização, em que o EfficientAD-M apresentou AU-PRO médio de 0,9362, aproximadamente 2,32 pontos percentuais acima do PatchCore. Entretanto, a análise por categoria mostrou que essa vantagem não é uniforme. O PatchCore apresentou melhor desempenho em classes como `transistor`, enquanto o EfficientAD-M obteve ganhos expressivos em `metal_nut`, `wood`, `toothbrush` e `tile`.

Complemento:

> A inspeção qualitativa também revelou padrões distintos nos anomaly maps. O PatchCore tende a produzir respostas mais suaves ou difusas em algumas categorias texturizadas, enquanto o EfficientAD-M frequentemente gera mapas mais concentrados, podendo subsegmentar a extensão da anomalia. Esses resultados sugerem que diferenças na estratégia de representação e aprendizado dos métodos se refletem não apenas nas métricas agregadas, mas também na forma espacial das respostas produzidas.

Complemento sobre custo:

> Apesar do maior AU-PRO médio, o EfficientAD-M apresentou custo experimental significativamente superior. Enquanto o PatchCore foi executado em aproximadamente 12 minutos para as 15 categorias, o treinamento acumulado do EfficientAD-M ultrapassou 30 horas. Assim, a comparação entre as baselines deve considerar não apenas desempenho, mas também custo computacional e comportamento qualitativo.

---

# 19. Estrutura recomendada para o relatório

A comparação pode ser organizada em uma seção própria:

```text
X. Comparação entre as baselines de Visão Computacional

X.1. Padronização do protocolo de avaliação
X.2. Resultados quantitativos
X.3. Comparação por categoria
X.4. Análise qualitativa comparativa
X.5. Custo computacional
X.6. Discussão
```

Se o relatório for mais curto:

```text
X. Comparação PatchCore × EfficientAD-M
X.1. Resultados
X.2. Análise por categoria
X.3. Discussão
```

---

# 20. Tabelas recomendadas para o relatório

## Tabela principal

Utilizar:

| Categoria | PatchCore Image AUROC | EfficientAD Image AUROC | PatchCore AU-PRO | EfficientAD AU-PRO |
|---|---:|---:|---:|---:|

com as 15 categorias.

## Tabela resumida

| Método | Image AUROC médio | AU-PRO médio | Tempo experimental |
|---|---:|---:|---:|
| PatchCore | **0.9910** | 0.9129 | ~11m51s |
| EfficientAD-M | 0.9901 | **0.9362** | ~30h41m |

---

# 21. Figuras recomendadas

Não é necessário repetir todas as figuras das seções individuais.

Para a comparação, usar poucas figuras representativas.

## Figura comparativa 1 — `tile`

### PatchCore
```text
tile/pior_localizacao/01_gray_stroke_012.png
```

### EfficientAD-M
```text
tile/pior_localizacao/01_gray_stroke_002.png
```

Objetivo:
mostrar:

```text
PatchCore → mapa difuso
EfficientAD → mapa concentrado/subsegmentado
```

### Legenda sugerida

> **Figura X — Comparação qualitativa entre PatchCore e EfficientAD-M na categoria `tile`.** O PatchCore apresenta resposta mais difusa, enquanto o EfficientAD-M concentra a ativação em uma região menor da anomalia.

---

## Figura comparativa 2 — `screw`

### PatchCore
```text
screw/pior_localizacao/01_thread_side_000.png
```

### EfficientAD-M
```text
screw/anomalias_menor_score/02_thread_side_004.png
```

Objetivo:
mostrar diferentes comportamentos para defeitos pequenos.

---

## Figura comparativa 3 — `leather`

### PatchCore
```text
leather/pior_localizacao/03_fold_004.png
```

### EfficientAD-M
```text
leather/pior_localizacao/03_fold_009.png
```

Objetivo:
mostrar que ambos funcionam bem, mas com mapas espacialmente diferentes.

---

# 22. Sobre a diferença do AU-PRO do PatchCore

O script oficial da configuração PatchCore IM224 reporta aproximadamente:

```text
PRO ≈ 0.944
```

Na avaliação padronizada realizada neste estudo foi obtido:

```text
AU-PRO = 0.912930
```

Essa diferença deve ser registrada.

## Possíveis fatores

- versão do código;
- versão das bibliotecas;
- procedimento de exportação dos mapas;
- redimensionamento para a resolução original;
- detalhes do protocolo de avaliação;
- diferenças de ambiente.

## Como escrever no relatório

> O AU-PRO médio obtido para o PatchCore na avaliação padronizada foi de 0,9129, inferior ao valor de aproximadamente 0,944 indicado no script de referência da implementação oficial. Como o Image AUROC reproduzido permaneceu praticamente idêntico ao obtido na avaliação original, a diferença parece estar associada especificamente ao pipeline de localização e avaliação dos anomaly maps. Essa discrepância foi mantida documentada e deve ser considerada na interpretação da comparação.

## Importante

Não afirmar que:

```text
"a reprodução do PatchCore está errada"
```

sem evidência adicional.

---

# 23. Cuidados de interpretação

Evitar afirmações absolutas como:

```text
"EfficientAD é melhor que PatchCore."
"PatchCore é pior para localização."
"EfficientAD sempre localiza melhor."
```

Preferir:

```text
"Nesta reprodução..."
"Sob o protocolo padronizado utilizado..."
"Em média..."
"Na maioria das categorias avaliadas..."
```

Exemplo seguro:

> Sob o protocolo padronizado utilizado neste estudo, o EfficientAD-M apresentou AU-PRO médio superior ao PatchCore, enquanto os dois métodos apresentaram Image AUROC médio praticamente equivalente.

---

# 24. Conclusões da comparação

## Principais conclusões

1. Os dois métodos apresentam Image AUROC médio próximo de 0,99.
2. A diferença média em detecção é inferior a 0,1 ponto percentual.
3. O EfficientAD-M apresentou AU-PRO médio aproximadamente 2,32 pontos percentuais superior.
4. A vantagem de localização do EfficientAD-M não ocorre em todas as categorias.
5. PatchCore apresentou AU-PRO superior em `transistor`, `hazelnut`, `grid` e `carpet`.
6. EfficientAD-M apresentou ganhos expressivos em `metal_nut`, `wood`, `toothbrush` e `tile`.
7. Os anomaly maps apresentam padrões qualitativamente diferentes entre os métodos.
8. O custo experimental do EfficientAD-M é muito superior ao do PatchCore.
9. A comparação quantitativa só se tornou adequada após padronização do avaliador.
10. A avaliação por categoria é essencial para interpretar as médias globais.

---

# 25. Texto sugerido para conclusão da seção

> A comparação padronizada mostrou que PatchCore e EfficientAD-M apresentam desempenho praticamente equivalente em detecção de anomalias em nível de imagem, ambos com Image AUROC médio próximo de 0,99. Em localização, o EfficientAD-M apresentou AU-PRO médio superior, embora essa vantagem varie significativamente entre categorias. A análise qualitativa revelou ainda diferenças no formato dos mapas de anomalia, com o PatchCore produzindo respostas frequentemente mais suaves e o EfficientAD-M apresentando ativações mais concentradas e, em alguns casos, subsegmentadas. Além do desempenho, o custo experimental diferencia fortemente as abordagens: o PatchCore foi executado em poucos minutos, enquanto o EfficientAD-M exigiu aproximadamente 30 horas de treinamento acumulado. Esses resultados indicam que a escolha da baseline deve considerar simultaneamente desempenho, comportamento por categoria, qualidade espacial dos mapas e custo computacional.

---

# 26. Estado da etapa

```text
Baselines CV — MVTec AD
├── PatchCore reproduzido              ✅
├── EfficientAD-M reproduzido          ✅
├── Análises qualitativas              ✅
├── Avaliação padronizada              ✅
├── Comparação quantitativa            ✅
├── Comparação qualitativa             ✅
└── Documentação comparativa           ✅
```

---

# 27. Próximo passo recomendado

Com a comparação das duas baselines concluída, há dois caminhos naturais.

## Opção 1 — ampliar as baselines clássicas

Adicionar uma terceira baseline, preferencialmente de natureza diferente.

Exemplos possíveis:

```text
PaDiM
FastFlow
CFLOW-AD
```

## Opção 2 — avançar para MVTec LOCO AD

Reproduzir PatchCore e EfficientAD-M no MVTec LOCO AD e analisar:

```text
anomalias estruturais
vs.
anomalias lógicas
```

Esse caminho é particularmente interessante porque aproxima o estudo da etapa futura com VLMs, já que o LOCO AD contém anomalias que dependem mais de relações e contexto global do objeto.

## Recomendação para a sequência do projeto

A sequência mais coerente é:

```text
MVTec AD
    ↓
PatchCore + EfficientAD-M
    ↓
comparação padronizada
    ↓
MVTec LOCO AD
    ↓
anomalias estruturais × lógicas
    ↓
VLMs
    ↓
CV + VLM
```

Isso mantém uma progressão experimental clara e alinhada ao objetivo do projeto.
