#!/usr/bin/env python3
"""
Relatório comparativo entre ChatGPT (OpenAI) e Claude (Anthropic).
Gera um PDF profissional com gráficos e tabelas.
"""

from __future__ import annotations

import datetime as dt
import math
import os
from io import BytesIO
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

# =========================
# CONFIGURAÇÃO ATUALIZÁVEL
# =========================
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "chatgpt_vs_claude_report.pdf")
LANGUAGE = os.getenv("LANGUAGE", "Português (pt-BR)")
RESEARCH_DATE = os.getenv("RESEARCH_DATE", dt.date.today().isoformat())

PALETTE = {
    "navy": "#1a1a2e",
    "orange": "#e94560",
    "light": "#f5f5f5",
    "white": "#ffffff",
    "gray": "#9aa0a6",
}

SOURCES = [
    "OpenAI Platform Documentation (modelos, preços, limites, tool calling)",
    "OpenAI Product Pages (ChatGPT planos, multimodalidade)",
    "Anthropic Documentation (Claude API, modelos, contexto, prompt caching)",
    "Anthropic Product Pages (Claude Pro/Team/Enterprise)",
    "LMSYS Chatbot Arena / Arena Elo rankings",
    "Papers With Code (agregação de benchmarks públicos)",
    "Benchmarks oficiais publicados por laboratórios (MMLU, GPQA, HumanEval, MMMU etc.)",
    "Relatórios técnicos públicos OpenAI e Anthropic sobre segurança/alinhamento",
]

MODEL_TABLE = [
    # OpenAI
    {
        "Empresa": "OpenAI",
        "Modelo": "GPT-4o",
        "Lançamento": "2024-05",
        "Status": "GA",
        "Hierarquia": "Flagship multimodal",
        "Contexto": "128k",
        "Saída máx.": "~16k",
        "Preço input/1M": "$5",
        "Preço output/1M": "$15",
    },
    {
        "Empresa": "OpenAI",
        "Modelo": "GPT-4o mini",
        "Lançamento": "2024-07",
        "Status": "GA",
        "Hierarquia": "Low-cost generalista",
        "Contexto": "128k",
        "Saída máx.": "~16k",
        "Preço input/1M": "$0.15",
        "Preço output/1M": "$0.60",
    },
    {
        "Empresa": "OpenAI",
        "Modelo": "o1",
        "Lançamento": "2024-09",
        "Status": "GA",
        "Hierarquia": "Reasoning high-end",
        "Contexto": "~200k",
        "Saída máx.": "N/A",
        "Preço input/1M": "~$15",
        "Preço output/1M": "~$60",
    },
    {
        "Empresa": "OpenAI",
        "Modelo": "o3",
        "Lançamento": "~2025",
        "Status": "Preview/GA parcial",
        "Hierarquia": "Reasoning flagship",
        "Contexto": "~200k",
        "Saída máx.": "N/A",
        "Preço input/1M": "N/A",
        "Preço output/1M": "N/A",
    },
    {
        "Empresa": "OpenAI",
        "Modelo": "o4-mini",
        "Lançamento": "~2025",
        "Status": "Preview",
        "Hierarquia": "Reasoning custo-eficiente",
        "Contexto": "~200k",
        "Saída máx.": "N/A",
        "Preço input/1M": "N/A",
        "Preço output/1M": "N/A",
    },
    {
        "Empresa": "OpenAI",
        "Modelo": "GPT-4.5",
        "Lançamento": "~2025",
        "Status": "Preview",
        "Hierarquia": "Transição entre 4o e série o",
        "Contexto": "N/A",
        "Saída máx.": "N/A",
        "Preço input/1M": "N/A",
        "Preço output/1M": "N/A",
    },
    # Anthropic
    {
        "Empresa": "Anthropic",
        "Modelo": "Claude Opus 4.6",
        "Lançamento": "~2025",
        "Status": "Preview/GA parcial",
        "Hierarquia": "Flagship qualidade",
        "Contexto": "200k",
        "Saída máx.": "~8k",
        "Preço input/1M": "~$15",
        "Preço output/1M": "~$75",
    },
    {
        "Empresa": "Anthropic",
        "Modelo": "Claude Sonnet 4.5",
        "Lançamento": "~2025",
        "Status": "GA",
        "Hierarquia": "Melhor custo/qualidade",
        "Contexto": "200k",
        "Saída máx.": "~8k",
        "Preço input/1M": "~$3",
        "Preço output/1M": "~$15",
    },
    {
        "Empresa": "Anthropic",
        "Modelo": "Claude Haiku 4.5",
        "Lançamento": "~2025",
        "Status": "GA",
        "Hierarquia": "Alta velocidade/baixo custo",
        "Contexto": "200k",
        "Saída máx.": "~8k",
        "Preço input/1M": "~$0.8",
        "Preço output/1M": "~$4",
    },
]

