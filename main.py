#!/usr/bin/env python3
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api_github.miner import GithubMiner
from src.analytics.graph_analytics import GraphAnalytics

# Logger simples para rastrear progresso
def log(message, level="INFO"):
    """Exibe mensagem com timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def create_results_structure(repo_name):
    """Cria estrutura de pastas: resultados/owner-repo/"""
    base_results = os.path.join(os.path.dirname(__file__), "resultados")

    # Criar pasta resultados se não existir
    os.makedirs(base_results, exist_ok=True)

    # Criar pasta com nome do repositório
    repo_folder = os.path.join(base_results, repo_name)
    os.makedirs(repo_folder, exist_ok=True)

    return repo_folder

def main():
    print("==================================================")
    print(" PUC Minas - Teoria de Grafos e Computabilidade ")
    print("==================================================")

    # 1. Mineração e Modelagem de Dados
    log("Inicializando GithubMiner...")
    miner = GithubMiner()

    # Obter nome do repositório do .env
    repo_name = os.getenv('GITHUB_REPOSITORY', 'unknown-repo')
    repo_token = os.getenv('GITHUB_TOKEN', 'not-set')

    log(f"Repositório configurado: {repo_name}")
    log(f"Token GitHub: {'*' * 10}... (configurado)" if repo_token != 'not-set' else "Token GitHub: NÃO CONFIGURADO!")

    repo_folder = create_results_structure(repo_name)
    log(f"Estrutura de pastas criada: {repo_folder}")

    try:
        log(f"Minerando repositório: {repo_name}", "START")
        log(f"Salvando resultados em: {repo_folder}")

        log("Iniciando fetch_data(pages=5)...", "FETCH")
        miner.fetch_data(pages=5)
        log("fetch_data() concluído!", "FETCH")

        log("Construindo grafos...", "BUILD")
        g1, g2, g3, g_integrated = miner.build_graphs()
        log(f"Grafos construídos com sucesso!", "BUILD")
    except Exception as e:
        log(f"ERRO durante a mineração: {e}", "ERROR")
        log("Verifique seu Token do GitHub no arquivo .env!", "ERROR")
        import traceback
        traceback.print_exc()
        return

    # 2. Consumo e Demonstração da API (Exigência do Trabalho)
    print("\n--- [ DEMONSTRAÇÃO DA API - GRAFO INTEGRADO ] ---")
    log(f"Total de Vértices (Usuários): {g_integrated.getVertexCount()}", "API")
    log(f"Total de Arestas (Interações): {g_integrated.getEdgeCount()}", "API")
    print(f"O Grafo é vazio? {g_integrated.isEmptyGraph()}")
    print(f"O Grafo é completo? {g_integrated.isCompleteGraph()}")
    print(f"A rede possui conectividade fraca? {g_integrated.isConnected()}")

    # 3. Análise com Algoritmos
    print("\n--- [ MÉTRICAS DE REDES COMPLEXAS ] ---")
    log("Calculando PageRank...", "ANALYTICS")
    analytics = GraphAnalytics(g_integrated)

    density = analytics.get_density()
    log(f"Densidade da Rede: {density:.6f}", "ANALYTICS")

    log("Calculando PageRank (isso pode levar alguns segundos)...", "ANALYTICS")
    pr_scores = analytics.get_pagerank()
    log("PageRank calculado com sucesso!", "ANALYTICS")

    ranked_users = sorted(
        [(g_integrated.vertexLabels[i], score) for i, score in enumerate(pr_scores)],
        key=lambda x: x[1],
        reverse=True
    )

    print("\n-> Top 5 Contribuidores por PageRank (Influência):")
    top_5_users = []
    for i, (user, score) in enumerate(ranked_users[:5]):
        uid = g_integrated.vertexLabels.index(user)
        in_deg = g_integrated.getVertexInDegree(uid)
        print(f"  {i+1}º - {user} (PR: {score:.5f}, In-Degree: {in_deg})")
        top_5_users.append((user, score))

    log("Calculando Betweenness Centrality...", "ANALYTICS")
    bw_scores = analytics.get_betweenness_centrality()
    ranked_bw = sorted(
        [(g_integrated.vertexLabels[i], score) for i, score in enumerate(bw_scores)],
        key=lambda x: x[1],
        reverse=True
    )
    print("\n-> Top 5 por Betweenness Centrality (Pontes da Rede):")
    for i, (user, score) in enumerate(ranked_bw[:5]):
        print(f"  {i+1}º - {user} (BW: {score:.5f})")

    # 4. Exportação para GEPHI (os 4 grafos: integrado + os 3 separados)
    log("Exportando grafos para GEPHI...", "EXPORT")
    export_path = os.path.join(repo_folder, "grafo_integrado.csv")
    g_integrated.exportToGEPHI(export_path)
    log(f"Grafo integrado exportado em: {export_path}", "EXPORT")

    # Grafos separados, um por tipo de relação (Etapa 1 do enunciado)
    for grafo, nome_arquivo, descricao in [
        (g1, "grafo_comentarios.csv", "G1 - comentários em issues/PRs"),
        (g2, "grafo_fechamentos.csv", "G2 - fechamento de issues por outro usuário"),
        (g3, "grafo_revisoes_merges.csv", "G3 - revisões/aprovações/merges de PRs"),
    ]:
        caminho = os.path.join(repo_folder, nome_arquivo)
        grafo.exportToGEPHI(caminho)
        log(f"{descricao} exportado em: {caminho}", "EXPORT")

    # 5. Gerar relatório em texto
    log("Gerando relatório de mineração...", "REPORT")
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

    log(f"Relatório salvo em: {report_path}", "REPORT")

    # 6. Executar análise detalhada
    log("Gerando análise detalhada...", "ANALYSIS")
    analyze_path = os.path.join(repo_folder, "analise_detalhada.txt")
    run_detailed_analysis(g_integrated, analyze_path)
    log(f"Análise detalhada salva em: {analyze_path}", "ANALYSIS")

    # 7. Informações finais
    print("\n" + "="*60)
    print(f"RESULTADOS SALVOS EM: {repo_folder}")
    print("="*60)
    log("EXECUÇÃO CONCLUÍDA COM SUCESSO!", "SUCCESS")
    print("\nArquivos gerados:")
    print(f"  • grafo_integrado.csv (para GEPHI)")
    print(f"  • grafo_comentarios.csv (G1, para GEPHI)")
    print(f"  • grafo_fechamentos.csv (G2, para GEPHI)")
    print(f"  • grafo_revisoes_merges.csv (G3, para GEPHI)")
    print(f"  • relatorio_mineracao.txt")
    print(f"  • analise_detalhada.txt")

def run_detailed_analysis(graph, output_path):
    """Gera análise detalhada dos grafos"""
    analytics = GraphAnalytics(graph)

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
        log(f"Densidade: {density:.6f}", "DETAIL")

        # 2. Graus
        f.write("2. GRAUS DOS VÉRTICES\n")
        f.write("-" * 60 + "\n")
        log(f"Analisando graus...", "DETAIL")
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

        # 3. PageRank
        f.write("3. TOP 10 POR PAGERANK\n")
        f.write("-" * 60 + "\n")
        log("Calculando PageRank...", "DETAIL")
        pr_scores = analytics.get_pagerank()
        ranked_pr = sorted(
            [(graph.vertexLabels[i], score) for i, score in enumerate(pr_scores)],
            key=lambda x: x[1], reverse=True
        )
        for i, (user, score) in enumerate(ranked_pr[:10], 1):
            f.write(f"{i:2d}. {user:30s} {score:.6f}\n")
        f.write("\n")
        log("PageRank concluído!", "DETAIL")

        # 4. Betweenness Centrality
        f.write("4. TOP 10 POR BETWEENNESS CENTRALITY (Pontes da Rede)\n")
        f.write("-" * 60 + "\n")
        log("Calculando Betweenness Centrality...", "DETAIL")
        bw_scores = analytics.get_betweenness_centrality()
        ranked_bw = sorted(
            [(graph.vertexLabels[i], score) for i, score in enumerate(bw_scores)],
            key=lambda x: x[1], reverse=True
        )
        for i, (user, score) in enumerate(ranked_bw[:10], 1):
            f.write(f"{i:2d}. {user:30s} {score:.6f}\n")
        f.write("\n")
        log("Betweenness concluído!", "DETAIL")

        # 5. Closeness Centrality
        f.write("5. TOP 10 POR CLOSENESS CENTRALITY (Proximidade)\n")
        f.write("-" * 60 + "\n")
        log("Calculando Closeness Centrality...", "DETAIL")
        cl_scores = [analytics.get_closeness_centrality(u) for u in range(graph.getVertexCount())]
        ranked_cl = sorted(
            [(graph.vertexLabels[i], score) for i, score in enumerate(cl_scores)],
            key=lambda x: x[1], reverse=True
        )
        for i, (user, score) in enumerate(ranked_cl[:10], 1):
            f.write(f"{i:2d}. {user:30s} {score:.6f}\n")
        f.write("\n")
        log("Closeness concluído!", "DETAIL")

        # 6. Clustering Coefficient
        f.write("6. COEFICIENTE DE AGLOMERAÇÃO (Clustering Coefficient)\n")
        f.write("-" * 60 + "\n")
        log("Calculando Clustering Coefficient...", "DETAIL")
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
        log(f"Clustering médio: {avg_clustering:.6f}", "DETAIL")

        # 7. Assortatividade
        f.write("7. ASSORTATIVIDADE\n")
        f.write("-" * 60 + "\n")
        log("Calculando Assortatividade...", "DETAIL")
        assortativity = analytics.get_assortativity()
        f.write(f"Coeficiente de assortatividade: {assortativity:.6f}\n")
        if assortativity > 0.1:
            interpretation = "Rede assortativa: colaboradores muito conectados tendem a interagir entre si."
        elif assortativity < -0.1:
            interpretation = "Rede dissortativa: colaboradores muito conectados tendem a interagir com menos conectados (hub-and-spoke)."
        else:
            interpretation = "Rede neutra: sem padrão claro de preferência de conexão por grau."
        f.write(f"Interpretação: {interpretation}\n\n")
        log(f"Assortatividade: {assortativity:.6f}", "DETAIL")

        # 8. Detecção de Comunidades
        f.write("8. DETECÇÃO DE COMUNIDADES (Louvain Simplificado)\n")
        f.write("-" * 60 + "\n")
        log("Detectando comunidades...", "DETAIL")
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
        log(f"Comunidades detectadas: {num_communities}", "DETAIL")

        # 9. Eigenvector Centrality
        f.write("9. EIGENVECTOR CENTRALITY (Influência via Importância)\n")
        f.write("-" * 60 + "\n")
        log("Calculando Eigenvector Centrality...", "DETAIL")
        eig_scores = analytics.get_eigenvector_centrality()
        ranked_eig = sorted(
            [(graph.vertexLabels[i], score) for i, score in enumerate(eig_scores)],
            key=lambda x: x[1], reverse=True
        )
        f.write(f"Top 10 usuários por Eigenvector Centrality:\n")
        for i, (user, score) in enumerate(ranked_eig[:10], 1):
            f.write(f"{i:2d}. {user:30s} {score:.6f}\n")
        f.write("\n")
        log("Eigenvector concluído!", "DETAIL")

        # 10. Bridging Ties
        f.write("10. BRIDGING TIES (Conectores entre Comunidades)\n")
        f.write("-" * 60 + "\n")
        log("Identificando bridging ties...", "DETAIL")
        bridges = analytics.get_bridging_ties(communities)
        f.write("Top 10 usuários que conectam mais comunidades distintas:\n")
        for idx, (v, label, num_comm) in enumerate(bridges[:10], 1):
            f.write(f"{idx:2d}. {label:30s} conecta {num_comm} comunidades\n")
        f.write("\n")
        log("Bridging ties concluído!", "DETAIL")

        log("Análise detalhada concluída!", "DETAIL")

if __name__ == "__main__":
    main()
