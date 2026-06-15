from .abstract_graph import AbstractGraph

class AdjacencyMatrixGraph(AbstractGraph):
    """Implementação de grafo usando matriz de adjacência."""
    def __init__(self, numVertices: int):
        super().__init__(numVertices)
        self.matrix = [[None for _ in range(numVertices)] for _ in range(numVertices)]
        self._edgeCount = 0
        self._inDegrees = [0] * numVertices

    def getEdgeCount(self) -> int:
        return self._edgeCount

    def hasEdge(self, u: int, v: int) -> bool:
        self._check_vertex(u)
        self._check_vertex(v)
        return self.matrix[u][v] is not None

    def addEdge(self, u: int, v: int) -> None:
        """Adiciona uma aresta de u para v (idempotente)."""
        self._check_vertex(u)
        self._check_vertex(v)
        if u == v:
            raise ValueError("Grafos devem ser simples: laços não são permitidos.")

        if self.matrix[u][v] is None:
            self.matrix[u][v] = 1.0
            self._edgeCount += 1
            self._inDegrees[v] += 1

    def removeEdge(self, u: int, v: int) -> None:
        """Remove a aresta de u para v, se existir."""
        self._check_vertex(u)
        self._check_vertex(v)
        if self.matrix[u][v] is not None:
            self.matrix[u][v] = None
            self._edgeCount -= 1
            self._inDegrees[v] -= 1

    def getVertexInDegree(self, u: int) -> int:
        """Retorna o in-degree (número de arestas entrantes) do vértice u em O(1)."""
        self._check_vertex(u)
        return self._inDegrees[u]

    def getVertexOutDegree(self, u: int) -> int:
        """Retorna o out-degree (número de arestas saintes) do vértice u."""
        self._check_vertex(u)
        degree = 0
        for i in range(self.numVertices):
            if self.matrix[u][i] is not None:
                degree += 1
        return degree

    def setEdgeWeight(self, u: int, v: int, w: float) -> None:
        """Define o peso de uma aresta existente."""
        self._check_vertex(u)
        self._check_vertex(v)
        if self.matrix[u][v] is None:
            raise ValueError(f"Aresta ({u}, {v}) não existe.")
        self.matrix[u][v] = w

    def getEdgeWeight(self, u: int, v: int) -> float:
        """Retorna o peso de uma aresta."""
        self._check_vertex(u)
        self._check_vertex(v)
        if self.matrix[u][v] is None:
            raise ValueError(f"Aresta ({u}, {v}) não existe.")
        return self.matrix[u][v]