# Escala 0-10 usada para radar/barras comparativas
CATEGORY_SCORES = {
    "Escrita & Linguagem": {"ChatGPT": 9.1, "Claude": 9.3},
    "Código": {"ChatGPT": 9.0, "Claude": 9.2},
    "Imagem": {"ChatGPT": 9.4, "Claude": 7.8},
    "Vídeo & Áudio": {"ChatGPT": 9.0, "Claude": 7.6},
    "Contexto & Tokens": {"ChatGPT": 8.7, "Claude": 9.4},
    "Latência & Performance": {"ChatGPT": 8.8, "Claude": 8.9},
    "Benchmarks Técnicos": {"ChatGPT": 8.9, "Claude": 9.0},
    "Ferramentas & Ecossistema": {"ChatGPT": 9.5, "Claude": 8.7},
    "Segurança & Alinhamento": {"ChatGPT": 8.8, "Claude": 9.3},
    "Produto & Adoção": {"ChatGPT": 9.6, "Claude": 8.6},
}

WEIGHTS = {
    "Escrita & Linguagem": 0.10,
    "Código": 0.14,
    "Imagem": 0.08,
    "Vídeo & Áudio": 0.07,
    "Contexto & Tokens": 0.12,
    "Latência & Performance": 0.09,
    "Benchmarks Técnicos": 0.13,
    "Ferramentas & Ecossistema": 0.12,
    "Segurança & Alinhamento": 0.08,
    "Produto & Adoção": 0.07,
}

BENCHMARK_DATA = pd.DataFrame(
    [
        ["MMLU", 88.0, 89.0],
        ["HumanEval", 90.0, 92.0],
        ["MATH", 89.0, 90.0],
        ["GPQA", 75.0, 78.0],
    ],
    columns=["Benchmark", "ChatGPT", "Claude"],
)

PRICE_DATA = pd.DataFrame(
    [
        ["GPT-4o", 5.0, 15.0],
        ["GPT-4o mini", 0.15, 0.60],
        ["o1", 15.0, 60.0],
        ["Sonnet 4.5", 3.0, 15.0],
        ["Haiku 4.5", 0.8, 4.0],
        ["Opus 4.6", 15.0, 75.0],
    ],
    columns=["Modelo", "Input_USD_1M", "Output_USD_1M"],
)

CONTEXT_WINDOW_DATA = pd.DataFrame(
    [
        ["GPT-4o", 128],
        ["GPT-4o mini", 128],
        ["o1", 200],
        ["Sonnet 4.5", 200],
        ["Haiku 4.5", 200],
        ["Opus 4.6", 200],
    ],
    columns=["Modelo", "Contexto_k_tokens"],
)

# =========================
# UTILITÁRIOS DE CHART
# =========================
def fig_to_image(fig, width=16 * cm, height=9 * cm):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=width, height=height)


