# Etapa 2 — Desenvolvimento da Ferramenta

Implementação da estrutura de grafos, com herança/abstração e a API obrigatória do
trabalho.

## Estrutura de classes (`core/`)

- `abstract_graph.py` — classe abstrata `AbstractGraph`: define a API comum, atributos
  compartilhados (rótulos e pesos de vértices) e métodos auxiliares (ex.: validação de índices).
- `adjacency_matrix_graph.py` — `AdjacencyMatrixGraph(numVertices)`: implementação com
  matriz de adjacência.
- `adjacency_list_graph.py` — `AdjacencyListGraph(numVertices)`: implementação com listas
  de adjacência.

## API obrigatória implementada

`getVertexCount`, `getEdgeCount`, `hasEdge`, `addEdge`, `removeEdge`, `isSucessor`,
`isPredessor`, `isDivergent`, `isConvergent`, `isIncident`, `getVertexInDegree`,
`getVertexOutDegree`, `setVertexWeight`/`getVertexWeight`, `setEdgeWeight`/`getEdgeWeight`,
`isConnected`, `isEmptyGraph`, `isCompleteGraph`, `exportToGEPHI`.

## Restrições atendidas

- Grafos simples: sem laços, sem múltiplas arestas;
- `addEdge(u, v)` é idempotente;
- Índices inválidos e operações inconsistentes lançam exceções;
- Nenhuma biblioteca de grafos pronta (ex.: networkX) é utilizada.

## Aplicação de demonstração

`demo_api.py` é a aplicação separada que consome a API e demonstra todas as operações
disponíveis em ambas as implementações (`AdjacencyMatrixGraph` e `AdjacencyListGraph`),
além de rodar a mineração (Etapa 1) e a análise (Etapa 3) sobre o repositório configurado.

```bash
python etapa2/demo_api.py
```

## Testes

```bash
python -m pytest etapa2/tests
```

`tests/test_core.py` cobre criação, manipulação de arestas/pesos, relações entre arestas,
propriedades do grafo (conexo, vazio, completo) e exportação para o Gephi — para ambas as
implementações.
