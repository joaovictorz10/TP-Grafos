from collections import deque
from src.core.abstract_graph import AbstractGraph

class GraphAnalytics:
    def __init__(self, graph: AbstractGraph):
        self.graph = graph
        self.n = graph.getVertexCount()
        self._neighbors = None  # cache de vizinhos não-direcionados

    def _get_neighbors(self) -> list:
        """Pré-computa e cacheia lista de vizinhos não-direcionados."""
        if self._neighbors is not None:
            return self._neighbors
        n = self.n
        neighbors = [set() for _ in range(n)]
        for u in range(n):
            for v in range(u + 1, n):
                if self.graph.hasEdge(u, v) or self.graph.hasEdge(v, u):
                    neighbors[u].add(v)
                    neighbors[v].add(u)
        self._neighbors = neighbors
        return neighbors

    def get_density(self) -> float:
        """
        Densidade da rede: proporção entre arestas existentes e possíveis.

        Indica o quanto colaborativa é a rede como um todo (0.0 a 1.0).
        """
        if self.n <= 1:
            return 0.0
        max_edges = self.n * (self.n - 1)
        return self.graph.getEdgeCount() / max_edges

    def get_degree_centrality(self, u: int) -> dict:
        """
        Mede conexões diretas (grau de entrada e saída).

        Retorna um dicionário com in-degree, out-degree e total.
        """
        in_deg = self.graph.getVertexInDegree(u)
        out_deg = self.graph.getVertexOutDegree(u)
        return {"in": in_deg, "out": out_deg, "total": in_deg + out_deg}

    def get_pagerank(self, iterations: int = 100, damping_factor: float = 0.85) -> list:
        """
        PageRank iterativo implementado do zero.

        Mede a importância de um nó baseado em quantas arestas entram nele.
        """
        if self.n == 0:
            return []

        pr = [1.0 / self.n] * self.n

        for _ in range(iterations):
            new_pr = [(1.0 - damping_factor) / self.n] * self.n
            for u in range(self.n):
                out_deg = self.graph.getVertexOutDegree(u)
                if out_deg > 0:
                    for v in range(self.n):
                        if self.graph.hasEdge(u, v):
                            new_pr[v] += damping_factor * (pr[u] / out_deg)
                else:
                    for v in range(self.n):
                        new_pr[v] += damping_factor * (pr[u] / self.n)
            pr = new_pr
        return pr

    def get_eigenvector_centrality(self, iterations: int = 100, tolerance: float = 1e-6) -> list:
        """
        Calcula eigenvector centrality usando método de potência.

        A importância de um nó é proporcional à soma das importâncias de seus predecessores.
        Cada nó herda importância de quem aponta para ele.

        Limitação teórica: para grafos acíclicos dirigidos (DAGs), a matriz de adjacência é
        nilpotente e seu único autovalor é 0, de modo que a eigenvector centrality não está
        bem-definida (o método da potência converge para o vetor nulo). Nesses casos, o guard
        de norma abaixo retorna uma distribuição uniforme como fallback. No grafo integrado
        deste trabalho a presença de arestas anti-paralelas garante ciclos, então a métrica
        converge normalmente; ainda assim, ela é mais informativa em grafos com ciclos.

        Args:
            iterations: Número máximo de iterações
            tolerance: Tolerância de convergência

        Returns:
            Lista com eigenvector centrality de cada vértice (normalizado)
        """
        n = self.n
        if n == 0:
            return []

        x = [1.0 / n] * n

        for iteration in range(iterations):
            x_new = [0.0] * n

            for v in range(n):
                for u in range(n):
                    if self.graph.hasEdge(u, v):
                        x_new[v] += x[u]

            norm = sum(xi ** 2 for xi in x_new) ** 0.5
            if norm > tolerance:
                x_new = [xi / norm for xi in x_new]
            else:
                return [1.0 / n] * n

            diff = sum((x_new[i] - x[i]) ** 2 for i in range(n)) ** 0.5

            if diff < tolerance:
                return x_new

            x = x_new

        return x

    def get_betweenness_centrality(self) -> list:
        """
        Betweenness centrality: identifica colaboradores que atuam como pontes entre diferentes grupos.

        Mostra quais colaboradores atuam como 'pontes' entre diferentes grupos ou áreas do projeto.
        Implementação via algoritmo de Brandes com BFS.
        """
        n = self.n
        betweenness = [0.0] * n

        for s in range(n):
            stack = []
            predecessors = [[] for _ in range(n)]
            sigma = [0] * n
            sigma[s] = 1
            dist = [-1] * n
            dist[s] = 0
            queue = deque([s])

            while queue:
                v = queue.popleft()
                stack.append(v)
                for w in range(n):
                    if not self.graph.hasEdge(v, w):
                        continue
                    if dist[w] == -1:
                        queue.append(w)
                        dist[w] = dist[v] + 1
                    if dist[w] == dist[v] + 1:
                        sigma[w] += sigma[v]
                        predecessors[w].append(v)

            delta = [0.0] * n
            while stack:
                w = stack.pop()
                for v in predecessors[w]:
                    if sigma[w] > 0:
                        delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
                if w != s:
                    betweenness[w] += delta[w]

        if n > 2:
            norm = 1.0 / ((n - 1) * (n - 2))
            betweenness = [b * norm for b in betweenness]

        return betweenness

    def get_closeness_centrality(self, u: int) -> float:
        """
        Centralidade de Proximidade via BFS.

        Identifica quem está mais 'próximo' de todos os outros, ou seja, quem tem acesso rápido à informação no grafo.
        """
        distances = [-1] * self.n
        distances[u] = 0
        queue = deque([u])

        while queue:
            curr = queue.popleft()
            for v in range(self.n):
                if self.graph.hasEdge(curr, v) and distances[v] == -1:
                    distances[v] = distances[curr] + 1
                    queue.append(v)

        reachable_nodes = sum(1 for d in distances if d > 0)
        if reachable_nodes == 0:
            return 0.0

        total_distance = sum(d for d in distances if d > 0)
        return reachable_nodes / total_distance

    def get_clustering_coefficient(self) -> list:
        """
        Coeficiente de aglomeração local de cada vértice.

        Mede a tendência de colaboradores formarem 'clusters' (pequenos grupos muito conectados).
        Trata o grafo como não-direcionado.
        """
        neighbors = self._get_neighbors()
        coefficients = []

        for u in range(self.n):
            nb = list(neighbors[u])
            k = len(nb)
            if k < 2:
                coefficients.append(0.0)
                continue

            triangles = 0
            for i in range(len(nb)):
                for j in range(i + 1, len(nb)):
                    a, b = nb[i], nb[j]
                    if b in neighbors[a]:
                        triangles += 1

            max_triangles = k * (k - 1) / 2
            coefficients.append(triangles / max_triangles)

        return coefficients

    def get_average_clustering(self) -> float:
        """
        Coeficiente de aglomeração médio da rede.

        Valor médio dos coeficientes de clustering de todos os vértices.
        """
        coefficients = self.get_clustering_coefficient()
        if not coefficients:
            return 0.0
        return sum(coefficients) / len(coefficients)

    def get_assortativity(self) -> float:
        """
        Assortatividade por grau de Newman (para grafos direcionados, usa out-degree).

        Mede se nós muito conectados tendem a se ligar a outros muito conectados.
        Para grafos direcionados: usa out-degree apenas (padrão em literatura).
        """
        edges = []
        for u in range(self.n):
            for v in range(self.n):
                if self.graph.hasEdge(u, v):
                    edges.append((u, v))

        m = len(edges)
        if m == 0:
            return 0.0

        degrees = [self.graph.getVertexOutDegree(i) for i in range(self.n)]

        sum_ei = sum_ai = sum_bi = sum_sq = 0.0
        for (u, v) in edges:
            du, dv = degrees[u], degrees[v]
            sum_ei += du * dv
            sum_ai += du
            sum_bi += dv
            sum_sq += du * du + dv * dv

        sum_ei /= m
        sum_ai /= m
        sum_bi /= m
        sum_sq /= (2 * m)

        numerator = sum_ei - (sum_ai * sum_bi)
        denominator = sum_sq - (sum_ai ** 2 + sum_bi ** 2) / 2

        if denominator == 0:
            return 0.0
        return numerator / denominator

    def get_communities_louvain(self) -> list:
        """
        Detecção de comunidades via Louvain simplificado (greedy modularity).

        Permite identificar grupos de colaboradores que trabalham mais frequentemente juntos.
        Usa listas de adjacência pré-computadas para eficiência.
        """
        n = self.n
        neighbors = self._get_neighbors()

        total_edges = sum(len(nb) for nb in neighbors) // 2
        if total_edges == 0:
            return list(range(n))

        degrees = [len(neighbors[u]) for u in range(n)]
        community = list(range(n))
        sigma_tot = {c: degrees[c] for c in range(n)}
        m2 = 2 * total_edges

        improved = True
        while improved:
            improved = False
            for u in range(n):
                c_u = community[u]
                k_u = degrees[u]

                # Conta links de u para cada comunidade vizinha
                community_links = {}
                for v in neighbors[u]:
                    c_v = community[v]
                    community_links[c_v] = community_links.get(c_v, 0) + 1

                k_u_in = community_links.get(c_u, 0)
                best_community = c_u
                best_gain = 0.0

                for c, k_u_to_c in community_links.items():
                    if c == c_u:
                        continue
                    # Ganho de modularidade ao mover u de c_u para c.
                    # Forma diferencial: ΔQ = (k_u→c - k_u→c_u)/m - k_u·(Σtot(c) - Σtot(c_u) + k_u)/(2m²).
                    # O primeiro termo usa m (= total_edges); o segundo usa 2m² (= m2 * total_edges),
                    # mantendo a escala consistente entre os dois termos.
                    gain = (
                        (k_u_to_c - k_u_in) / total_edges
                        - k_u * (sigma_tot.get(c, 0) - sigma_tot.get(c_u, 0) + k_u) / (m2 * total_edges)
                    )
                    if gain > best_gain:
                        best_gain = gain
                        best_community = c

                if best_community != c_u:
                    community[u] = best_community
                    sigma_tot[c_u] = sigma_tot.get(c_u, 0) - k_u
                    sigma_tot[best_community] = sigma_tot.get(best_community, 0) + k_u
                    improved = True

        # Renumera comunidades sequencialmente
        mapping = {}
        counter = 0
        result = []
        for c in community:
            if c not in mapping:
                mapping[c] = counter
                counter += 1
            result.append(mapping[c])

        return result

    def get_bridging_ties(self, communities: list) -> list:
        """
        Bridging ties: vértices que conectam comunidades diferentes.

        Análise de quem conecta diferentes comunidades, atuando como elo entre grupos isolados.
        Retorna lista de (vértice, label, num_comunidades_conectadas) ordenada por importância.
        """
        neighbors = self._get_neighbors()
        bridges = []

        for u in range(self.n):
            connected_communities = set()
            for v in neighbors[u]:
                if communities[v] != communities[u]:
                    connected_communities.add(communities[v])

            if connected_communities:
                bridges.append((u, self.graph.vertexLabels[u], len(connected_communities)))

        bridges.sort(key=lambda x: x[2], reverse=True)
        return bridges
