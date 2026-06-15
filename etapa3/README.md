# Etapa 3 — Análise do Repositório Baseada em Dados

Implementação dos algoritmos e métricas de redes complexas aplicados ao grafo integrado
de colaboração construído na Etapa 1.

## Métricas implementadas

- `graph_analytics.py` — classe `GraphAnalytics(graph)`, recebendo qualquer
  implementação de [`AbstractGraph`](../etapa2/core/abstract_graph.py):

### Métricas de centralidade

- `get_degree_centrality(u)` — grau (in/out-degree) do vértice `u`, normalizado pelo
  número de vértices: quantas conexões diretas o usuário tem;
- `get_betweenness_centrality()` — centralidade de intermediação (algoritmo de
  Brandes): mede em quantos caminhos mínimos entre outros pares de usuários o
  vértice aparece — identifica "pontes" da rede;
- `get_closeness_centrality(u)` — centralidade de proximidade (via BFS): inverso da
  soma das distâncias de `u` a todos os outros vértices alcançáveis;
- `get_pagerank(iterations, damping)` — PageRank (damping = 0.85 por padrão): mede a
  importância de um usuário com base em quem interage com ele e na importância de
  quem interage;
- `get_eigenvector_centrality(iterations)` — eigenvector centrality: similar ao
  PageRank, atribui maior pontuação a vértices conectados a outros vértices
  importantes.

### Métricas de estrutura e coesão

- `get_density()` — densidade da rede: razão entre o número de arestas existentes e
  o número máximo possível de arestas (`V·(V-1)` em um grafo direcionado);
- `get_clustering_coefficient()` / `get_average_clustering()` — coeficiente de
  aglomeração: para cada vértice, a fração de pares de vizinhos que também estão
  conectados entre si (tendência a formar "triângulos"/grupos fechados);
- `get_assortativity()` — assortatividade (baseada em out-degree, grafo
  direcionado): correlação entre o grau de um vértice e o grau médio de seus
  vizinhos. Valores negativos indicam padrão *hub-and-spoke* (poucos vértices muito
  conectados, ligados a muitos vértices pouco conectados).

### Métricas de comunidade

- `get_communities_louvain()` — detecção de comunidades por maximização de
  modularidade (algoritmo de Louvain): agrupa usuários que interagem mais entre si
  do que com o resto da rede;
- `get_bridging_ties(communities)` — a partir das comunidades detectadas, identifica
  os vértices cujas conexões atravessam mais comunidades distintas (conectores entre
  grupos).

## Resultados obtidos (devlikeapro/waha)

Estes são os valores gerados por `main.py` para o repositório configurado no `.env`
(ver também o [README principal](../README.md#resultados-obtidos-devlikeaprowaha)):

| Métrica | Valor |
| --- | --- |
| Densidade da rede | 0,006103 |
| Clustering médio | 0,148564 |
| Assortatividade | -0,249 (rede dissortativa) |
| Comunidades (Louvain) | 135 |
| Top 1 PageRank | `devlikepro` (0,11730) |

Os rankings completos (top 10 por métrica) ficam em
`resultados/<owner>-<repo>/analise_detalhada.txt`.

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
