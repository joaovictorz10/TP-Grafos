# ============================================================================
# ADJACENCY LIST GRAPH — Implementação com Lista de Adjacência
# ============================================================================
# Representação: Lista de dicionários para armazenar arestas
# Eficiência: O(V + E) espaço, O(grau) acesso a aresta
# Melhor para: Grafos esparsos (nosso caso: 481 vértices, 1409 arestas)
# ============================================================================

from .abstract_graph import AbstractGraph

class AdjacencyListGraph(AbstractGraph):
    # =========================================================================
    # INICIALIZAÇÃO — Cria estrutura de lista de adjacência
    # =========================================================================
    def __init__(self, numVertices: int):
        """
        Inicializa grafo vazio com lista de adjacência.

        Args:
            numVertices: Número de vértices (0 a numVertices-1)

        Estrutura:
            self.adj_list = [
                {1: 2.0, 3: 4.0},    # nó 0: tem arestas para 1 (peso 2) e 3 (peso 4)
                {0: 3.0, 2: 5.0},    # nó 1: tem arestas para 0 (peso 3) e 2 (peso 5)
                {},                   # nó 2: sem arestas saintes
                {}                    # nó 3: sem arestas saintes
            ]

        Complexidade:
            - Espaço: O(V + E) — armazena apenas arestas que existem
            - Construção: O(V) — cria V dicionários vazios
        """
        # Chama construtor da classe pai (AbstractGraph)
        # Isso inicializa:
        # - self.numVertices = numVertices
        # - self._vertexWeights = [1.0] * numVertices
        # - self._vertexLabels = [str(i) for i in range(numVertices)]
        super().__init__(numVertices)

        # =====================================================================
        # ESTRUTURA PRINCIPAL — Lista de dicionários
        # =====================================================================
        # self.adj_list[u] = {v: weight, ...}
        # Cada índice u é um vértice
        # Cada dicionário mapeia vértice destino v para peso da aresta
        # Exemplo: adj_list[0] = {1: 2.0, 3: 4.0} significa:
        #          vértice 0 tem arestas para:
        #          - vértice 1 com peso 2.0 (comentário)
        #          - vértice 3 com peso 4.0 (revisão)
        self.adj_list = [{} for _ in range(numVertices)]

        # =====================================================================
        # CONTADOR DE ARESTAS — Cache para O(1) getEdgeCount()
        # =====================================================================
        # Mantém total de arestas (sem contar duas vezes)
        # Necessário para métodos que precisam saber número de arestas
        # Exemplo: densidade = arestas / (vértices * (vértices - 1))
        self._edgeCount = 0

    # =========================================================================
    # CONSULTA DE ARESTAS — Verifica propriedades básicas
    # =========================================================================
    def getEdgeCount(self) -> int:
        """
        Retorna número total de arestas no grafo.

        Returns:
            int: Número de arestas direcionadas

        Complexidade: O(1) — valor cacheado
        """
        return self._edgeCount

    def hasEdge(self, u: int, v: int) -> bool:
        """
        Verifica se existe aresta direcionada de u para v.

        Args:
            u: Vértice origem (0 a numVertices-1)
            v: Vértice destino (0 a numVertices-1)

        Returns:
            bool: True se existe aresta u → v, False caso contrário

        Complexidade:
            O(1) em média (dicionário hash)
            O(grau de u) no pior caso (improvável em hash)

        Validação:
            Lança IndexError se u ou v estão fora de limites
        """
        # Valida índices
        self._check_vertex(u)
        self._check_vertex(v)

        # Verifica se v está no dicionário do vértice u
        # v in self.adj_list[u] retorna True/False em O(1)
        return v in self.adj_list[u]

    # =========================================================================
    # ADIÇÃO DE ARESTAS — Garante propriedades do grafo
    # =========================================================================
    def addEdge(self, u: int, v: int) -> None:
        """
        Adiciona aresta direcionada de u para v com peso padrão 1.0.

        Args:
            u: Vértice origem
            v: Vértice destino

        Restrições:
            1. u != v (grafo simples: sem self-loops)
            2. Idempotência: chamar 2× com mesmo (u,v) não duplica aresta
            3. Sempre com peso padrão 1.0 (usar setEdgeWeight() depois para alterar)

        Comportamento:
            - Primeira chamada addEdge(0, 1): cria aresta 0→1 com peso 1.0
            - Segunda chamada addEdge(0, 1): não faz nada (idempotência)
            - Para alterar peso: addEdge() depois setEdgeWeight() (ou setEdgeWeight() direto)

        Complexidade:
            O(1) em média — inserção em dicionário hash
        """
        # Valida índices
        self._check_vertex(u)
        self._check_vertex(v)

        # =====================================================================
        # RESTRIÇÃO 1: Grafo simples (sem self-loops)
        # =====================================================================
        # Se u == v, lança exceção
        # Restrição do enunciado TP-ES.pdf: "grafos devem ser simples"
        if u == v:
            raise ValueError("Grafos devem ser simples: laços não são permitidos.")

        # =====================================================================
        # RESTRIÇÃO 2: Idempotência
        # =====================================================================
        # Se aresta já existe, não faz nada
        # Garante que múltiplas chamadas com mesmo (u,v) não duplicam
        # Isto é essencial para construção pós-mineração:
        # - GithubMiner acumula pesos em dicionário
        # - build_graphs() chama addEdge() uma vez por par único
        # - Se try-add-add ocorresse, quebraria construção
        if v not in self.adj_list[u]:
            # Aresta nova: criar com peso padrão 1.0
            # Depois, minerador chama setEdgeWeight() com peso real (2.0, 3.0, etc.)
            self.adj_list[u][v] = 1.0

            # Incrementa contador de arestas
            self._edgeCount += 1

    def removeEdge(self, u: int, v: int) -> None:
        """
        Remove aresta direcionada de u para v.

        Args:
            u: Vértice origem
            v: Vértice destino

        Comportamento:
            - Se aresta existe: remove e decrementa contador
            - Se aresta não existe: silenciosamente ignora (não erro)

        Complexidade:
            O(1) em média — deleção em dicionário hash
        """
        # Valida índices
        self._check_vertex(u)
        self._check_vertex(v)

        # Verifica se aresta existe antes de deletar
        if v in self.adj_list[u]:
            # Remove entrada do dicionário
            del self.adj_list[u][v]

            # Decrementa contador
            self._edgeCount -= 1

    # =========================================================================
    # GRAUS — Mede conectividade de vértices
    # =========================================================================
    def getVertexInDegree(self, u: int) -> int:
        """
        Retorna in-degree do vértice u.

        In-degree = número de arestas que CHEGAM em u
        Interpretação: "quantos vértices apontam para u?"

        Args:
            u: Vértice (0 a numVertices-1)

        Returns:
            int: Número de vértices v tal que existe aresta v → u

        Exemplo (grafo com 3 arestas):
            0 → 1 (peso 2)
            2 → 1 (peso 3)
            0 → 2 (peso 4)

            getVertexInDegree(1) = 2 (arestas 0→1, 2→1)
            getVertexInDegree(0) = 0 (nenhuma aresta chega em 0)
            getVertexInDegree(2) = 1 (aresta 0→2)

        Complexidade:
            O(V) — necessário iterar todos os vértices para contar arestas entrantes
            (lista de adjacência não armazena arestas entrantes diretamente)

        Nota:
            Para grafo com 481 vértices: 481 iterações por chamada
            Alternativa: manter matriz de arestas entrantes (O(E) espaço extra)
            Tradeoff: tempo vs espaço. Escolhemos tempo (métodos de análise chamam raras vezes)
        """
        # Valida índice
        self._check_vertex(u)

        # Contador de arestas entrantes
        degree = 0

        # Itera TODOS os vértices
        for i in range(self.numVertices):
            # Para cada vértice i, verifica se u está em seu dicionário
            # u in self.adj_list[i] = "existe aresta i → u?"
            if u in self.adj_list[i]:
                # Encontrou uma aresta entrante: i → u
                degree += 1

        return degree

    def getVertexOutDegree(self, u: int) -> int:
        """
        Retorna out-degree do vértice u.

        Out-degree = número de arestas que SAEM de u
        Interpretação: "para quantos vértices u aponta?"

        Args:
            u: Vértice (0 a numVertices-1)

        Returns:
            int: Número de vértices v tal que existe aresta u → v

        Exemplo (mesmo grafo anterior):
            getVertexOutDegree(0) = 2 (arestas 0→1, 0→2)
            getVertexOutDegree(1) = 0 (nenhuma aresta sai de 1)
            getVertexOutDegree(2) = 1 (aresta 2→1)

        Complexidade:
            O(1) — apenas conta elementos do dicionário self.adj_list[u]
            len(dict) é O(1) em Python (tamanho cacheado)

        Nota:
            Out-degree é muito mais rápido que in-degree (O(1) vs O(V))
            Por isso: PageRank calcula out-degree, Betweenness usa in-degree
        """
        # Valida índice
        self._check_vertex(u)

        # Retorna tamanho do dicionário do vértice u
        # Cada entrada {v: weight} = 1 aresta sainte
        return len(self.adj_list[u])

    # =========================================================================
    # PESOS DE ARESTAS — Define e consulta pesos
    # =========================================================================
    def setEdgeWeight(self, u: int, v: int, w: float) -> None:
        """
        Define o peso de uma aresta existente.

        Args:
            u: Vértice origem
            v: Vértice destino
            w: Novo peso (float)

        Restrições:
            - Aresta DEVE existir (u → v já foi criada com addEdge())
            - Se não existir: lança ValueError

        Fluxo típico:
            1. addEdge(u, v)           # cria com peso padrão 1.0
            2. setEdgeWeight(u, v, 2.0)  # atualiza para peso real

            Usado em build_graphs():
            ```python
            if not graph.hasEdge(u, v):
                graph.addEdge(u, v)
                graph.setEdgeWeight(u, v, weight)
            else:
                # acumula pesos de múltiplas interações
                graph.setEdgeWeight(u, v, graph.getEdgeWeight(u, v) + weight)
            ```

        Complexidade:
            O(1) — atribuição em dicionário hash
        """
        # Valida índices
        self._check_vertex(u)
        self._check_vertex(v)

        # Verifica se aresta existe
        if v not in self.adj_list[u]:
            # Aresta não existe: erro
            raise ValueError(f"Aresta ({u}, {v}) não existe.")

        # Atribui novo peso
        # Sobrescreve peso anterior
        # Exemplo: setEdgeWeight(0, 1, 6.0) → adj_list[0][1] = 6.0
        self.adj_list[u][v] = w

    def getEdgeWeight(self, u: int, v: int) -> float:
        """
        Retorna o peso de uma aresta existente.

        Args:
            u: Vértice origem
            v: Vértice destino

        Returns:
            float: Peso da aresta u → v

        Restrições:
            - Aresta DEVE existir
            - Se não existir: lança ValueError

        Exemplo:
            addEdge(0, 1)
            setEdgeWeight(0, 1, 2.0)
            getEdgeWeight(0, 1) → 2.0

        Complexidade:
            O(1) — acesso direto em dicionário hash
        """
        # Valida índices
        self._check_vertex(u)
        self._check_vertex(v)

        # Verifica se aresta existe
        if v not in self.adj_list[u]:
            # Aresta não existe: erro
            raise ValueError(f"Aresta ({u}, {v}) não existe.")

        # Retorna peso armazenado
        return self.adj_list[u][v]