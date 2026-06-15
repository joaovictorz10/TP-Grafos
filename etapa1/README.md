# Etapa 1 — Modelagem e Planejamento da Solução

Implementação da mineração de dados do repositório GitHub escolhido, responsável por
transformar as interações entre colaboradores em grafos.

## Conteúdo

- `miner.py` — classe `GithubMiner`:
  - `fetch_data(pages)`: consome a API REST do GitHub e coleta, para cada `issue`/`pull request`:
    - comentários em issues/PRs;
    - fechamento de issues por outro usuário;
    - revisões/aprovações e merges de pull requests.
  - `build_graphs()`: constrói 4 grafos (`AdjacencyListGraph`, de [`etapa2/core`](../etapa2/core)), um nó por usuário:
    - **Grafo 1**: comentários em issues/PRs;
    - **Grafo 2**: fechamento de issue por outro usuário;
    - **Grafo 3**: revisões/aprovações/merges de PRs;
    - **Grafo integrado**: combinação ponderada de todas as interações.

## Esquema de pesos (grafo integrado)

| Interação | Peso |
|---|---|
| Comentário em issue ou pull request | 2 |
| Abertura de issue comentada por outro usuário | 3 |
| Revisão/aprovação de pull request | 4 |
| Merge de pull request | 5 |

A justificativa, contextualização do repositório escolhido e o detalhamento da
estratégia de coleta estão no relatório (`relatorio/relatorio tex/relatorio.tex`,
seção "Modelagem do Problema").

## Como executar a mineração

A mineração real (com dados do GitHub) é disparada pelo `main.py`, na raiz do
projeto, que usa `GithubMiner` internamente. É necessário configurar o `.env` na
raiz com:

```bash
GITHUB_TOKEN=seu_token_pessoal_do_github
GITHUB_REPOSITORY=devlikeapro/waha
```

```bash
python main.py
```

O parâmetro `pages` de `fetch_data(pages)` controla quantas páginas de issues/PRs são
buscadas na API (cada página tem até 100 itens). Sem `GITHUB_TOKEN`, o limite de
requisições da API do GitHub é menor (60/h) e a mineração pode ser interrompida por
*rate limit* em repositórios grandes.

## Saída gerada

Ao final da execução de `main.py`, esta etapa contribui com:

- `resultados/<owner>-<repo>/grafo_comentarios.csv` (G1), `grafo_fechamentos.csv`
  (G2), `grafo_revisoes_merges.csv` (G3) e `grafo_integrado.csv` (grafo ponderado),
  todos prontos para importação no [Gephi](https://gephi.org/);
- `resultados/<owner>-<repo>/relatorio_mineracao.txt` — total de usuários, total de
  interações, densidade da rede e top 5 usuários por PageRank.

## Testes

```bash
python -m pytest etapa1/tests
```

Os testes em `tests/test_miner.py` usam mocks da API do GitHub para validar que
`fetch_data` e `build_graphs` extraem corretamente usuários, arestas e pesos para
os 4 grafos, sem depender de rede.
