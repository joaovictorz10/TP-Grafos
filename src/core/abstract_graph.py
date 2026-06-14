import csv
from abc import ABC, abstractmethod

class AbstractGraph(ABC):
    """
    Classe abstrata que define a API comum para grafos simples e direcionados.

    Atributos:
        numVertices: Número de vértices no grafo
        _vertexWeights: Pesos de cada vértice
        _vertexLabels: Rótulos de cada vértice
    """
    def __init__(self, numVertices: int):
        if numVertices <= 0:
            raise ValueError("O número de vértices deve ser maior que zero.")
        self.numVertices = numVertices
        self._vertexWeights = [1.0] * numVertices
        self._vertexLabels = [str(i) for i in range(numVertices)]

    def _check_vertex(self, v: int):
        """Lança exceção para índices inválidos[cite: 72]."""
        if v < 0 or v >= self.numVertices:
            raise IndexError(f"Vértice {v} fora dos limites (0 a {self.numVertices - 1}).")

    def getVertexCount(self) -> int:
        """Retorna o número total de vértices no grafo."""
        return self.numVertices

    @abstractmethod
    def getEdgeCount(self) -> int:
        """Retorna o número total de arestas no grafo."""
        pass

    @abstractmethod
    def hasEdge(self, u: int, v: int) -> bool:
        """Verifica se existe uma aresta de u para v."""
        pass

    @abstractmethod
    def addEdge(self, u: int, v: int) -> None:
        """Adiciona uma aresta de u para v (idempotente)."""
        pass

    @abstractmethod
    def removeEdge(self, u: int, v: int) -> None:
        """Remove a aresta de u para v, se existir."""
        pass

    def isSucessor(self, u: int, v: int) -> bool:
        """Verifica se v é sucessor de u (existe aresta u->v)."""
        self._check_vertex(u)
        self._check_vertex(v)
        return self.hasEdge(u, v)

    def isPredessor(self, u: int, v: int) -> bool:
        """Verifica se v é predecessor de u (existe aresta v->u)."""
        self._check_vertex(u)
        self._check_vertex(v)
        return self.hasEdge(v, u)

    def isDivergent(self, u1: int, v1: int, u2: int, v2: int) -> bool:
        """Verifica se arestas (u1,v1) e (u2,v2) divergem (mesmo origem, destinos diferentes)."""
        return (u1 == u2) and (v1 != v2) and self.hasEdge(u1, v1) and self.hasEdge(u2, v2)

    def isConvergent(self, u1: int, v1: int, u2: int, v2: int) -> bool:
        """Verifica se arestas (u1,v1) e (u2,v2) convergem (destinos iguais, origens diferentes)."""
        return (v1 == v2) and (u1 != u2) and self.hasEdge(u1, v1) and self.hasEdge(u2, v2)

    def isIncident(self, u: int, v: int, x: int) -> bool:
        """Verifica se vértice x é incidente na aresta (u,v)."""
        return (x == u or x == v) and self.hasEdge(u, v)

    @abstractmethod
    def getVertexInDegree(self, u: int) -> int:
        """Retorna o in-degree (número de arestas entrantes) do vértice u."""
        pass

    @abstractmethod
    def getVertexOutDegree(self, u: int) -> int:
        """Retorna o out-degree (número de arestas saintes) do vértice u."""
        pass

    def setVertexWeight(self, v: int, w: float) -> None:
        """Define o peso de um vértice."""
        self._check_vertex(v)
        self._vertexWeights[v] = w

    def getVertexWeight(self, v: int) -> float:
        """Retorna o peso de um vértice."""
        self._check_vertex(v)
        return self._vertexWeights[v]

    @abstractmethod
    def setEdgeWeight(self, u: int, v: int, w: float) -> None:
        """Define o peso de uma aresta existente."""
        pass

    @abstractmethod
    def getEdgeWeight(self, u: int, v: int) -> float:
        """Retorna o peso de uma aresta."""
        pass

    def isConnected(self) -> bool:
        """Verifica conectividade fraca através de uma Busca em Largura (BFS). Ignora direção das arestas."""
        if self.numVertices == 0:
            return True
        visited = set()
        queue = [0]
        visited.add(0)

        while queue:
            current = queue.pop(0)
            for i in range(self.numVertices):
                if (self.hasEdge(current, i) or self.hasEdge(i, current)) and i not in visited:
                    visited.add(i)
                    queue.append(i)

        return len(visited) == self.numVertices

    def isEmptyGraph(self) -> bool:
        """Verifica se o grafo não possui arestas."""
        return self.getEdgeCount() == 0

    def isCompleteGraph(self) -> bool:
        """Verifica se o grafo é completo (todas as arestas possíveis existem)."""
        max_edges = self.numVertices * (self.numVertices - 1)
        return self.getEdgeCount() == max_edges

    @property
    def vertexLabels(self):
        """Retorna os rótulos dos vértices."""
        return self._vertexLabels

    @vertexLabels.setter
    def vertexLabels(self, labels):
        """Define os rótulos dos vértices."""
        if len(labels) != self.numVertices:
            raise ValueError(f"Número de rótulos ({len(labels)}) deve ser igual ao de vértices ({self.numVertices})")
        self._vertexLabels = labels

    @property
    def vertexWeights(self):
        """Retorna os pesos dos vértices."""
        return self._vertexWeights

    @vertexWeights.setter
    def vertexWeights(self, weights):
        """Define os pesos dos vértices."""
        if len(weights) != self.numVertices:
            raise ValueError(f"Número de pesos ({len(weights)}) deve ser igual ao de vértices ({self.numVertices})")
        self._vertexWeights = weights

    def exportToGEPHI(self, path: str) -> None:
        """Exporta para formato CSV de arestas aceito pelo GEPHI."""
        with open(path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Source', 'Target', 'Weight'])
            for i in range(self.numVertices):
                for j in range(self.numVertices):
                    if self.hasEdge(i, j):
                        writer.writerow([self._vertexLabels[i], self._vertexLabels[j], self.getEdgeWeight(i, j)])