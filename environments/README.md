# Ambientes registrados

As versões vêm de `logs/*_pip_freeze.txt` e `logs/*_conda_environment.yml`, preservados integralmente como evidência do ambiente experimental. Não há um ambiente único confirmado para todas as tarefas.

As listas `patchcore-requirements.txt` e `efficientad-requirements.txt` reproduzem o `pip freeze` correspondente. A referência local `packaging @ file:///home/conda/...` foi convertida para `packaging==26.3`, versão registrada nos exports Conda. Foi adicionado o índice CUDA 13.0 para localizar os builds `+cu130` registrados. Nenhuma versão foi inferida a partir da versão mais recente de um pacote.

Preparação sugerida com Conda, a partir da raiz do projeto:

```bash
conda create -n ic-patchcore python=3.11.16 pip
conda activate ic-patchcore
python -m pip install -r environments/patchcore-requirements.txt

conda create -n ic-efficientad python=3.11.16 pip
conda activate ic-efficientad
python -m pip install -r environments/efficientad-requirements.txt
```

Estes comandos não foram executados numa instalação limpa durante a publicação. A disponibilidade futura dos pacotes nos índices não é garantida. Registre qualquer substituição antes de comparar novas execuções. Os exports Conda originais incluem `prefix` específico da máquina e não devem ser aplicados cegamente em outra instalação.

O avaliador AD requer também `tabulate`, confirmado como `0.10.0` no snapshot EfficientAD; use esse ambiente para ambos os avaliadores. As dependências de análise qualitativa (`matplotlib`, entre outras) estão registradas no ambiente PatchCore. Os arquivos de requirements dos clones refletem seus ambientes originais e podem diferir dos snapshots efetivamente usados nesta IC.
