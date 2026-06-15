import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etapa1.miner import GithubMiner
from etapa3.graph_analytics import GraphAnalytics
from etapa2.core.adjacency_matrix_graph import AdjacencyMatrixGraph
from etapa2.core.adjacency_list_graph import AdjacencyListGraph


def demo_api_completa(g_list, g_matrix):
    """Demonstra TODAS as operações obrigatórias da API em ambas as implementações."""

    print("\n" + "="*60)
    print(" DEMONSTRAÇÃO COMPLETA DA API")
    print("="*60)

    for nome, g in [("AdjacencyListGraph", g_list), ("AdjacencyMatrixGraph", g_matrix)]:
        print(f"\n--- [{nome}] ---")

        # Cria um grafo pequeno fixo para demonstração das operações estruturais
        demo = g.__class__(6)
        demo.vertexLabels = ["alice", "bob", "carol", "dave", "eve", "frank"]

        # getVertexCount / getEdgeCount
        print(f"  getVertexCount()      = {demo.getVertexCount()}")
        print(f"  getEdgeCount()        = {demo.getEdgeCount()} (grafo vazio)")

        # isEmptyGraph
        print(f"  isEmptyGraph()        = {demo.isEmptyGraph()}")

        # addEdge (idempotente)
        demo.addEdge(0, 1)  # alice -> bob
        demo.addEdge(0, 2)  # alice -> carol  (diverge de alice->bob)
        demo.addEdge(1, 2)  # bob   -> carol  (converge com alice->carol)
        demo.addEdge(2, 3)  # carol -> dave
        demo.addEdge(3, 4)  # dave  -> eve
        demo.addEdge(4, 5)  # eve   -> frank
        demo.addEdge(5, 0)  # frank -> alice  (fecha ciclo)
        demo.addEdge(0, 1)  # idempotência: não duplica aresta
        print(f"  addEdge (7 chamadas, 1 repetida) -> getEdgeCount() = {demo.getEdgeCount()} (esperado 7)")

        # hasEdge
        print(f"  hasEdge(0,1)          = {demo.hasEdge(0, 1)}  (alice->bob existe)")
        print(f"  hasEdge(1,0)          = {demo.hasEdge(1, 0)}  (bob->alice não existe)")

        # isSucessor / isPredessor
        print(f"  isSucessor(0,1)       = {demo.isSucessor(0, 1)}  (bob é sucessor de alice)")
        print(f"  isSucessor(1,0)       = {demo.isSucessor(1, 0)} (alice NÃO é sucessor de bob)")
        print(f"  isPredessor(1,0)      = {demo.isPredessor(1, 0)}  (alice é predecessor de bob)")
        print(f"  isPredessor(0,1)      = {demo.isPredessor(0, 1)} (bob NÃO é predecessor de alice)")

        # isDivergent / isConvergent
        print(f"  isDivergent(0,1,0,2)  = {demo.isDivergent(0,1,0,2)}  (alice diverge para bob e carol)")
        print(f"  isConvergent(0,2,1,2) = {demo.isConvergent(0,2,1,2)}  (alice e bob convergem para carol)")

        # isIncident
        print(f"  isIncident(0,1, x=0)  = {demo.isIncident(0,1,0)}  (alice incidente em alice->bob)")
        print(f"  isIncident(0,1, x=1)  = {demo.isIncident(0,1,1)}  (bob incidente em alice->bob)")
        print(f"  isIncident(0,1, x=2)  = {demo.isIncident(0,1,2)} (carol NÃO é incidente em alice->bob)")

        # getVertexInDegree / getVertexOutDegree
        print(f"  getVertexInDegree(2)  = {demo.getVertexInDegree(2)}  (carol: recebe de alice e bob)")
        print(f"  getVertexOutDegree(0) = {demo.getVertexOutDegree(0)}  (alice: envia para bob e carol)")

        # setVertexWeight / getVertexWeight
        demo.setVertexWeight(0, 9.5)
        print(f"  setVertexWeight(0, 9.5) -> getVertexWeight(0) = {demo.getVertexWeight(0)}")

        # setEdgeWeight / getEdgeWeight
        demo.setEdgeWeight(0, 1, 4.0)
        print(f"  setEdgeWeight(0,1,4.0) -> getEdgeWeight(0,1)  = {demo.getEdgeWeight(0, 1)}")

        # isConnected
        print(f"  isConnected()         = {demo.isConnected()}  (ciclo garante conectividade)")

        # isCompleteGraph
        print(f"  isCompleteGraph()     = {demo.isCompleteGraph()} (não tem todas as arestas)")

        # removeEdge
        demo.removeEdge(0, 1)
        print(f"  removeEdge(0,1) -> getEdgeCount() = {demo.getEdgeCount()} (era 7, agora 6)")
        print(f"  hasEdge(0,1) após removeEdge      = {demo.hasEdge(0, 1)}")


