#!/usr/bin/env python3
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from etapa1.miner import GithubMiner
from etapa3.graph_analytics import GraphAnalytics

SEPARATOR = "=" * 60


def section(title):
    """Imprime um cabeçalho de seção para organizar a saída do console."""
    print(f"\n{SEPARATOR}")
    print(f" {title}")
    print(SEPARATOR)


def log(message, level="INFO"):
    """Imprime uma linha de status com horário e nível (INFO/OK/ERRO)."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level:<5} {message}")


def create_results_structure(repo_name):
    """Cria a estrutura de pastas resultados/<owner>-<repo>/."""
    base_results = os.path.join(os.path.dirname(__file__), "resultados")
    os.makedirs(base_results, exist_ok=True)

    repo_folder = os.path.join(base_results, repo_name)
    os.makedirs(repo_folder, exist_ok=True)

    return repo_folder


def main():
    section("PUC Minas - Teoria de Grafos e Computabilidade")

    # ------------------------------------------------------------------
    # ETAPA 1 - Mineração e construção dos grafos
    # ------------------------------------------------------------------
    section("ETAPA 1 - Mineração de dados do GitHub")

    repo_name = os.getenv('GITHUB_REPOSITORY', 'unknown-repo')
    repo_token = os.getenv('GITHUB_TOKEN', 'not-set')

    log(f"Repositório: {repo_name}")
    if repo_token != 'not-set':
        log("Token do GitHub configurado", "OK")
    else:
        log("Token do GitHub NÃO CONFIGURADO (.env)", "ERRO")

    repo_folder = create_results_structure(repo_name)
    log(f"Resultados serão salvos em: {repo_folder}")

    miner = GithubMiner()
    try:
        log("Coletando issues, PRs, comentários e revisões (pages=5)...")
        miner.fetch_data(pages=5)

        log("Construindo grafos G1, G2, G3 e integrado...")
        g1, g2, g3, g_integrated = miner.build_graphs()
        log(
            f"{g_integrated.getVertexCount()} usuários e "
            f"{g_integrated.getEdgeCount()} interações no grafo integrado",
            "OK",
        )
    except Exception as e:
        log(f"Falha na mineração: {e}", "ERRO")
        log("Verifique o GITHUB_TOKEN no arquivo .env", "ERRO")
        import traceback
        traceback.print_exc()
        return

    # ------------------------------------------------------------------
    # ETAPA 2 - Propriedades do grafo integrado (demonstração da API)
    # ------------------------------------------------------------------
    section("ETAPA 2 - Propriedades do grafo integrado")
    print(f"  Vértices (usuários):     {g_integrated.getVertexCount()}")
    print(f"  Arestas (interações):    {g_integrated.getEdgeCount()}")
    print(f"  Grafo vazio?             {g_integrated.isEmptyGraph()}")
    print(f"  Grafo completo?          {g_integrated.isCompleteGraph()}")
    print(f"  Conectado (fracamente)?  {g_integrated.isConnected()}")

    # ------------------------------------------------------------------
    # ETAPA 3 - Métricas de redes complexas
    # ------------------------------------------------------------------
    section("ETAPA 3 - Métricas de redes complexas")
    analytics = GraphAnalytics(g_integrated)

    density = analytics.get_density()
    print(f"  Densidade da rede: {density:.6f}")

    log("Calculando PageRank...")
    pr_scores = analytics.get_pagerank()
    ranked_users = sorted(
        [(g_integrated.vertexLabels[i], score) for i, score in enumerate(pr_scores)],
        key=lambda x: x[1],
        reverse=True
    )

    print("\n  Top 5 - PageRank (influência):")
    top_5_users = []
    for i, (user, score) in enumerate(ranked_users[:5], 1):
        uid = g_integrated.vertexLabels.index(user)
        in_deg = g_integrated.getVertexInDegree(uid)
        print(f"    {i}. {user:25s} PR={score:.5f}  in-degree={in_deg}")
        top_5_users.append((user, score))

    log("Calculando Betweenness Centrality...")
    bw_scores = analytics.get_betweenness_centrality()
    ranked_bw = sorted(
        [(g_integrated.vertexLabels[i], score) for i, score in enumerate(bw_scores)],
        key=lambda x: x[1],
        reverse=True
    )
    print("\n  Top 5 - Betweenness Centrality (pontes da rede):")
    for i, (user, score) in enumerate(ranked_bw[:5], 1):
        print(f"    {i}. {user:25s} BW={score:.5f}")

    # ------------------------------------------------------------------
    # Exportação para GEPHI (grafo integrado + os 3 grafos separados)
    # ------------------------------------------------------------------
    section("Exportação para GEPHI")

    export_path = os.path.join(repo_folder, "grafo_integrado.csv")
    g_integrated.exportToGEPHI(export_path)
    log("grafo_integrado.csv (grafo consolidado e ponderado)", "OK")

    for grafo, nome_arquivo, descricao in [
        (g1, "grafo_comentarios.csv", "G1 - comentários em issues/PRs"),
        (g2, "grafo_fechamentos.csv", "G2 - fechamento de issues por outro usuário"),
        (g3, "grafo_revisoes_merges.csv", "G3 - revisões/aprovações/merges de PRs"),
    ]:
        caminho = os.path.join(repo_folder, nome_arquivo)
        grafo.exportToGEPHI(caminho)
        log(f"{nome_arquivo} ({descricao})", "OK")

    # ------------------------------------------------------------------
    # Relatório de mineração em texto
    # ------------------------------------------------------------------
    report_path = os.path.join(repo_folder, "relatorio_mineracao.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("RELATÓRIO DE MINERAÇÃO - GITHUB\n")
        f.write("="*60 + "\n\n")
        f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Repositório: {repo_name}\n")
        f.write(f"URL: https://github.com/{repo_name}\n\n")

        f.write("ESTATÍSTICAS GERAIS:\n")
        f.write("-" * 60 + "\n")
        f.write(f"Total de Usuários: {g_integrated.getVertexCount()}\n")
        f.write(f"Total de Interações: {g_integrated.getEdgeCount()}\n")
        f.write(f"Densidade da Rede: {density:.6f}\n")
        f.write(f"Grafo Conectado: {g_integrated.isConnected()}\n\n")

        f.write("TOP 5 CONTRIBUIDORES (PageRank):\n")
        f.write("-" * 60 + "\n")
        for i, (user, score) in enumerate(top_5_users, 1):
            f.write(f"{i}. {user} (Score: {score:.5f})\n")
        f.write("\n")

    log("relatorio_mineracao.txt", "OK")

    # ------------------------------------------------------------------
    # Análise detalhada da rede
    # ------------------------------------------------------------------
    section("Análise detalhada da rede")
    analyze_path = os.path.join(repo_folder, "analise_detalhada.txt")
    run_detailed_analysis(g_integrated, analyze_path)
    log("analise_detalhada.txt", "OK")

    # ------------------------------------------------------------------
    # Resumo final
    # ------------------------------------------------------------------
    section("Concluído")
    print(f"  Resultados salvos em: {repo_folder}\n")
    print("  Arquivos gerados:")
    for nome in [
        "grafo_integrado.csv",
        "grafo_comentarios.csv",
        "grafo_fechamentos.csv",
        "grafo_revisoes_merges.csv",
        "relatorio_mineracao.txt",
        "analise_detalhada.txt",
    ]:
        print(f"    - {nome}")
    print()


def run_detailed_analysis(graph, output_path):
    """Gera análise detalhada dos grafos, com progresso resumido no console."""
    analytics = GraphAnalytics(graph)
    total_steps = 10
    step = 0

    def progress(label, result):
        nonlocal step
        step += 1
        log(f"[{step:2d}/{total_steps}] {label}: {result}")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("ANÁLISE DETALHADA DA REDE\n")
        f.write("="*60 + "\n\n")

        # 1. Densidade
        f.write("1. DENSIDADE DA REDE\n")
        f.write("-" * 60 + "\n")
        density = analytics.get_density()
        f.write(f"Densidade: {density:.6f}\n")
        f.write("Interpretação: Proporção de conexões existentes em relação ao total possível.\n\n")
        progress("Densidade da rede", f"{density:.6f}")

        # 2. Graus
        f.write("2. GRAUS DOS VÉRTICES\n")
        f.write("-" * 60 + "\n")
        max_in_degree = max_out_degree = 0
        max_in_user = max_out_user = ""

        for i in range(graph.getVertexCount()):
            in_deg = graph.getVertexInDegree(i)
            out_deg = graph.getVertexOutDegree(i)
            if in_deg > max_in_degree:
                max_in_degree = in_deg
                max_in_user = graph.vertexLabels[i]
            if out_deg > max_out_degree:
                max_out_degree = out_deg
                max_out_user = graph.vertexLabels[i]

        f.write(f"Maior In-Degree:  {max_in_user} ({max_in_degree} conexões recebidas)\n")
        f.write(f"Maior Out-Degree: {max_out_user} ({max_out_degree} conexões enviadas)\n\n")
        progress("Graus", f"maior in-degree={max_in_user} ({max_in_degree}), maior out-degree={max_out_user} ({max_out_degree})")

        # 3. PageRank
        f.write("3. TOP 10 POR PAGERANK\n")
        f.write("-" * 60 + "\n")
        pr_scores = analytics.get_pagerank()
        ranked_pr = sorted(
            [(graph.vertexLabels[i], score) for i, score in enumerate(pr_scores)],
            key=lambda x: x[1], reverse=True
        )
        for i, (user, score) in enumerate(ranked_pr[:10], 1):
            f.write(f"{i:2d}. {user:30s} {score:.6f}\n")
        f.write("\n")
        progress("PageRank", f"top 1 = {ranked_pr[0][0]} ({ranked_pr[0][1]:.6f})")

        # 4. Betweenness Centrality
        f.write("4. TOP 10 POR BETWEENNESS CENTRALITY (Pontes da Rede)\n")
        f.write("-" * 60 + "\n")
        bw_scores = analytics.get_betweenness_centrality()
        ranked_bw = sorted(
            [(graph.vertexLabels[i], score) for i, score in enumerate(bw_scores)],
            key=lambda x: x[1], reverse=True
        )
        for i, (user, score) in enumerate(ranked_bw[:10], 1):
            f.write(f"{i:2d}. {user:30s} {score:.6f}\n")
        f.write("\n")
        progress("Betweenness Centrality", f"top 1 = {ranked_bw[0][0]} ({ranked_bw[0][1]:.6f})")

        # 5. Closeness Centrality
        f.write("5. TOP 10 POR CLOSENESS CENTRALITY (Proximidade)\n")
        f.write("-" * 60 + "\n")
        cl_scores = [analytics.get_closeness_centrality(u) for u in range(graph.getVertexCount())]
        ranked_cl = sorted(
            [(graph.vertexLabels[i], score) for i, score in enumerate(cl_scores)],
            key=lambda x: x[1], reverse=True
        )
        for i, (user, score) in enumerate(ranked_cl[:10], 1):
            f.write(f"{i:2d}. {user:30s} {score:.6f}\n")
        f.write("\n")
        progress("Closeness Centrality", f"top 1 = {ranked_cl[0][0]} ({ranked_cl[0][1]:.6f})")

        # 6. Clustering Coefficient
        f.write("6. COEFICIENTE DE AGLOMERAÇÃO (Clustering Coefficient)\n")
        f.write("-" * 60 + "\n")
        avg_clustering = analytics.get_average_clustering()
        cc_scores = analytics.get_clustering_coefficient()
        ranked_cc = sorted(
            [(graph.vertexLabels[i], score) for i, score in enumerate(cc_scores) if score > 0],
            key=lambda x: x[1], reverse=True
        )
        f.write(f"Coeficiente médio da rede: {avg_clustering:.6f}\n")
        f.write("Interpretação: Mede a tendência de colaboradores formarem grupos fechados (triângulos).\n")
        f.write(f"Top 10 com maior coeficiente local:\n")
        for i, (user, score) in enumerate(ranked_cc[:10], 1):
            f.write(f"{i:2d}. {user:30s} {score:.6f}\n")
        f.write("\n")
        progress("Clustering Coefficient", f"média da rede = {avg_clustering:.6f}")

        # 7. Assortatividade
        f.write("7. ASSORTATIVIDADE\n")
        f.write("-" * 60 + "\n")
        assortativity = analytics.get_assortativity()
        f.write(f"Coeficiente de assortatividade: {assortativity:.6f}\n")
        if assortativity > 0.1:
            interpretation = "Rede assortativa: colaboradores muito conectados tendem a interagir entre si."
        elif assortativity < -0.1:
            interpretation = "Rede dissortativa: colaboradores muito conectados tendem a interagir com menos conectados (hub-and-spoke)."
        else:
            interpretation = "Rede neutra: sem padrão claro de preferência de conexão por grau."
        f.write(f"Interpretação: {interpretation}\n\n")
        progress("Assortatividade", f"{assortativity:.6f}")

        # 8. Detecção de Comunidades
        f.write("8. DETECÇÃO DE COMUNIDADES (Louvain Simplificado)\n")
        f.write("-" * 60 + "\n")
        communities = analytics.get_communities_louvain()
        num_communities = len(set(communities))
        f.write(f"Número de comunidades detectadas: {num_communities}\n")
        community_sizes = {}
        for c in communities:
            community_sizes[c] = community_sizes.get(c, 0) + 1
        sorted_communities = sorted(community_sizes.items(), key=lambda x: x[1], reverse=True)
        f.write("Tamanho das 10 maiores comunidades:\n")
        for c_id, size in sorted_communities[:10]:
            f.write(f"  Comunidade {c_id:3d}: {size} membros\n")
        f.write("\n")
        progress("Comunidades (Louvain)", f"{num_communities} comunidades detectadas")

        # 9. Eigenvector Centrality
        f.write("9. EIGENVECTOR CENTRALITY (Influência via Importância)\n")
        f.write("-" * 60 + "\n")
        eig_scores = analytics.get_eigenvector_centrality()
        ranked_eig = sorted(
            [(graph.vertexLabels[i], score) for i, score in enumerate(eig_scores)],
            key=lambda x: x[1], reverse=True
        )
        f.write(f"Top 10 usuários por Eigenvector Centrality:\n")
        for i, (user, score) in enumerate(ranked_eig[:10], 1):
            f.write(f"{i:2d}. {user:30s} {score:.6f}\n")
        f.write("\n")
        progress("Eigenvector Centrality", f"top 1 = {ranked_eig[0][0]} ({ranked_eig[0][1]:.6f})")

        # 10. Bridging Ties
        f.write("10. BRIDGING TIES (Conectores entre Comunidades)\n")
        f.write("-" * 60 + "\n")
        bridges = analytics.get_bridging_ties(communities)
        f.write("Top 10 usuários que conectam mais comunidades distintas:\n")
        for idx, (v, label, num_comm) in enumerate(bridges[:10], 1):
            f.write(f"{idx:2d}. {label:30s} conecta {num_comm} comunidades\n")
        f.write("\n")
        if bridges:
            progress("Bridging Ties", f"top 1 = {bridges[0][1]} (conecta {bridges[0][2]} comunidades)")
        else:
            progress("Bridging Ties", "nenhum encontrado")


if __name__ == "__main__":
    main()
