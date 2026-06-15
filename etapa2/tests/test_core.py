import pytest
from etapa2.core.adjacency_matrix_graph import AdjacencyMatrixGraph
from etapa2.core.adjacency_list_graph import AdjacencyListGraph

# Roda os mesmos testes para ambas as estruturas de dados
@pytest.fixture(params=[AdjacencyMatrixGraph, AdjacencyListGraph])
def graph_class(request):
    return request.param

def test_graph_creation(graph_class):
    """Testa se o grafo recusa instâncias vazias/negativas."""
    with pytest.raises(ValueError):
        g = graph_class(0)

    g = graph_class(5)
    assert g.getVertexCount() == 5
    assert g.getEdgeCount() == 0
    assert g.isEmptyGraph() is True

def test_add_edge_and_idempotence(graph_class):
    """Testa a criação de arestas e garante que múltiplas arestas não são criadas (idempotência)."""
    g = graph_class(3)
    g.addEdge(0, 1)

    assert g.hasEdge(0, 1) is True
    assert g.hasEdge(1, 0) is False # Direcionado
    assert g.getEdgeCount() == 1

    # Teste de idempotência
    g.addEdge(0, 1)
    assert g.getEdgeCount() == 1

def test_simple_graph_restriction(graph_class):
    """Testa se o grafo rejeita laços, mantendo a regra de Grafo Simples."""
    g = graph_class(3)
    with pytest.raises(ValueError):
        g.addEdge(1, 1)

def test_divergent_convergent(graph_class):
    """Testa as lógicas de divergência e convergência."""
    g = graph_class(5)
    g.addEdge(0, 1)
    g.addEdge(0, 2) # 0 diverge para 1 e 2

    g.addEdge(3, 4)
    g.addEdge(2, 4) # 3 e 2 convergem para 4

    assert g.isDivergent(0, 1, 0, 2) is True
    assert g.isConvergent(3, 4, 2, 4) is True

def test_remove_edge(graph_class):
    """Testa remoção de arestas."""
    g = graph_class(3)
    g.addEdge(0, 1)
    assert g.getEdgeCount() == 1

    g.removeEdge(0, 1)
    assert g.getEdgeCount() == 0
    assert g.hasEdge(0, 1) is False

def test_vertex_degrees(graph_class):
    """Testa cálculo de in-degree e out-degree."""
    g = graph_class(4)
    g.addEdge(0, 1)
    g.addEdge(0, 2)
    g.addEdge(3, 1)

    # Vértice 0: out-degree = 2, in-degree = 0
    assert g.getVertexOutDegree(0) == 2
    assert g.getVertexInDegree(0) == 0

    # Vértice 1: out-degree = 0, in-degree = 2
    assert g.getVertexOutDegree(1) == 0
    assert g.getVertexInDegree(1) == 2

def test_vertex_weights(graph_class):
    """Testa pesos de vértices."""
    g = graph_class(3)

    g.setVertexWeight(0, 5.0)
    assert g.getVertexWeight(0) == 5.0

    g.setVertexWeight(1, 3.5)
    assert g.getVertexWeight(1) == 3.5

def test_edge_weights(graph_class):
    """Testa pesos de arestas."""
    g = graph_class(3)
    g.addEdge(0, 1)

    g.setEdgeWeight(0, 1, 2.5)
    assert g.getEdgeWeight(0, 1) == 2.5

    g.addEdge(1, 2)
    g.setEdgeWeight(1, 2, 4.0)
    assert g.getEdgeWeight(1, 2) == 4.0

def test_invalid_indices(graph_class):
    """Testa exceções para índices inválidos."""
    g = graph_class(3)

    with pytest.raises(IndexError):
        g.hasEdge(5, 1)

    with pytest.raises(IndexError):
        g.addEdge(-1, 2)

    with pytest.raises(IndexError):
        g.getVertexWeight(10)

