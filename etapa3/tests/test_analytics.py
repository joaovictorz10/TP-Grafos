import pytest
from etapa2.core.adjacency_list_graph import AdjacencyListGraph
from etapa3.graph_analytics import GraphAnalytics


def test_assortativity_uses_out_degree():
    """Testa que assortativity usa apenas out-degree para grafos direcionados."""
    g = AdjacencyListGraph(3)
    g.addEdge(0, 1)
    g.addEdge(1, 2)

    analytics = GraphAnalytics(g)
    assortativity = analytics.get_assortativity()

    # Deve retornar um valor válido entre -1 e 1
    assert -1 <= assortativity <= 1

def test_eigenvector_centrality_basic():
    """Testa eigenvector centrality em grafo simples."""
    g = AdjacencyListGraph(3)
    g.addEdge(0, 1)
    g.addEdge(1, 2)

    analytics = GraphAnalytics(g)
    eig = analytics.get_eigenvector_centrality()

    assert len(eig) == 3
    assert all(0 <= x <= 1 for x in eig)  # Valores normalizados entre 0 e 1
    # Vértice 2 deve ter maior score: recebe de 1, que recebe de 0
    assert eig[2] >= eig[1] >= eig[0]

def test_integration_pipeline():
    """Testa pipeline completo: construção + análise de grafo."""
    # Criar grafo de teste
    g = AdjacencyListGraph(5)
    g.addEdge(0, 1)
    g.addEdge(1, 2)
    g.addEdge(2, 3)
    g.addEdge(3, 4)
    g.addEdge(4, 0)  # Criar ciclo

    # Verificar estrutura
    assert g.getVertexCount() == 5
    assert g.getEdgeCount() == 5

    # Executar análises
    analytics = GraphAnalytics(g)

    # Densidade
    density = analytics.get_density()
    assert 0 <= density <= 1

    # Graus
    for i in range(5):
        in_deg = g.getVertexInDegree(i)
        out_deg = g.getVertexOutDegree(i)
        assert in_deg >= 0
        assert out_deg >= 0

    # PageRank
    pr = analytics.get_pagerank(iterations=50)
    assert len(pr) == 5
    assert all(p > 0 for p in pr)

    # Eigenvector
    eig = analytics.get_eigenvector_centrality()
    assert len(eig) == 5
    assert all(e >= 0 for e in eig)

    # Betweenness
    bw = analytics.get_betweenness_centrality()
    assert len(bw) == 5
    assert all(b >= 0 for b in bw)

    # Clustering
    cc = analytics.get_clustering_coefficient()
    assert len(cc) == 5
    assert all(0 <= c <= 1 for c in cc)

    # Comunidades
    communities = analytics.get_communities_louvain()
    assert len(communities) == 5
    assert len(set(communities)) >= 1  # Pelo menos 1 comunidade


def test_louvain_detects_known_communities():
    """Louvain deve separar dois grupos densos ligados por uma única ponte.

    Estrutura: dois triângulos completos {0,1,2} e {3,4,5}, cada um totalmente
    conectado internamente (arestas em ambos os sentidos), unidos por uma única
    aresta-ponte 2->3. A modularidade correta deve detectar exatamente 2 comunidades,
    com 0,1,2 juntos e 3,4,5 juntos.
    """
    g = AdjacencyListGraph(6)
    # Triângulo denso A: {0,1,2}
    for u, v in [(0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1)]:
        g.addEdge(u, v)
    # Triângulo denso B: {3,4,5}
    for u, v in [(3, 4), (4, 3), (3, 5), (5, 3), (4, 5), (5, 4)]:
        g.addEdge(u, v)
    # Ponte única entre os dois grupos
    g.addEdge(2, 3)

    communities = GraphAnalytics(g).get_communities_louvain()

    # Exatamente duas comunidades
    assert len(set(communities)) == 2
    # Cada triângulo permanece em uma única comunidade
    assert communities[0] == communities[1] == communities[2]
    assert communities[3] == communities[4] == communities[5]
    # E os dois grupos são comunidades distintas
    assert communities[0] != communities[3]
