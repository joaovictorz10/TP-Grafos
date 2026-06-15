# TP-Grafos — Análise da Rede de Colaboração em Repositórios do GitHub

Trabalho prático da disciplina **Teoria de Grafos e Computabilidade** — PUC Minas,
Curso de Engenharia de Software (Prof. Leonardo V. Cardoso, 2026/1).

Ferramenta que minera as interações entre colaboradores de um repositório público do
GitHub, modela essas interações como grafos direcionados ponderados e aplica métricas
de redes complexas (centralidades, densidade, clustering, comunidades etc.) para
analisar a colaboração do projeto.

## Equipe

- Davi Nunes Carvalho
- Luiz Fernando Batista Moreira
- Josué Carlos Goulart dos Reis
- João Victor Russo Marquito

## Repositório analisado

[`devlikeapro/waha`](https://github.com/devlikeapro/waha) (WAHA — WhatsApp HTTP API),
escolhido por ter mais de 5.000 estrelas e um volume significativo de issues, pull
requests, revisões e comentários, garantindo uma rede de colaboração rica para análise.

## Visão geral do projeto

O trabalho está organizado em **3 etapas**, cada uma em sua própria pasta, com código,
testes e README específicos:

| Etapa | Pasta | Conteúdo |
| --- | --- | --- |
| **Etapa 1** — Modelagem e mineração de dados | [`etapa1/`](etapa1/) | `GithubMiner`: coleta dados via API REST do GitHub e constrói os grafos G1, G2, G3 e o grafo integrado ponderado |
| **Etapa 2** — Estrutura de grafos (API) | [`etapa2/`](etapa2/) | `AbstractGraph`, `AdjacencyMatrixGraph`, `AdjacencyListGraph` e a aplicação de demonstração `demo_api.py` |
| **Etapa 3** — Análise do repositório | [`etapa3/`](etapa3/) | `GraphAnalytics`: centralidades, densidade, clustering, assortatividade, comunidades e bridging ties |

O `main.py`, na raiz do projeto, é o **orquestrador final**: executa a mineração
(Etapa 1), monta o grafo integrado (Etapa 2) e roda todas as métricas (Etapa 3),
exportando os resultados para `resultados/<owner>-<repo>/`.

## Estrutura do projeto

```text
TP-Grafos/
├── main.py                  # pipeline completo (mineração + métricas + relatórios)
├── requirements.txt
├── .env                      # GITHUB_TOKEN e GITHUB_REPOSITORY (não versionar o token real)
├── etapa1/                   # Etapa 1 — mineração
│   ├── miner.py
│   ├── tests/test_miner.py
│   └── README.md
├── etapa2/                   # Etapa 2 — API de grafos
│   ├── core/
│   │   ├── abstract_graph.py
│   │   ├── adjacency_matrix_graph.py
│   │   └── adjacency_list_graph.py
│   ├── demo_api.py
│   ├── tests/test_core.py
│   └── README.md
├── etapa3/                   # Etapa 3 — análise de redes complexas
│   ├── graph_analytics.py
│   ├── tests/test_analytics.py
│   └── README.md
├── diagramas/                # Diagramas UML (PlantUML)
├── relatorio/                # Relatório técnico em LaTeX (template SBC)
├── resultados/               # Saída gerada por main.py (CSVs para o Gephi + relatórios .txt)
└── ROTEIRO_VIDEO.md          # Roteiro para a apresentação em vídeo
```

## Diagramas

Os diagramas UML (fontes `.puml` em [`diagramas/`](diagramas/), renderizados como `.png`
em [`relatorio/relatorio tex/modelagem/`](<relatorio/relatorio tex/modelagem/>)) descrevem
a arquitetura do sistema:

### Diagrama de classes

Estrutura `AbstractGraph` → `AdjacencyListGraph` / `AdjacencyMatrixGraph`, e os módulos
`GithubMiner` (Etapa 1) e `GraphAnalytics` (Etapa 3).

![Diagrama de classes](<relatorio/relatorio tex/modelagem/Diagrama_de_classes.png>)

### Diagrama de componentes

Arquitetura modular: aplicação principal, minerador, armazenamento de grafos, motor de
análise e módulo de exportação.

![Diagrama de componentes](<relatorio/relatorio tex/modelagem/diagrama_componentes.png>)

### Diagrama de sequência — mineração

Fluxo de chamadas entre `main.py`, `GithubMiner` e a API REST do GitHub durante
`fetch_data` / `build_graphs`.

![Diagrama de sequência - mineração](<relatorio/relatorio tex/modelagem/diagrama_sequencia_mineracao.png>)

### Diagramas de atividades

Fluxo de coleta de dados (`diagrama_atividades_fetch.puml`) e fluxo de cálculo das
métricas (`diagrama_atividades_analytics.puml`).

![Diagrama de atividades - mineração](<relatorio/relatorio tex/modelagem/diagrama_atividades_fetch.png>)
![Diagrama de atividades - análise](<relatorio/relatorio tex/modelagem/diagrama_atividades_analytics.png>)

> Os diagramas de estado (`diagrama_estados_grafo.puml` e `diagrama_estados_miner.puml`)
> estão disponíveis apenas como fonte `.puml` em `diagramas/` e podem ser renderizados em
> [plantuml.com](https://www.plantuml.com/plantuml/uml/) ou em uma extensão PlantUML da IDE.

## Como executar

### 1. Pré-requisitos

- Python 3.10+
- Dependências:

```bash
pip install -r requirements.txt
```

### 2. Configurar o `.env`

Crie/edite o arquivo `.env` na raiz do projeto:

```bash
GITHUB_TOKEN=seu_token_pessoal_do_github
GITHUB_REPOSITORY=devlikeapro/waha
```

O token precisa apenas de permissão de leitura pública (escopo `public_repo` ou
nenhum escopo, para repositórios públicos) — usado para aumentar o limite de
requisições à API do GitHub.

### 3. Rodar os testes (não precisa de token nem internet)

```bash
python -m pytest -v
```

São **85 testes** no total, divididos por etapa:

```bash
python -m pytest etapa1/tests -v   # mineração (com mocks da API)
python -m pytest etapa2/tests -v   # estrutura de grafos
python -m pytest etapa3/tests -v   # métricas de redes complexas
```

### 4. Rodar a aplicação de demonstração da API (Etapa 2)

```bash
python etapa2/demo_api.py
```

Demonstra **todas** as operações obrigatórias da API em `AdjacencyListGraph` e
`AdjacencyMatrixGraph`, e em seguida minera o repositório configurado no `.env` para
mostrar a API aplicada a dados reais.

### 5. Rodar o pipeline completo (Etapas 1, 2 e 3)

```bash
python main.py
```

Minera o repositório, constrói os 4 grafos, calcula todas as métricas e grava em
`resultados/<owner>-<repo>/`:

- `grafo_integrado.csv`, `grafo_comentarios.csv`, `grafo_fechamentos.csv`,
  `grafo_revisoes_merges.csv` — para importar no [Gephi](https://gephi.org/);
- `relatorio_mineracao.txt` — estatísticas gerais e top 5 por PageRank;
- `analise_detalhada.txt` — todas as métricas da Etapa 3 (top 10 por métrica).

## Resultados obtidos (devlikeapro/waha)

| Métrica | Valor |
| --- | --- |
| Usuários (vértices) | 481 |
| Interações (arestas, grafo integrado) | 1409 |
| Densidade da rede | 0,006103 |
| Grafo fracamente conectado | Não |
| Clustering médio | 0,148564 |
| Assortatividade | -0,249 (dissortativo) |
| Comunidades detectadas (Louvain) | 135 |

**Top 5 por PageRank**: `devlikepro` (mantenedor principal), `bergpinheiro`
(co-mantenedor), `vicentemarciot27`, `OrionZap`, `github-actions[bot]`.

## Relatório técnico

O relatório completo (LaTeX, template SBC) está em
[`relatorio/relatorio tex/relatorio.tex`](<relatorio/relatorio tex/relatorio.tex>),
contendo: justificativa da escolha do repositório, modelagem formal dos grafos,
esquema de pesos, diagramas, definição matemática de cada métrica e discussão dos
resultados.

## Apresentação em vídeo

O roteiro de fala para o vídeo de demonstração (até 2 minutos) está em
[`ROTEIRO_VIDEO.md`](ROTEIRO_VIDEO.md).
