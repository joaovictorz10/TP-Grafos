import pytest
from unittest.mock import patch, MagicMock
from collections import defaultdict

from etapa1.miner import GithubMiner


# ---------------------------------------------------------------------------
# Dados fictícios que simulam respostas da API do GitHub
# ---------------------------------------------------------------------------

FAKE_ISSUE = {
    "number": 1,
    "user": {"login": "alice"},
    "state": "closed",
    "closed_by": {"login": "bob"},
    "comments_url": "https://api.github.com/repos/owner/repo/issues/1/comments",
}

FAKE_PR = {
    "number": 2,
    "user": {"login": "carol"},
    "state": "closed",
    "pull_request": {},  # presença desta chave indica PR
    "comments_url": "https://api.github.com/repos/owner/repo/issues/2/comments",
}

FAKE_COMMENT_ON_ISSUE = [
    {"user": {"login": "bob"}},   # bob comenta na issue de alice
]

FAKE_COMMENT_ON_PR = [
    {"user": {"login": "dave"}},  # dave comenta no PR de carol
]

FAKE_REVIEWS = [
    {"user": {"login": "eve"}},   # eve revisa o PR de carol
]

FAKE_PR_DETAILS_MERGED = {
    "merged": True,
    "merged_by": {"login": "frank"},  # frank faz merge do PR de carol
}

FAKE_PR_DETAILS_NOT_MERGED = {
    "merged": False,
    "merged_by": None,
}


def make_miner() -> GithubMiner:
    """Instancia GithubMiner com token e repo fictícios."""
    with patch.dict("os.environ", {"GITHUB_TOKEN": "fake_token", "GITHUB_REPOSITORY": "owner/repo"}):
        return GithubMiner()


def _side_effect_factory(items, comment_map, reviews_map, pr_details_map):
    """
    Gera um side_effect para _request que devolve dados corretos
    dependendo do endpoint chamado.
    """
    def side_effect(endpoint, params=None):
        if endpoint == "issues":
            return items
        if "comments" in endpoint:
            number = int(endpoint.split("/")[-2])
            return comment_map.get(number, [])
        if endpoint.startswith("pulls/") and endpoint.endswith("/reviews"):
            number = int(endpoint.split("/")[1])
            return reviews_map.get(number, [])
        if endpoint.startswith("pulls/"):
            number = int(endpoint.split("/")[1])
            return pr_details_map.get(number, {})
        return []
    return side_effect


# ---------------------------------------------------------------------------
# Testes de fetch_data
# ---------------------------------------------------------------------------