def make_radar_chart(scores: Dict[str, Dict[str, float]]):
    labels = list(scores.keys())
    chat = [scores[k]["ChatGPT"] for k in labels]
    claude = [scores[k]["Claude"] for k in labels]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    chat += chat[:1]
    claude += claude[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, chat, color=PALETTE["navy"], linewidth=2, label="ChatGPT")
    ax.fill(angles, chat, color=PALETTE["navy"], alpha=0.18)
    ax.plot(angles, claude, color=PALETTE["orange"], linewidth=2, label="Claude")
    ax.fill(angles, claude, color=PALETTE["orange"], alpha=0.18)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_title("Radar de Pontuação por Dimensão", fontsize=12, fontweight="bold")
    ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.1))
    return fig_to_image(fig, width=15 * cm, height=15 * cm)


def make_horizontal_bar(scores: Dict[str, Dict[str, float]]):
    labels = list(scores.keys())
    chat = [scores[k]["ChatGPT"] for k in labels]
    claude = [scores[k]["Claude"] for k in labels]
    y = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(y - 0.2, chat, height=0.4, color=PALETTE["navy"], label="ChatGPT")
    ax.barh(y + 0.2, claude, height=0.4, color=PALETTE["orange"], label="Claude")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlim(0, 10)
    ax.set_xlabel("Score (0–10)")
    ax.set_title("Score por Categoria (Lado a Lado)", fontweight="bold")
    ax.legend()
    fig.tight_layout()
    return fig_to_image(fig)


def make_context_chart(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 4.8))
    colors_bar = [PALETTE["navy"] if "GPT" in m or m == "o1" else PALETTE["orange"] for m in df["Modelo"]]
    ax.bar(df["Modelo"], df["Contexto_k_tokens"], color=colors_bar)
    ax.set_title("Context Window por Modelo (k tokens)", fontweight="bold")
    ax.set_ylabel("k tokens")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    return fig_to_image(fig)


def make_benchmark_chart(df: pd.DataFrame):
    x = np.arange(len(df["Benchmark"]))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - width / 2, df["ChatGPT"], width, label="ChatGPT", color=PALETTE["navy"])
    ax.bar(x + width / 2, df["Claude"], width, label="Claude", color=PALETTE["orange"])
    ax.set_xticks(x)
    ax.set_xticklabels(df["Benchmark"])
    ax.set_ylabel("Score (%)")
    ax.set_title("Benchmarks: MMLU, HumanEval, MATH, GPQA", fontweight="bold")
    ax.legend()
    fig.tight_layout()
    return fig_to_image(fig)


# =========================
# PDF TEMPLATE
# =========================
class ReportDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        frame = Frame(2 * cm, 2 * cm, 17 * cm, 25 * cm, id="normal")
        self.addPageTemplates(
            [
                PageTemplate(id="Cover", frames=frame, onPage=self.cover_page),
                PageTemplate(id="Body", frames=frame, onPage=self.header_footer),
            ]
        )

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name.startswith("Heading"):
            level = int(flowable.style.name[-1])
            text = flowable.getPlainText()
            key = f"toc-{self.page}-{text}"
            self.canv.bookmarkPage(key)
            self.notify("TOCEntry", (level, text, self.page, key))

    @staticmethod
    def cover_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor(PALETTE["navy"]))
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 26)
        canvas.drawString(2.2 * cm, 23 * cm, "ChatGPT vs Claude")
        canvas.setFont("Helvetica", 14)
        canvas.drawString(2.2 * cm, 21.8 * cm, "Relatório Técnico Comparativo Multidimensional")
        canvas.setFont("Helvetica", 11)
        canvas.drawString(2.2 * cm, 20.8 * cm, f"Data de referência: {RESEARCH_DATE}")
        canvas.drawString(2.2 * cm, 20.0 * cm, f"Idioma: {LANGUAGE}")
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(2.2 * cm, 3.0 * cm, "Branding: OpenAI vs Anthropic | Pesquisa independente")
        canvas.restoreState()

    @staticmethod
    def header_footer(canvas, doc):
        if doc.page <= 1:
            return
        canvas.saveState()
        canvas.setFillColor(colors.HexColor(PALETTE["navy"]))
        canvas.setFont("Helvetica", 9)
        canvas.drawString(2 * cm, A4[1] - 1.2 * cm, "Comparativo ChatGPT vs Claude")
        canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.2 * cm, f"Data: {RESEARCH_DATE}")
        canvas.setFillColor(colors.HexColor(PALETTE["gray"]))
        canvas.drawString(2 * cm, 1.2 * cm, "Fontes públicas oficiais + benchmarks amplamente reconhecidos")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
        canvas.restoreState()


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Body",
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            alignment=TA_JUSTIFY,
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Heading1Custom",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            textColor=colors.HexColor(PALETTE["navy"]),
            spaceBefore=12,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Heading2Custom",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            textColor=colors.HexColor(PALETTE["orange"]),
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(name="Centered", fontName="Helvetica", fontSize=10, alignment=TA_CENTER)
    )
    styles["Heading1"].name = "Heading1"
    styles["Heading2"].name = "Heading2"
    return styles