def test_successor_predecessor(graph_class):
    """Testa relações de sucessor e predecessor."""
    g = graph_class(3)
    g.addEdge(0, 1)

    # 1 é sucessor de 0
    assert g.isSucessor(0, 1) is True
    assert g.isSucessor(1, 0) is False

    # 0 é predecessor de 1
    assert g.isPredessor(0, 1) is False
    assert g.isPredessor(1, 0) is True

def test_incident(graph_class):
    """Testa incidência de arestas."""
    g = graph_class(4)
    g.addEdge(0, 1)
    g.addEdge(1, 2)

    # Vértice 0 está incidente na aresta (0, 1)
    assert g.isIncident(0, 1, 0) is True
    assert g.isIncident(0, 1, 1) is True
    assert g.isIncident(0, 1, 2) is False

def test_empty_graph(graph_class):
    """Testa verificação de grafo vazio."""
    g = graph_class(5)
    assert g.isEmptyGraph() is True

    g.addEdge(0, 1)
    assert g.isEmptyGraph() is False

def test_complete_graph(graph_class):
    """Testa verificação de grafo completo."""
    g = graph_class(3)
    assert g.isCompleteGraph() is False

    # Adiciona todas as arestas possíveis
    g.addEdge(0, 1)
    g.addEdge(0, 2)
    g.addEdge(1, 0)
    g.addEdge(1, 2)
    g.addEdge(2, 0)
    g.addEdge(2, 1)

    assert g.isCompleteGraph() is True

def test_connected_graph(graph_class):
    """Testa verificação de conectividade."""
    g = graph_class(3)
    # Grafo desconectado
    g.addEdge(0, 1)
    assert g.isConnected() is False

    # Conecta todos os vértices
    g.addEdge(1, 2)
    assert g.isConnected() is True

def test_export_gephi(graph_class, tmp_path):
    """Testa exportação para GEPHI em formato CSV."""
    g = graph_class(3)
    g.addEdge(0, 1)
    g.addEdge(1, 2)

    # Atribuir rótulos
    g.vertexLabels = ["user_a", "user_b", "user_c"]

    # Exportar para arquivo temporário
    export_file = tmp_path / "test_graph.csv"
    g.exportToGEPHI(str(export_file))

    # Verificar que o arquivo foi criado
    assert export_file.exists()

    # Verificar conteúdo
    with open(export_file, 'r') as f:
        content = f.read()
        assert "Source" in content
        assert "Target" in content
        assert "Weight" in content
        assert "user_a" in content

def test_vertex_labels(graph_class):
    """Testa rótulos de vértices."""
    g = graph_class(3)

    g.vertexLabels[0] = "alice"
    g.vertexLabels[1] = "bob"
    g.vertexLabels[2] = "charlie"

    assert g.vertexLabels[0] == "alice"
    assert g.vertexLabels[1] == "bob"
    assert g.vertexLabels[2] == "charlie"

def test_multiple_edges_same_vertices(graph_class):
    """Testa que múltiplas arestas entre mesmos vértices são evitadas."""
    g = graph_class(2)

    g.addEdge(0, 1)
    initial_count = g.getEdgeCount()

    g.addEdge(0, 1)
    assert g.getEdgeCount() == initial_count  # Não aumenta

def test_directed_graph_asymmetry(graph_class):
    """Testa assimetria de grafo direcionado."""
    g = graph_class(2)
    g.addEdge(0, 1)

    assert g.hasEdge(0, 1) is True
    assert g.hasEdge(1, 0) is False  # Grafo é direcionado

def test_large_graph_performance(graph_class):
    """Testa desempenho com grafo maior."""
    g = graph_class(100)

    # Adiciona múltiplas arestas
    for i in range(90):
        g.addEdge(i, i + 1)

    assert g.getEdgeCount() == 90
    assert g.getVertexCount() == 100

