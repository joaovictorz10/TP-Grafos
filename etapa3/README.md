# Etapa 3 — Análise do Repositório Baseada em Dados

Implementação dos algoritmos e métricas de redes complexas aplicados ao grafo integrado
de colaboração construído na Etapa 1.

## Conteúdo

- `graph_analytics.py` — classe `GraphAnalytics(graph)`, recebendo qualquer
  implementação de [`AbstractGraph`](../etapa2/core/abstract_graph.py):

### Métricas de centralidade

- `get_degree_centrality(u)` — grau (in/out-degree);
- `get_betweenness_centrality()` — centralidade de intermediação (Brandes);
- `get_closeness_centrality(u)` — centralidade de proximidade (BFS);
- `get_pagerank(iterations, damping)` — PageRank;
- `get_eigenvector_centrality(iterations)` — eigenvector centrality.

### Métricas de estrutura e coesão

- `get_density()` — densidade da rede;
- `get_clustering_coefficient()` / `get_average_clustering()` — coeficiente de aglomeração;
- `get_assortativity()` — assortatividade (baseada em out-degree, grafo direcionado).

### Métricas de comunidade

- `get_communities_louvain()` — detecção de comunidades por modularidade (Louvain);
- `get_bridging_ties(communities)` — vértices que conectam diferentes comunidades.

## Relatório final

`main.py` (na raiz do projeto) executa o pipeline completo — mineração (Etapa 1),
construção dos grafos (Etapa 2) e estas análises (Etapa 3) — e grava os resultados em
`resultados/<owner>-<repo>/` (CSVs para o Gephi e relatórios `.txt` com os rankings de
centralidade, densidade, clustering, assortatividade, comunidades e bridging ties).

```bash
python main.py
```

## Testes

```bash
python -m pytest etapa3/tests
```

`tests/test_analytics.py` valida assortatividade, eigenvector centrality, detecção de
comunidades (Louvain) e um pipeline de integração completo (construção do grafo + todas
as métricas).