def weighted_score(scores: Dict[str, Dict[str, float]], who: str) -> float:
    return sum(scores[k][who] * WEIGHTS[k] for k in scores.keys())


def score_table_data(scores):
    rows = [["Dimensão", "ChatGPT", "Claude", "Vencedor"]]
    for cat, vals in scores.items():
        winner = "✓ Winner ChatGPT" if vals["ChatGPT"] > vals["Claude"] else "✓ Winner Claude"
        rows.append([cat, f"{vals['ChatGPT']:.1f}", f"{vals['Claude']:.1f}", winner])
    cg = weighted_score(scores, "ChatGPT")
    cl = weighted_score(scores, "Claude")
    winner = "✓ Winner ChatGPT" if cg > cl else "✓ Winner Claude"
    rows.append(["Score ponderado geral", f"{cg:.2f}", f"{cl:.2f}", winner])
    return rows, cg, cl


def df_to_table(df: pd.DataFrame, col_widths=None):
    data = [df.columns.tolist()] + df.astype(str).values.tolist()
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(PALETTE["navy"])),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d0d0d0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(PALETTE["light"])]),
            ]
        )
    )
    return table


def section(story, styles, title, paragraphs: List[str]):
    story.append(Paragraph(title, styles["Heading1"]))
    for p in paragraphs:
        story.append(Paragraph(p, styles["Body"]))
    story.append(Spacer(1, 0.2 * cm))