def test_weight_accumulation(graph_class):
    """Testa comportamento com pesos."""
    g = graph_class(2)
    g.addEdge(0, 1)

    # Define peso inicial
    g.setEdgeWeight(0, 1, 5.0)
    assert g.getEdgeWeight(0, 1) == 5.0

    # Atualiza peso
    g.setEdgeWeight(0, 1, 10.0)
    assert g.getEdgeWeight(0, 1) == 10.0

def test_remove_nonexistent_edge(graph_class):
    """Testa remoção de aresta inexistente."""
    g = graph_class(2)

    # Tenta remover aresta que não existe
    g.removeEdge(0, 1)
    assert g.getEdgeCount() == 0

def test_edge_weight_error_nonexistent(graph_class):
    """Testa erro ao acessar peso de aresta inexistente."""
    g = graph_class(2)

    with pytest.raises(ValueError):
        g.getEdgeWeight(0, 1)

def test_set_weight_nonexistent_edge(graph_class):
    """Testa erro ao definir peso de aresta inexistente."""
    g = graph_class(2)

    with pytest.raises(ValueError):
        g.setEdgeWeight(0, 1, 5.0)

def test_graph_with_isolated_vertices(graph_class):
    """Testa grafo com vértices isolados."""
    g = graph_class(5)

    g.addEdge(0, 1)
    g.addEdge(2, 3)

    # Vértice 4 é isolado
    assert g.getVertexOutDegree(4) == 0
    assert g.getVertexInDegree(4) == 0

def test_self_loops_consistently_rejected(graph_class):
    """Testa que laços sempre são rejeitados."""
    g = graph_class(5)

    for i in range(5):
        with pytest.raises(ValueError):
            g.addEdge(i, i)

def test_convergence_divergence_complex(graph_class):
    """Testa convergência e divergência em grafo mais complexo."""
    g = graph_class(6)

    # Cria padrão: 0 -> 1, 0 -> 2 (divergente)
    g.addEdge(0, 1)
    g.addEdge(0, 2)

    # Cria padrão: 3 -> 4, 5 -> 4 (convergente)
    g.addEdge(3, 4)
    g.addEdge(5, 4)

    assert g.isDivergent(0, 1, 0, 2) is True
    assert g.isConvergent(3, 4, 5, 4) is True
    assert g.isDivergent(3, 4, 5, 4) is False
    assert g.isConvergent(0, 1, 0, 2) is False

def test_edge_count_accuracy(graph_class):
    """Testa precisão da contagem de arestas."""
    g = graph_class(10)

    count = 0
    for i in range(9):
        g.addEdge(i, i + 1)
        count += 1
        assert g.getEdgeCount() == count

def test_vertex_weight_default(graph_class):
    """Testa peso padrão de vértices."""
    g = graph_class(3)

    # Todos os vértices devem começar com peso padrão (1.0)
    for i in range(3):
        assert g.getVertexWeight(i) == 1.0

def test_edge_weight_default(graph_class):
    """Testa peso padrão de arestas."""
    g = graph_class(2)
    g.addEdge(0, 1)

    # Peso padrão é 1.0
    assert g.getEdgeWeight(0, 1) == 1.0

def test_in_degree_optimization_matrix(graph_class):
    """Testa que getVertexInDegree é O(1) em matriz com cache."""
    if graph_class == AdjacencyMatrixGraph:
        g = graph_class(5)
        g.addEdge(0, 1)
        g.addEdge(2, 1)
        g.addEdge(3, 1)

        # Deve retornar 3 rapidamente (usando cache, não loop)
        assert g.getVertexInDegree(1) == 3

        # Remover aresta
        g.removeEdge(2, 1)
        assert g.getVertexInDegree(1) == 2

def test_encapsulation_vertex_labels():
    """Testa que vertexLabels usa property com validação."""
    g = AdjacencyListGraph(3)

    # Deve permitir atribuir
    g.vertexLabels = ["a", "b", "c"]
    assert g.vertexLabels == ["a", "b", "c"]

    # Deve rejeitar tamanho incorreto
    with pytest.raises(ValueError):
        g.vertexLabels = ["a", "b"]  # Faltam rótulos
