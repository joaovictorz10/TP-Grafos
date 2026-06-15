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

## Testes

```bash
python -m pytest etapa1/tests
```

Os testes em `tests/test_miner.py` usam mocks da API do GitHub para validar que
`fetch_data` e `build_graphs` extraem corretamente usuários, arestas e pesos para
os 4 grafos, sem depender de rede.
