# ============================================================================
# MINERADOR DO GITHUB — Coleta dados de repositórios e constrói grafos
# ============================================================================
# Responsabilidade: Fazer requisições à API REST do GitHub e transformar
# interações (comentários, revisões, merges) em arestas ponderadas de grafos
# ============================================================================

import os
import requests
from dotenv import load_dotenv
from collections import defaultdict
from etapa2.core.adjacency_list_graph import AdjacencyListGraph

# Carrega variáveis de ambiente do arquivo .env
# Necessário para acessar GITHUB_TOKEN e GITHUB_REPOSITORY
load_dotenv()

class GithubMiner:
    # =========================================================================
    # INICIALIZAÇÃO — Configuração de autenticação e estruturas de dados
    # =========================================================================
    def __init__(self):
        # Carrega credenciais do .env
        # GITHUB_TOKEN: token de autenticação pessoal para API (ghp_xxxxx...)
        # GITHUB_REPOSITORY: repositório alvo no formato "owner/repo"
        self.token = os.getenv('GITHUB_TOKEN')
        self.repo = os.getenv('GITHUB_REPOSITORY')

        # Headers obrigatórios para requisições à API do GitHub
        # Authorization: Token para aumentar rate limit (60 req/min → 5000 req/min)
        # Accept: Especifica versão da API (v3 = REST API, não GraphQL)
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        # URL base construída dinamicamente
        # Exemplo: https://api.github.com/repos/devlikeapro/waha
        self.base_url = f'https://api.github.com/repos/{self.repo}'

        # =====================================================================
        # MAPEAMENTO DE USUÁRIOS — Converte logins (string) em IDs (int)
        # =====================================================================
        # users_set: Conjunto de todos os logins únicos encontrados
        #           Removido automaticamente duplicatas durante coleta
        #           Exemplo: {"devlikepro", "bergpinheiro", "vicentemarciot27"}
        self.users_set = set()

        # user_to_id: Dicionário login → ID sequencial (0, 1, 2, ...)
        #            Criado após coleta, no método build_graphs()
        #            Mapeamento: "devlikepro" → 0, "bergpinheiro" → 1, etc.
        self.user_to_id = {}

        # id_to_user: Dicionário ID → login (inverso de user_to_id)
        #            Necessário para exportar rótulos de vértices para Gephi
        #            Mapeamento: 0 → "devlikepro", 1 → "bergpinheiro", etc.
        self.id_to_user = {}

        # =====================================================================
        # DICIONÁRIOS DE ARESTAS — Acumulam pesos de interações
        # =====================================================================
        # defaultdict(float): Retorna 0.0 automaticamente para chaves novas
        # Estrutura: {(user1, user2): weight_acumulado, (user3, user4): weight, ...}

        # edges_g1: Comentários em issues/PRs
        #          Cada comentário adiciona +1 (depois multiplicado por 2 no integrado)
        #          Representa: "quem comenta com quem"
        self.edges_g1 = defaultdict(float)

        # edges_g2: Fechamento de issues por outros usuários
        #          Cada fechamento adiciona +1
        #          Representa: "quem fecha issues de quem"
        self.edges_g2 = defaultdict(float)

        # edges_g3: Revisões e merges de pull requests
        #          Cada revisão adiciona +1, cada merge adiciona +1
        #          Representa: "quem revisa/mergua PRs de quem"
        self.edges_g3 = defaultdict(float)

        # edges_integrated: Combinação ponderada de G1, G2, G3
        #                  Acumula com PESOS ESPECÍFICOS:
        #                  - Comentário: +2
        #                  - Abertura comentada: +3 (aresta reversa do comentário)
        #                  - Revisão: +4
        #                  - Merge: +5
        #                  Representa: "força da colaboração"
        self.edges_integrated = defaultdict(float)

    # =========================================================================
    # REQUISIÇÃO AUXILIAR — Abstrai as chamadas HTTP à API
    # =========================================================================
    def _request(self, endpoint, params=None):
        """
        Faz requisição GET à API do GitHub.

        Args:
            endpoint: Caminho relativo após /repos/owner/repo/
                      Exemplo: "issues", "pulls/123/reviews", "pulls/456"
            params: Dicionário de query parameters
                    Exemplo: {"state": "all", "per_page": 100, "page": 1}

        Returns:
            Lista de dicionários (JSON parseado) ou lista vazia se erro

        Comportamento:
            - Sucesso (200): Retorna JSON parseado
            - Erro: Printa aviso e retorna [] (fail graceful, não bloqueia)
        """
        # Constrói URL completa
        # Exemplo: base_url + "issues" = https://api.github.com/repos/devlikeapro/waha/issues
        url = f"{self.base_url}/{endpoint}"

        # Faz requisição GET com headers de autenticação
        response = requests.get(url, headers=self.headers, params=params)

        # Verifica status code
        if response.status_code == 200:
            # Sucesso: retorna JSON parseado
            return response.json()
        else:
            # Erro: aviso e retorna vazio (não quebra fluxo)
            print(f"Aviso: Erro {response.status_code} ao acessar {endpoint}.")
            return []

    # =========================================================================
    # COLETA DE DADOS — Itera issues/PRs e acumula arestas
    # =========================================================================
    def fetch_data(self, pages=2):
        """
        Coleta todas as interações do repositório via API GitHub.

        Args:
            pages: Número de páginas a coletar (100 itens/página)
                   Limite sugerido: 5 (500 items, ~25 min com rate limit)
                   Evita exceder rate limit (5000 req/hora com autenticação)

        Fluxo:
            1. Para cada página (1 a pages):
               a. GET /issues (retorna issues E pull requests, estado=all)
               b. Para cada item:
                  - Coleta COMENTÁRIOS (interação: commenter → author)
                  - Se é ISSUE: coleta quem FECHOU (closer → author)
                  - Se é PR: coleta REVISÕES (reviewer → author)
                  - Se é PR: coleta MERGES (merger → author)
                  - Acumula em edges_g1, edges_g2, edges_g3, edges_integrated

        Acumulação de pesos:
            - Múltiplos comentários: pesos somam (e.g., 3 comentários = 2+2+2=6)
            - Revisão + Merge mesma aresta: pesos somam (4+5=9)
            - Sem duplicatas de arestas: usa addEdge idempotente + setEdgeWeight
        """
        print(f"Minerando dados de {self.repo}...")

        # =====================================================================
        # LOOP DE PAGINAÇÃO — Coleta 100 itens por página
        # =====================================================================
        for page in range(1, pages + 1):
            # Nota importante: /issues retorna TANTO issues quanto PRs
            # Diferenciação: 'pull_request' in item → é PR
            items = self._request("issues", params={
                "state": "all",      # Coleta issues abertas E fechadas
                "per_page": 100,     # Máximo permitido por página
                "page": page         # Número da página (começa em 1)
            })

            # =====================================================================
            # PARA CADA ISSUE/PR — Coleta interações
            # =====================================================================
            for item in items:
                # Extrai autor (quem abriu a issue/PR)
                author = item['user']['login']
                self.users_set.add(author)

                # Diferencia issue vs PR
                # 'pull_request' key presente → é PR, senão é issue comum
                is_pr = 'pull_request' in item

                # ===================================================================
                # 1. COLETA COMENTÁRIOS — Aplicável a issues E pull requests
                # ===================================================================
                # Obtém URL de comentários do item
                # Exemplo: https://api.github.com/repos/devlikeapro/waha/issues/123/comments
                # Reduz para: "issues/123/comments" (remove base_url)
                comments_url = item['comments_url'].replace(f'https://api.github.com/repos/{self.repo}/', '')
                comments = self._request(comments_url)

                # Processa cada comentário
                for comment in comments:
                    # Extrai quem comentou
                    commenter = comment['user']['login']
                    self.users_set.add(commenter)

                    # Ignora comentários do próprio autor (sem self-loops)
                    if commenter != author:
                        # GRAFO 1: Comentário direto (contagem)
                        # Estrutura: commenter → author (1 por comentário)
                        # Significado: "quem interage com quem via comentários"
                        self.edges_g1[(commenter, author)] += 1

                        # GRAFO INTEGRADO: Comentário com peso 2
                        # Estrutura: commenter → author (+2 por comentário)
                        # Semântica: "comentário = participação leve"
                        self.edges_integrated[(commenter, author)] += 2

                        # GRAFO INTEGRADO: Abertura comentada com peso 3 (REVERSO)
                        # Estrutura: author → commenter (+3 quando comentado)
                        # APENAS se é issue (não PR)
                        # Semântica: "autor ganhou envolvimento da comunidade"
                        if not is_pr:
                            self.edges_integrated[(author, commenter)] += 3

                # ===================================================================
                # 2. COLETA FECHAMENTO DE ISSUES — APENAS issues (não PRs)
                # ===================================================================
                # Verifica:
                # - is_pr == False: não é PR
                # - item['state'] == 'closed': está fechada
                # - item.get('closed_by'): tem informação de quem fechou
                if not is_pr and item['state'] == 'closed' and item.get('closed_by'):
                    # Extrai quem fechou a issue
                    closer = item['closed_by']['login']
                    self.users_set.add(closer)

                    # Ignora self-close
                    if closer != author:
                        # GRAFO 2: Fechamento de issue (contagem)
                        # Estrutura: closer → author (1 por fechamento)
                        # Significado: "quem resolve problemas de quem"
                        self.edges_g2[(closer, author)] += 1
                        # Nota: Peso no integrado não especificado para fechamento puro

                # ===================================================================
                # 3. COLETA PULL REQUESTS — APENAS se é PR
                # ===================================================================
                if is_pr:
                    # Extrai número da PR (necessário para endpoints específicos)
                    pr_number = item['number']

                    # ============================================================
                    # 3A. REVISÕES/APROVAÇÕES — Quem revisou a PR
                    # ============================================================
                    reviews = self._request(f"pulls/{pr_number}/reviews")
                    for review in reviews:
                        # Extrai quem fez a revisão
                        reviewer = review['user']['login']
                        self.users_set.add(reviewer)

                        # Ignora self-review
                        if reviewer != author:
                            # GRAFO 3: Revisão (contagem)
                            # Estrutura: reviewer → author (1 por revisão)
                            # Significado: "quem revisa código de quem"
                            self.edges_g3[(reviewer, author)] += 1

                            # GRAFO INTEGRADO: Revisão com peso 4
                            # Semântica: "revisão = análise técnica profunda"
                            self.edges_integrated[(reviewer, author)] += 4

                    # ============================================================
                    # 3B. MERGES — Quem integrou/mergou a PR
                    # ============================================================
                    # Necessário acessar detalhes completos do PR
                    # (endpoint /issues não retorna 'merged_by')
                    pr_details = self._request(f"pulls/{pr_number}")

                    # Verifica:
                    # - pr_details: requisição bem-sucedida
                    # - .get('merged'): PR foi merged (True/False)
                    # - .get('merged_by'): tem informação de quem mergou
                    if pr_details and pr_details.get('merged') and pr_details.get('merged_by'):
                        # Extrai quem mergou
                        merger = pr_details['merged_by']['login']
                        self.users_set.add(merger)

                        # Ignora self-merge
                        if merger != author:
                            # GRAFO 3: Merge (contagem)
                            # Estrutura: merger → author (1 por merge)
                            # Significado: "quem integra código de quem"
                            self.edges_g3[(merger, author)] += 1

                            # GRAFO INTEGRADO: Merge com peso 5
                            # Semântica: "merge = responsabilidade de integração"
                            self.edges_integrated[(merger, author)] += 5

    # =========================================================================
    # CONSTRUÇÃO DE GRAFOS — Converte arestas em estruturas de dados
    # =========================================================================
    def build_graphs(self):
        """
        Transforma dados coletados em 4 grafos instanciados.

        Passos:
            1. Cria mapeamento login → ID sequencial (0 a n-1)
            2. Instancia 4 AdjacencyListGraphs com n vértices
            3. Popula cada grafo com arestas acumuladas
            4. Atualiza rótulos de vértices (logins)

        Returns:
            Tupla (g1, g2, g3, g_integrated)
            - Cada um é uma instância de AdjacencyListGraph
            - Cada um tem 481 vértices (para devlikeapro/waha)
            - Pesos já acumulados conforme coleta

        Invariante:
            Se uma aresta foi adicionada 2× na coleta, aparece 1× no grafo
            com peso = soma dos pesos das 2 adições (idempotência garantida)
        """
        # ===================================================================
        # MAPEAMENTO: string logins → IDs sequenciais
        # ===================================================================
        # Ordena logins alfabeticamente (determinístico)
        # Cria mapping bidirecional
        for i, user in enumerate(sorted(list(self.users_set))):
            self.user_to_id[user] = i           # "devlikepro" → 0
            self.id_to_user[i] = user           # 0 → "devlikepro"

        # Total de vértices = total de usuários únicos
        num_vertices = len(self.users_set)

        # Validação: não pode estar vazio
        if num_vertices == 0:
            raise ValueError("Nenhum usuário minerado. Verifique o repositório ou o token.")

        print(f"Total de usuários (vértices) identificados: {num_vertices}")

        # ===================================================================
        # INSTANCIAÇÃO — Cria 4 grafos vazios
        # ===================================================================
        # Usa AdjacencyListGraph (mais eficiente que matriz para dados esparsos)
        # 481 vértices, 0 arestas inicialmente
        g1 = AdjacencyListGraph(num_vertices)
        g2 = AdjacencyListGraph(num_vertices)
        g3 = AdjacencyListGraph(num_vertices)
        g_integrated = AdjacencyListGraph(num_vertices)

        # ===================================================================
        # RÓTULOS DE VÉRTICES — Armazena nomes reais (logins)
        # ===================================================================
        # Para cada grafo, atualiza atributo vertexLabels
        # vertexLabels[i] = login do vértice i
        # Necessário para exportar para Gephi com nomes reais
        for g in [g1, g2, g3, g_integrated]:
            g.vertexLabels = [self.id_to_user[i] for i in range(num_vertices)]

        # ===================================================================
        # FUNÇÃO AUXILIAR — Popula grafo com arestas acumuladas
        # ===================================================================
        def populate_graph(graph, edges_dict):
            """
            Adiciona arestas a um grafo.

            Args:
                graph: Instância de AdjacencyListGraph a popular
                edges_dict: Dicionário {(login1, login2): weight_acumulado}

            Lógica:
                Para cada par (u_name, v_name) com weight acumulado:
                1. Converte logins para IDs
                2. Se aresta não existe: cria com weight
                3. Se aresta existe: soma weight (caso múltiplas interações)
                   Isso garante que se G1, G2, G3 adicionam peso à mesma aresta,
                   o integrado acumula todos (0-loop idempotência)
            """
            for (u_name, v_name), weight in edges_dict.items():
                # Converte nomes para IDs
                u = self.user_to_id[u_name]
                v = self.user_to_id[v_name]

                # Lógica de adição/acumulação
                if not graph.hasEdge(u, v):
                    # Aresta nova: criar com peso
                    graph.addEdge(u, v)
                    graph.setEdgeWeight(u, v, weight)
                else:
                    # Aresta existente: somar peso (para múltiplas interações)
                    # Exemplo: reviewer comenta E revisa = ambos somam ao integrado
                    graph.setEdgeWeight(u, v, graph.getEdgeWeight(u, v) + weight)

        # ===================================================================
        # POPULAÇÃO — Preenche cada grafo
        # ===================================================================
        # G1: Comentários (contagem → será peso 2 no integrado)
        populate_graph(g1, self.edges_g1)

        # G2: Fechamentos (contagem)
        populate_graph(g2, self.edges_g2)

        # G3: Revisões/Merges (contagem → será peso 4/5 no integrado)
        populate_graph(g3, self.edges_g3)

        # G_Integrado: Combinação ponderada
        # Tem pesos acumulados (2, 3, 4, 5) conforme tipo de interação
        populate_graph(g_integrated, self.edges_integrated)

        print("Construção dos grafos concluída com sucesso!")

        # Retorna todos os 4 grafos
        return g1, g2, g3, g_integrated