class TestFetchData:

    def test_usuarios_extraidos_corretamente(self):
        """Mineração identifica todos os usuários presentes nas interações."""
        miner = make_miner()
        side_effect = _side_effect_factory(
            items=[FAKE_ISSUE, FAKE_PR],
            comment_map={1: FAKE_COMMENT_ON_ISSUE, 2: FAKE_COMMENT_ON_PR},
            reviews_map={2: FAKE_REVIEWS},
            pr_details_map={2: FAKE_PR_DETAILS_MERGED},
        )
        with patch.object(miner, "_request", side_effect=side_effect):
            miner.fetch_data(pages=1)

        # alice (autora issue), bob (comentou + fechou), carol (autora PR),
        # dave (comentou PR), eve (revisou), frank (merge)
        assert "alice" in miner.users_set
        assert "bob" in miner.users_set
        assert "carol" in miner.users_set
        assert "dave" in miner.users_set
        assert "eve" in miner.users_set
        assert "frank" in miner.users_set

    def test_grafo1_comentario_em_issue(self):
        """Comentário de bob na issue de alice gera aresta bob->alice no G1."""
        miner = make_miner()
        side_effect = _side_effect_factory(
            items=[FAKE_ISSUE],
            comment_map={1: FAKE_COMMENT_ON_ISSUE},
            reviews_map={},
            pr_details_map={},
        )
        with patch.object(miner, "_request", side_effect=side_effect):
            miner.fetch_data(pages=1)

        assert ("bob", "alice") in miner.edges_g1

    def test_grafo1_comentario_em_pr(self):
        """Comentário de dave no PR de carol gera aresta dave->carol no G1."""
        miner = make_miner()
        side_effect = _side_effect_factory(
            items=[FAKE_PR],
            comment_map={2: FAKE_COMMENT_ON_PR},
            reviews_map={2: []},
            pr_details_map={2: FAKE_PR_DETAILS_NOT_MERGED},
        )
        with patch.object(miner, "_request", side_effect=side_effect):
            miner.fetch_data(pages=1)

        assert ("dave", "carol") in miner.edges_g1

    def test_grafo2_fechamento_de_issue(self):
        """Bob fecha issue de alice → aresta bob->alice no G2."""
        miner = make_miner()
        side_effect = _side_effect_factory(
            items=[FAKE_ISSUE],
            comment_map={1: []},
            reviews_map={},
            pr_details_map={},
        )
        with patch.object(miner, "_request", side_effect=side_effect):
            miner.fetch_data(pages=1)

        assert ("bob", "alice") in miner.edges_g2

    def test_grafo2_nao_registra_pr(self):
        """PRs não geram arestas no G2 (fechamento só é de issues)."""
        miner = make_miner()
        side_effect = _side_effect_factory(
            items=[FAKE_PR],
            comment_map={2: []},
            reviews_map={2: []},
            pr_details_map={2: FAKE_PR_DETAILS_MERGED},
        )
        with patch.object(miner, "_request", side_effect=side_effect):
            miner.fetch_data(pages=1)

        assert len(miner.edges_g2) == 0

    def test_grafo3_revisao_pr(self):
        """Eve revisa PR de carol → aresta eve->carol no G3."""
        miner = make_miner()
        side_effect = _side_effect_factory(
            items=[FAKE_PR],
            comment_map={2: []},
            reviews_map={2: FAKE_REVIEWS},
            pr_details_map={2: FAKE_PR_DETAILS_NOT_MERGED},
        )
        with patch.object(miner, "_request", side_effect=side_effect):
            miner.fetch_data(pages=1)

        assert ("eve", "carol") in miner.edges_g3

    def test_grafo3_merge_pr(self):
        """Frank faz merge do PR de carol → aresta frank->carol no G3."""
        miner = make_miner()
        side_effect = _side_effect_factory(
            items=[FAKE_PR],
            comment_map={2: []},
            reviews_map={2: []},
            pr_details_map={2: FAKE_PR_DETAILS_MERGED},
        )
        with patch.object(miner, "_request", side_effect=side_effect):
            miner.fetch_data(pages=1)

        assert ("frank", "carol") in miner.edges_g3

    def test_sem_auto_aresta(self):
        """Usuário que comenta na própria issue não gera aresta."""
        issue_self = {
            "number": 3,
            "user": {"login": "alice"},
            "state": "open",
            "comments_url": "https://api.github.com/repos/owner/repo/issues/3/comments",
        }
        comment_self = [{"user": {"login": "alice"}}]  # alice comenta em si mesma

        miner = make_miner()
        side_effect = _side_effect_factory(
            items=[issue_self],
            comment_map={3: comment_self},
            reviews_map={},
            pr_details_map={},
        )
        with patch.object(miner, "_request", side_effect=side_effect):
            miner.fetch_data(pages=1)

        assert ("alice", "alice") not in miner.edges_g1
        assert ("alice", "alice") not in miner.edges_integrated


# ---------------------------------------------------------------------------
# Testes de pesos no grafo integrado
# ---------------------------------------------------------------------------