def main():
    print("="*60)
    print(" PUC Minas - Teoria de Grafos e Computabilidade")
    print("="*60)

    # 1. Mineração
    miner = GithubMiner()

    try:
        miner.fetch_data(pages=5)
        g1, g2, g3, g_integrated = miner.build_graphs()
    except Exception as e:
        print(f"\nErro durante a mineração: {e}")
        print("Verifique seu Token do GitHub no arquivo .env!")
        return

    num_vertices = g_integrated.getVertexCount()

    # 2. Constrói cópia do grafo integrado em AdjacencyMatrixGraph para demonstração
    print(f"\nConstruindo AdjacencyMatrixGraph com {num_vertices} vértices...")
    g_matrix = AdjacencyMatrixGraph(num_vertices)
    g_matrix.vertexLabels = list(g_integrated.vertexLabels)

    for u in range(num_vertices):
        for v in range(num_vertices):
            if g_integrated.hasEdge(u, v):
                g_matrix.addEdge(u, v)
                g_matrix.setEdgeWeight(u, v, g_integrated.getEdgeWeight(u, v))

    print(f"AdjacencyMatrixGraph construído: {g_matrix.getEdgeCount()} arestas.")

    # 3. Demonstração completa da API nas duas implementações
    demo_api_completa(g_integrated, g_matrix)

    # 4. Demonstração com dados reais do repositório
    print("\n" + "="*60)
    print(" ANÁLISE DO REPOSITÓRIO REAL (AdjacencyListGraph)")
    print("="*60)

    print(f"\nTotal de Vértices (Usuários): {g_integrated.getVertexCount()}")
    print(f"Total de Arestas (Interações): {g_integrated.getEdgeCount()}")
    print(f"Grafo vazio?      {g_integrated.isEmptyGraph()}")
    print(f"Grafo completo?   {g_integrated.isCompleteGraph()}")
    print(f"Conectado (fraco)? {g_integrated.isConnected()}")

    analytics = GraphAnalytics(g_integrated)

    print(f"\nDensidade da Rede: {analytics.get_density():.6f}")

    print("\n-> Top 5 por PageRank (Influência):")
    pr_scores = analytics.get_pagerank()
    ranked_pr = sorted(
        [(g_integrated.vertexLabels[i], score) for i, score in enumerate(pr_scores)],
        key=lambda x: x[1], reverse=True
    )
    for i, (user, score) in enumerate(ranked_pr[:5]):
        print(f"  {i+1}. {user} (PR: {score:.5f})")

    print("\n-> Top 5 por Betweenness Centrality (Pontes):")
    bw_scores = analytics.get_betweenness_centrality()
    ranked_bw = sorted(
        [(g_integrated.vertexLabels[i], score) for i, score in enumerate(bw_scores)],
        key=lambda x: x[1], reverse=True
    )
    for i, (user, score) in enumerate(ranked_bw[:5]):
        print(f"  {i+1}. {user} (BW: {score:.5f})")

    # 5. Exportação para GEPHI
    export_path = "grafo_integrado.csv"
    g_integrated.exportToGEPHI(export_path)
    print(f"\n[SUCESSO] Grafo exportado para GEPHI: {export_path}")


if __name__ == "__main__":
    main()