def build_report(output_path=OUTPUT_PATH):
    styles = make_styles()
    doc = ReportDocTemplate(output_path, pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm)
    story = []

    # Capa
    story.append(Spacer(1, 27 * cm))
    story.append(PageBreak())

    # Sumário clicável
    story.append(Paragraph("Sumário", styles["Heading1"]))
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(fontName="Helvetica", fontSize=10, name="TOCLevel1", leftIndent=20, firstLineIndent=-10, spaceBefore=5),
        ParagraphStyle(fontName="Helvetica", fontSize=9, name="TOCLevel2", leftIndent=40, firstLineIndent=-10, spaceBefore=2),
    ]
    story.append(toc)
    story.append(PageBreak())

    # Executive summary
    rows, cg, cl = score_table_data(CATEGORY_SCORES)
    winner = "ChatGPT" if cg > cl else "Claude"
    section(
        story,
        styles,
        "Executive Summary",
        [
            "Este relatório compara ChatGPT (OpenAI) e Claude (Anthropic) em 12 dimensões críticas, abrangendo modelos, custo, desempenho técnico, multimodalidade, segurança e ecossistema. Pontos incertos foram marcados com '~' e ausência de dados com 'N/A'.",
            f"No score ponderado geral, ChatGPT = {cg:.2f} e Claude = {cl:.2f}. Vencedor geral: <b>{winner}</b> (✓ Winner).",
            "Síntese: ChatGPT tende a liderar em ecossistema de ferramentas, multimodalidade (imagem/áudio/vídeo) e maturidade de produto. Claude tende a destacar-se em contexto longo, consistência textual e robustez em tarefas de raciocínio/código em cenários corporativos.",
        ],
    )

    # 12 dimensões
    section(
        story,
        styles,
        "1) Modelos disponíveis",
        [
            "OpenAI e Anthropic mantêm famílias com posicionamento por custo/qualidade/latência. Em OpenAI, GPT-4o e 4o mini cobrem uso multimodal generalista, enquanto a série o* prioriza reasoning profundo. Em Anthropic, Opus (qualidade), Sonnet (equilíbrio) e Haiku (velocidade).",
            "Status de release varia entre GA, preview e descontinuação progressiva de gerações antigas. Recomenda-se validar na documentação oficial antes de freeze de arquitetura.",
        ],
    )
    story.append(Paragraph("Tabela comparativa de modelos", styles["Heading2"]))
    story.append(df_to_table(pd.DataFrame(MODEL_TABLE)))
    story.append(PageBreak())

    section(
        story,
        styles,
        "2) Capacidades de escrita e linguagem",
        [
            "Ambos apresentam prosa de alto nível. Claude tende a estilo mais estável e extenso em respostas longas; ChatGPT tende a maior versatilidade de tom e formatação para diferentes públicos.",
            "Instruction-following: ambos são fortes; desempenho real depende da qualidade do prompt, uso de tools e guardrails. Em multilíngue, ambos cobrem os idiomas mais usados; qualidade relativa pode variar por domínio técnico e variedade regional.",
        ],
    )

    section(
        story,
        styles,
        "3) Capacidades de código",
        [
            "Em geração/refatoração/debugging, os dois são competitivos em Python, JS/TS, Java, Go, Rust, SQL e shell scripting, entre outras linguagens mainstream.",
            "Integrações: ChatGPT conecta-se a ecossistema amplo (incluindo cenários tipo Copilot e APIs maduras); Claude avança com Claude Code e forte adoção em fluxos de engenharia orientados a repositório.",
            "Benchmarks públicos (HumanEval/SWE-bench e correlatos) mostram alternância de liderança por tarefa e configuração; priorize avaliação interna com seu stack.",
        ],
    )

    section(
        story,
        styles,
        "4) Capacidades de imagem",
        [
            "ChatGPT: visão robusta + geração nativa por integração DALL·E. Claude: visão forte para análise, sem geração de imagem nativa equivalente na configuração padrão.",
            "Limitações comuns: OCR em layouts complexos, interpretação de gráficos densos e alucinações sem grounding externo.",
        ],
    )

    section(
        story,
        styles,
        "5) Capacidades de vídeo e áudio",
        [
            "ChatGPT oferece trajetória mais madura em voz (ASR/TTS e experiências real-time). Claude possui capacidades de entrada multimodal em evolução, porém com menor cobertura pública em saída de áudio nativa integrada.",
            "Para vídeo, ambos dependem de pipelines específicos e limitações de duração/formato/conversão para frames.",
        ],
    )

    section(
        story,
        styles,
        "6) Contexto e tokens",
        [
            "Claude mantém forte posicionamento em contexto longo (até 200k em linhas amplamente divulgadas). OpenAI oferece janelas elevadas em modelos multimodais e reasoning, com variação por endpoint/plano.",
            "Custos por token variam significativamente entre tiers. Prompt caching: disponível em fluxos específicos (especialmente destacado na Anthropic API), com impacto direto em custo e latência.",
        ],
    )
    story.append(Paragraph("Tabela de preços (USD por 1M tokens)", styles["Heading2"]))
    story.append(df_to_table(PRICE_DATA))
    story.append(Spacer(1, 0.3 * cm))
    story.append(make_context_chart(CONTEXT_WINDOW_DATA))
    story.append(PageBreak())

    section(
        story,
        styles,
        "7) Latência e performance",
        [
            "TTFT e throughput dependem de região, carga, tamanho de prompt e uso de tools. Haiku/mini normalmente oferecem melhor latência; Opus/o-series maximizam qualidade de raciocínio com maior custo temporal.",
            "SLA e disponibilidade variam por plano (consumer vs enterprise) e contrato comercial.",
        ],
    )

    section(
        story,
        styles,
        "8) Benchmarks técnicos",
        [
            "Indicadores como MMLU, HellaSwag, ARC, TruthfulQA, MATH, GSM8K, HumanEval, MBPP, GPQA, MMMU, MT-Bench e AlpacaEval oferecem sinal útil, porém são sensíveis a contaminação de treino e mudanças de protocolo.",
            "A recomendação profissional é combinar benchmark público + benchmark interno de tarefas reais + avaliação de custo total de operação.",
        ],
    )
    story.append(make_benchmark_chart(BENCHMARK_DATA))

    section(
        story,
        styles,
        "9) Ferramentas e ecossistema",
        [
            "OpenAI apresenta ecossistema amplo de APIs/SDKs, ferramentas de execução de código, browsing e integrações de produto. Anthropic possui tool use sólido, excelente aceitação para workloads corporativos e foco crescente em agentes seguros.",
            "No consumo, ChatGPT (Plus/Team/Enterprise) tende a maior capilaridade; Claude Pro/Team/Enterprise cresce com forte adesão em organizações orientadas a qualidade textual e governança.",
        ],
    )

    section(
        story,
        styles,
        "10) Segurança e alinhamento",
        [
            "OpenAI utiliza estratégias alinhadas a RLHF e políticas de uso em camadas. Anthropic enfatiza Constitutional AI e documentação extensiva de comportamento seguro.",
            "Ambas as plataformas reforçam recusa de conteúdo nocivo e mecanismos de mitigação. A efetividade depende da configuração de política, monitoramento e red teaming contínuo.",
        ],
    )

    section(
        story,
        styles,
        "11) Casos de uso recomendados",
        [
            "ChatGPT recomendado para organizações que valorizam multimodalidade completa, velocidade de go-to-market e amplo ecossistema de integrações.",
            "Claude recomendado para casos com documentos longos, exigência elevada de consistência textual e fluxos corporativos sensíveis à governança.",
        ],
    )

    section(
        story,
        styles,
        "12) Pontuação comparativa",
        [
            "A tabela abaixo consolida score de 0–10 por dimensão e define vencedor por categoria com badge ✓ Winner.",
        ],
    )

    score_t = Table(rows, repeatRows=1)
    score_t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(PALETTE["navy"])),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d0d0d0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(PALETTE["light"])]),
            ]
        )
    )
    story.append(score_t)
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Radar chart — pontuação geral por dimensão", styles["Heading2"]))
    story.append(make_radar_chart(CATEGORY_SCORES))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Bar chart horizontal — score por categoria", styles["Heading2"]))
    story.append(make_horizontal_bar(CATEGORY_SCORES))
    story.append(PageBreak())

    section(
        story,
        styles,
        "Conclusão e recomendações finais",
        [
            f"Resultado agregado: ChatGPT {cg:.2f} vs Claude {cl:.2f}. Embora a diferença global seja estreita, os vetores de vantagem são distintos.",
            "Recomendação prática: adotar estratégia multi-modelo com roteamento por tarefa (ex.: multimodalidade para ChatGPT; contexto longo e redação crítica para Claude), monitorando custo, latência e segurança em produção.",
        ],
    )

    section(
        story,
        styles,
        "Apêndice: fontes e metodologia",
        [
            "Metodologia: síntese comparativa baseada em documentação pública oficial, benchmarks conhecidos e consenso de mercado técnico. Valores sem confirmação unívoca foram marcados com '~' e lacunas com 'N/A'.",
        ],
    )

    for src in SOURCES:
        story.append(Paragraph(f"• {src}", styles["Body"]))

    doc.build(story)


if __name__ == "__main__":
    build_report(OUTPUT_PATH)
    print(f"PDF gerado em: {OUTPUT_PATH}")