class TestPesosIntegrado:

    def test_peso_comentario_issue(self):
        """Comentário em issue gera peso 2 (commenter->author) no integrado."""
        miner = make_miner()
        side_effect = _side_effect_factory(
            items=[FAKE_ISSUE],
            comment_map={1: FAKE_COMMENT_ON_ISSUE},
            reviews_map={},
            pr_details_map={},
        )
        with patch.object(miner, "_request", side_effect=side_effect):
            miner.fetch_data(pages=1)

        assert miner.edges_integrated[("bob", "alice")] >= 2

    def test_peso_abertura_issue_comentada(self):
        """Abertura de issue comentada gera peso 3 (author->commenter) no integrado."""
        miner = make_miner()
        side_effect = _side_effect_factory(
            items=[FAKE_ISSUE],
            comment_map={1: FAKE_COMMENT_ON_ISSUE},
            reviews_map={},
            pr_details_map={},
        )
        with patch.object(miner, "_request", side_effect=side_effect):
            miner.fetch_data(pages=1)

        # alice (autora) -> bob (comentou): peso 3
        assert miner.edges_integrated[("alice", "bob")] >= 3

    def test_peso_revisao_pr(self):
        """Revisão de PR gera peso 4 no integrado."""
        miner = make_miner()
        side_effect = _side_effect_factory(
            items=[FAKE_PR],
            comment_map={2: []},
            reviews_map={2: FAKE_REVIEWS},
            pr_details_map={2: FAKE_PR_DETAILS_NOT_MERGED},
        )
        with patch.object(miner, "_request", side_effect=side_effect):
            miner.fetch_data(pages=1)

        assert miner.edges_integrated[("eve", "carol")] >= 4

    def test_peso_merge_pr(self):
        """Merge de PR gera peso 5 no integrado."""
        miner = make_miner()
        side_effect = _side_effect_factory(
            items=[FAKE_PR],
            comment_map={2: []},
            reviews_map={2: []},
            pr_details_map={2: FAKE_PR_DETAILS_MERGED},
        )
        with patch.object(miner, "_request", side_effect=side_effect):
            miner.fetch_data(pages=1)

        assert miner.edges_integrated[("frank", "carol")] >= 5

    def test_acumulacao_de_pesos(self):
        """Múltiplos comentários do mesmo usuário acumulam peso corretamente."""
        dois_comentarios = [
            {"user": {"login": "bob"}},
            {"user": {"login": "bob"}},
        ]
        miner = make_miner()
        side_effect = _side_effect_factory(
            items=[FAKE_ISSUE],
            comment_map={1: dois_comentarios},
            reviews_map={},
            pr_details_map={},
        )
        with patch.object(miner, "_request", side_effect=side_effect):
            miner.fetch_data(pages=1)

        # 2 comentários × peso 2 = 4
        assert miner.edges_integrated[("bob", "alice")] == pytest.approx(4.0)


# ---------------------------------------------------------------------------
# Testes de build_graphs
# ---------------------------------------------------------------------------

class TestBuildGraphs:

    def _miner_com_dados(self):
        """Retorna um miner já com fetch_data executado."""
        miner = make_miner()
        side_effect = _side_effect_factory(
            items=[FAKE_ISSUE, FAKE_PR],
            comment_map={1: FAKE_COMMENT_ON_ISSUE, 2: FAKE_COMMENT_ON_PR},
            reviews_map={2: FAKE_REVIEWS},
            pr_details_map={2: FAKE_PR_DETAILS_MERGED},
        )
        with patch.object(miner, "_request", side_effect=side_effect):
            miner.fetch_data(pages=1)
        return miner

    def test_build_retorna_quatro_grafos(self):
        """build_graphs deve retornar exatamente 4 grafos."""
        miner = self._miner_com_dados()
        result = miner.build_graphs()
        assert len(result) == 4

    def test_vertices_correspondem_a_usuarios(self):
        """Número de vértices em cada grafo é igual ao número de usuários minerados."""
        miner = self._miner_com_dados()
        num_users = len(miner.users_set)
        g1, g2, g3, g_int = miner.build_graphs()
        for g in [g1, g2, g3, g_int]:
            assert g.getVertexCount() == num_users

    def test_rotulos_sao_nomes_reais(self):
        """Os rótulos dos vértices devem ser os logins do GitHub."""
        miner = self._miner_com_dados()
        _, _, _, g_int = miner.build_graphs()
        labels = set(g_int.vertexLabels)
        assert "alice" in labels
        assert "bob" in labels
        assert "carol" in labels

    def test_grafo_integrado_tem_arestas(self):
        """O grafo integrado deve conter pelo menos uma aresta."""
        miner = self._miner_com_dados()
        _, _, _, g_int = miner.build_graphs()
        assert g_int.getEdgeCount() > 0

    def test_grafo_integrado_peso_correto(self):
        """Arestas do grafo integrado devem ter peso compatível com os pesos definidos."""
        miner = self._miner_com_dados()
        _, _, _, g_int = miner.build_graphs()

        # Verifica que todos os pesos são >= 2 (menor peso possível é 2)
        for u in range(g_int.getVertexCount()):
            for v in range(g_int.getVertexCount()):
                if g_int.hasEdge(u, v):
                    assert g_int.getEdgeWeight(u, v) >= 2.0

    def test_sem_usuarios_levanta_excecao(self):
        """build_graphs sem dados minerados deve lançar ValueError."""
        miner = make_miner()
        with pytest.raises(ValueError):
            miner.build_graphs()

    def test_grafo_simples_sem_lacos(self):
        """Nenhum grafo construído deve ter laços."""
        miner = self._miner_com_dados()
        g1, g2, g3, g_int = miner.build_graphs()
        for g in [g1, g2, g3, g_int]:
            for i in range(g.getVertexCount()):
                assert not g.hasEdge(i, i)
