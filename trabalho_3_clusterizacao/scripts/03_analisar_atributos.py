#!/usr/bin/env python3
"""Executa a análise exploratória dos atributos candidatos da Etapa 3.

O script calcula estatísticas descritivas na amostra oficial de 10.000 registros,
gera histogramas e boxplots e registra uma proposta inicial de atributos e pesos.
Não cria base ponderada e não calcula Hopkins.
"""

from __future__ import annotations

import argparse
import atexit
import math
import os
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TRABALHO_3_DIR = SCRIPT_DIR.parent
_MATPLOTLIB_CONFIG_DIR = TRABALHO_3_DIR / ".matplotlib_cache"
_MATPLOTLIB_CONFIG_DIR.mkdir(exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(_MATPLOTLIB_CONFIG_DIR)
atexit.register(shutil.rmtree, _MATPLOTLIB_CONFIG_DIR, ignore_errors=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
import seaborn as sns


SEP = ";"
ROW_ID = "ROW_ID_AMOSTRA"
PROTECTED_COLUMNS = {"SK_ID_CURR", "TARGET", ROW_ID}

REPOSITORY_ROOT = TRABALHO_3_DIR.parent
DEFAULT_INPUT = TRABALHO_3_DIR / "data" / "amostras" / "base_amostra_10000_analise.csv"
DEFAULT_DICTIONARY = (
    REPOSITORY_ROOT
    / "trabalho_1_preprocessamento"
    / "data"
    / "dicionario_codificacao_categorias.csv"
)
DEFAULT_RESULTS_DIR = TRABALHO_3_DIR / "resultados" / "exploracao"
DEFAULT_IMAGES_DIR = TRABALHO_3_DIR / "relatorio" / "imagens" / "exploracao"

CANDIDATES = [
    "AMT_CREDIT",
    "AMT_INCOME_TOTAL",
    "CNT_CHILDREN",
    "FLAG_OWN_CAR_COD",
    "AGE_YEARS",
    "CREDIT_INCOME_RATIO",
    "REGION_RATING_CLIENT",
    "SER_CREDITOS_ATIVOS",
    "SER_DIVIDA_ATRASADA",
    "NAME_FAMILY_STATUS_COD",
]

ATTRIBUTE_INFO = {
    "AMT_CREDIT": {
        "semantic_type": "numérico contínuo",
        "p1_type": "Numérico",
        "business": "Valor do crédito contratado; representa o porte da operação.",
        "caution": "Pode apresentar cauda à direita e valores elevados.",
    },
    "AMT_INCOME_TOTAL": {
        "semantic_type": "numérico contínuo",
        "p1_type": "Numérico",
        "business": "Capacidade financeira declarada do cliente.",
        "caution": "Possui outliers extremos; Min-Max pode comprimir a maioria dos registros.",
    },
    "CNT_CHILDREN": {
        "semantic_type": "numérico discreto",
        "p1_type": "Numérico",
        "business": "Composição familiar e possíveis necessidades de mobilidade.",
        "caution": "Muitos zeros e poucos valores altos; é uma contagem, não uma categoria nominal.",
    },
    "FLAG_OWN_CAR_COD": {
        "semantic_type": "nominal binário",
        "p1_type": "Nominal",
        "business": "Distingue clientes com e sem carro, diretamente útil para segmentação comercial.",
        "caution": "O código 0/1 deve ser declarado nominal ou recuperado como N/Y.",
    },
    "AGE_YEARS": {
        "semantic_type": "numérico contínuo",
        "p1_type": "Numérico",
        "business": "Representa o estágio de vida do cliente.",
        "caution": "Baixo risco metodológico, desde que normalizado.",
    },
    "CREDIT_INCOME_RATIO": {
        "semantic_type": "numérico contínuo",
        "p1_type": "Numérico",
        "business": "Expressa o crédito em relação à renda e facilita interpretar comprometimento financeiro.",
        "caution": "É derivado de crédito e renda; peso excessivo pode duplicar a dimensão financeira.",
    },
    "REGION_RATING_CLIENT": {
        "semantic_type": "ordinal",
        "p1_type": "Ordinal",
        "business": "Resume a classificação regional do cliente em três níveis ordenados.",
        "caution": "Baixa cardinalidade e forte concentração; a ordem precisa ser preservada.",
    },
    "SER_CREDITOS_ATIVOS": {
        "semantic_type": "numérico discreto",
        "p1_type": "Numérico",
        "business": "Quantidade de créditos ativos no histórico externo.",
        "caution": "Contagem assimétrica com concentração em valores baixos.",
    },
    "SER_DIVIDA_ATRASADA": {
        "semantic_type": "numérico contínuo",
        "p1_type": "Numérico",
        "business": "Valor de dívida atrasada observado no histórico externo.",
        "caution": "Extremamente esparso e com outliers severos; pode separar apenas poucos casos extremos.",
    },
    "NAME_FAMILY_STATUS_COD": {
        "semantic_type": "nominal codificado",
        "p1_type": "Nominal",
        "business": "Representa o estado civil e pode complementar o perfil familiar.",
        "caution": "Os códigos 0 a 5 não possuem distância ou ordem natural e precisam voltar a rótulos nominais.",
    },
}

PROPOSAL = [
    ("AMT_CREDIT", "principal", 6, "Captura o porte do empréstimo e diferencia necessidades de crédito."),
    ("CNT_CHILDREN", "principal", 4, "Acrescenta composição familiar e potencial necessidade de mobilidade."),
    ("FLAG_OWN_CAR_COD", "principal", 1, "Separa diretamente clientes com e sem veículo; no p1 original, peso nominal funciona apenas como inclusão."),
    ("AGE_YEARS", "principal", 5, "Distingue estágios de vida com boa interpretação comercial."),
    ("CREDIT_INCOME_RATIO", "principal", 7, "Resume comprometimento financeiro, com peso controlado por ser variável derivada."),
    ("SER_CREDITOS_ATIVOS", "principal", 5, "Adiciona intensidade do relacionamento de crédito externo sem o outlier extremo observado na renda."),
    ("AMT_INCOME_TOTAL", "alternativo", 4, "É relevante para o perfil comercial, mas o máximo de 117 milhões comprime a escala Min-Max; permanece disponível para caracterização posterior."),
    ("REGION_RATING_CLIENT", "alternativo", 3, "Pode introduzir contexto regional, mas tem somente três níveis."),
    ("SER_DIVIDA_ATRASADA", "alternativo", 2, "Possível indicador de comportamento, limitado pela forte concentração em zero."),
    ("NAME_FAMILY_STATUS_COD", "alternativo", 1, "Pode enriquecer o perfil familiar após recuperação dos rótulos; no p1 original, peso nominal não reescala o campo."),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analisa os atributos candidatos da Etapa 3.")
    parser.add_argument("--entrada", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--dicionario", type=Path, default=DEFAULT_DICTIONARY)
    parser.add_argument("--resultados-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--imagens-dir", type=Path, default=DEFAULT_IMAGES_DIR)
    parser.add_argument(
        "--sobrescrever",
        action="store_true",
        help="Permite substituir as saídas da Etapa 3.",
    )
    return parser.parse_args()


def safe_number(value: object) -> float | int | str:
    if pd.isna(value):
        return ""
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value)
    return str(value)


def load_code_labels(dictionary_path: Path) -> dict[str, dict[int, str]]:
    if not dictionary_path.is_file():
        raise FileNotFoundError(f"Dicionário de categorias não encontrado: {dictionary_path}")
    dictionary = pd.read_csv(dictionary_path, sep=SEP)
    mappings: dict[str, dict[int, str]] = {}
    source_to_candidate = {
        "FLAG_OWN_CAR": "FLAG_OWN_CAR_COD",
        "NAME_FAMILY_STATUS": "NAME_FAMILY_STATUS_COD",
    }
    for source_name, candidate_name in source_to_candidate.items():
        subset = dictionary[dictionary["CAMPO_ORIGINAL"] == source_name]
        mappings[candidate_name] = {
            int(row.CODIGO): str(row.CATEGORIA) for row in subset.itertuples(index=False)
        }
    return mappings


def calculate_statistics(df: pd.DataFrame, labels: dict[str, dict[int, str]]) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    percentiles = df[CANDIDATES].quantile([0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95])

    for attribute in CANDIDATES:
        series = pd.to_numeric(df[attribute], errors="coerce")
        non_null = series.dropna()
        modes = non_null.mode()
        mode = modes.iloc[0] if not modes.empty else np.nan
        mode_frequency = int((non_null == mode).sum()) if not modes.empty else 0
        q1 = float(percentiles.at[0.25, attribute])
        q3 = float(percentiles.at[0.75, attribute])
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outlier_mask = (series < lower) | (series > upper)
        semantic = ATTRIBUTE_INFO[attribute]["semantic_type"]
        iqr_applicable = semantic not in {"nominal binário", "nominal codificado", "ordinal"}
        label = ""
        if attribute in labels and not pd.isna(mode):
            label = labels[attribute].get(int(mode), "")

        records.append(
            {
                "atributo": attribute,
                "tipo_pandas": str(df[attribute].dtype),
                "tipo_semantico": semantic,
                "tipo_p1_sugerido": ATTRIBUTE_INFO[attribute]["p1_type"],
                "quantidade": int(len(series)),
                "quantidade_validos": int(non_null.size),
                "minimo": safe_number(non_null.min()),
                "maximo": safe_number(non_null.max()),
                "media": safe_number(non_null.mean()),
                "mediana": safe_number(non_null.median()),
                "moda": safe_number(mode),
                "rotulo_moda": label,
                "frequencia_moda": mode_frequency,
                "desvio_padrao": safe_number(non_null.std(ddof=1)),
                "variancia": safe_number(non_null.var(ddof=1)),
                "percentil_05": safe_number(percentiles.at[0.05, attribute]),
                "percentil_10": safe_number(percentiles.at[0.10, attribute]),
                "quartil_25": q1,
                "percentil_50": safe_number(percentiles.at[0.50, attribute]),
                "quartil_75": q3,
                "percentil_90": safe_number(percentiles.at[0.90, attribute]),
                "percentil_95": safe_number(percentiles.at[0.95, attribute]),
                "valores_unicos": int(non_null.nunique()),
                "ausentes": int(series.isna().sum()),
                "percentual_ausentes": float(series.isna().mean() * 100),
                "zeros": int((series == 0).sum()),
                "percentual_zeros": float((series == 0).mean() * 100),
                "iqr": iqr,
                "limite_inferior_iqr": lower,
                "limite_superior_iqr": upper,
                "possiveis_outliers_iqr": int(outlier_mask.sum()),
                "percentual_outliers_iqr": float(outlier_mask.mean() * 100),
                "criterio_iqr_aplicavel_semanticamente": iqr_applicable,
                "assimetria": safe_number(non_null.skew()),
            }
        )
    return pd.DataFrame(records)


def create_plots(df: pd.DataFrame, images_dir: Path) -> list[Path]:
    sns.set_theme(style="whitegrid", context="notebook")
    created: list[Path] = []
    for attribute in CANDIDATES:
        series = pd.to_numeric(df[attribute], errors="coerce").dropna()
        unique_count = series.nunique()
        is_discrete = unique_count <= 32

        fig, ax = plt.subplots(figsize=(9, 5.2))
        if is_discrete:
            minimum = int(math.floor(series.min()))
            maximum = int(math.ceil(series.max()))
            bins = np.arange(minimum - 0.5, maximum + 1.5, 1)
            sns.histplot(series, bins=bins, color="#276FBF", edgecolor="white", ax=ax)
            if maximum - minimum <= 20:
                ax.set_xticks(range(minimum, maximum + 1))
        else:
            upper_display = float(series.quantile(0.99)) if abs(series.skew()) > 2 else float(series.max())
            displayed = series[series <= upper_display]
            sns.histplot(displayed, bins=35, color="#276FBF", edgecolor="white", ax=ax)
            omitted = int((series > upper_display).sum())
            if omitted:
                ax.text(
                    0.99,
                    0.96,
                    f"Eixo limitado ao P99; {omitted} valores acima do limite",
                    transform=ax.transAxes,
                    ha="right",
                    va="top",
                    fontsize=9,
                    bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.85},
                )
        ax.set_title(f"Histograma — {attribute}")
        if attribute in {"AMT_CREDIT", "AMT_INCOME_TOTAL", "SER_DIVIDA_ATRASADA"}:
            money_formatter = FuncFormatter(
                lambda value, _: f"R$ {value / 1_000_000:.1f} mi".replace(".", ",")
            )
            ax.xaxis.set_major_formatter(money_formatter)
            ax.set_xlabel(f"{attribute} (milhões de reais)")
        else:
            ax.set_xlabel(attribute)
        ax.set_ylabel("Quantidade de clientes")
        fig.tight_layout()
        histogram_path = images_dir / f"{attribute.lower()}_histograma.png"
        fig.savefig(histogram_path, dpi=180, bbox_inches="tight")
        plt.close(fig)
        created.append(histogram_path)

        fig, ax = plt.subplots(figsize=(9, 3.8))
        sns.boxplot(x=series, color="#F28E2B", width=0.45, ax=ax)
        if abs(series.skew()) > 2 and series.min() >= 0:
            ax.set_xscale("symlog", linthresh=max(float(series.quantile(0.25)), 1.0))
            ax.set_xlim(left=0)
            scale_note = " (escala symlog para preservar zeros e outliers)"
        else:
            scale_note = ""
        ax.set_title(f"Boxplot — {attribute}{scale_note}")
        if attribute in {"AMT_CREDIT", "AMT_INCOME_TOTAL", "SER_DIVIDA_ATRASADA"}:
            ax.xaxis.set_major_formatter(
                FuncFormatter(
                    lambda value, _: f"R$ {value / 1_000_000:.1f} mi".replace(".", ",")
                )
            )
            ax.set_xlabel(f"{attribute} (milhões de reais)")
        else:
            ax.set_xlabel(attribute)
        fig.tight_layout()
        boxplot_path = images_dir / f"{attribute.lower()}_boxplot.png"
        fig.savefig(boxplot_path, dpi=180, bbox_inches="tight")
        plt.close(fig)
        created.append(boxplot_path)
    return created


def fmt(value: object, decimals: int = 2) -> str:
    if value == "" or pd.isna(value):
        return "n/d"
    return f"{float(value):,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def generate_markdown(stats: pd.DataFrame, sample_path: Path) -> str:
    indexed = stats.set_index("atributo")
    lines = [
        "# Análise exploratória dos atributos candidatos",
        "",
        "## Escopo e método",
        "",
        f"A análise usa `{sample_path.as_posix()}`, com 10.000 registros selecionados na Etapa 2 usando seed 42.",
        "`ROW_ID_AMOSTRA`, `SK_ID_CURR` e `TARGET` não foram analisados como atributos de agrupamento.",
        "Possíveis outliers numéricos foram sinalizados pela regra de 1,5 × IQR. Para campos nominais ou ordinais, a contagem mecânica de IQR não deve ser interpretada como anomalia.",
        "Nenhuma base ponderada foi gerada e Hopkins não foi executado.",
        "",
        "## Visão geral",
        "",
        "| Atributo | Tipo semântico | Ausentes | Únicos | Zeros | Mediana | Assimetria | Outliers IQR |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for attribute in CANDIDATES:
        row = indexed.loc[attribute]
        lines.append(
            f"| `{attribute}` | {row['tipo_semantico']} | {int(row['ausentes'])} | "
            f"{int(row['valores_unicos'])} | {int(row['zeros'])} | {fmt(row['mediana'])} | "
            f"{fmt(row['assimetria'])} | {int(row['possiveis_outliers_iqr'])} |"
        )

    lines.extend(["", "## Análise preliminar por atributo", ""])
    for attribute in CANDIDATES:
        row = indexed.loc[attribute]
        info = ATTRIBUTE_INFO[attribute]
        lines.extend(
            [
                f"### {attribute}",
                "",
                f"- Papel de negócio: {info['business']}",
                f"- Tipo indicado no p1: **{info['p1_type']}**.",
                f"- Faixa observada: {fmt(row['minimo'])} a {fmt(row['maximo'])}; mediana {fmt(row['mediana'])}.",
                f"- Ausentes: {int(row['ausentes'])}; zeros: {int(row['zeros'])} ({fmt(row['percentual_zeros'])}%).",
                f"- Assimetria: {fmt(row['assimetria'])}; possíveis outliers por IQR: {int(row['possiveis_outliers_iqr'])} ({fmt(row['percentual_outliers_iqr'])}%).",
                f"- Cuidado: {info['caution']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Proposta para aprovação",
            "",
            "Esta proposta é inicial e não autoriza a geração da base ponderada. Os pesos produzem efeito quadrático por meio da multiplicação por `sqrt(peso)` nos campos numéricos e ordinais. No `p1.py` original, atributos nominais são apenas preservados: seu peso decide inclusão ou exclusão, mas não multiplica a distância; por isso os nominais recebem peso 1 nesta proposta.",
            "`AMT_INCOME_TOTAL` foi mantido como alternativa porque sua mediana é 148.500, mas o máximo de 117 milhões e a assimetria de aproximadamente 99 fariam o Min-Max obrigatório comprimir quase toda a amostra. A renda continuará presente na base auxiliar para caracterizar os clusters, mesmo se não participar da distância.",
            "",
            "| Atributo | Papel | Tipo no p1 | Peso inicial | Justificativa | Problema principal |",
            "|---|---|---|---:|---|---|",
        ]
    )
    for attribute, role, weight, justification in PROPOSAL:
        info = ATTRIBUTE_INFO[attribute]
        lines.append(
            f"| `{attribute}` | {role} | {info['p1_type']} | {weight} | {justification} | {info['caution']} |"
        )

    lines.extend(
        [
            "",
            "## Decisões que exigem aprovação",
            "",
            "1. Aprovar ou alterar os seis atributos principais e seus pesos.",
            "2. Confirmar que `FLAG_OWN_CAR_COD` será recuperado como rótulo nominal N/Y antes do WEKA.",
            "3. Manter `NAME_FAMILY_STATUS_COD` apenas como alternativa e recuperar seus rótulos caso seja aprovado.",
            "4. Confirmar se `AMT_INCOME_TOTAL` deve permanecer fora da distância devido ao outlier extremo, sendo usada apenas na interpretação posterior.",
            "5. Avaliar Hopkins somente após a futura geração da base ponderada autorizada.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    input_path = args.entrada.expanduser().resolve()
    dictionary_path = args.dicionario.expanduser().resolve()
    results_dir = args.resultados_dir.expanduser().resolve()
    images_dir = args.imagens_dir.expanduser().resolve()
    stats_path = results_dir / "estatisticas_atributos.csv"
    analysis_path = results_dir / "analise_atributos.md"

    if not input_path.is_file():
        raise FileNotFoundError(f"Amostra da Etapa 2 não encontrada: {input_path}")
    existing = [path for path in (stats_path, analysis_path) if path.exists()]
    existing.extend(path for path in images_dir.glob("*.png") if path.is_file())
    if existing and not args.sobrescrever:
        raise FileExistsError("Saídas da Etapa 3 já existem. Use --sobrescrever após conferência.")

    df = pd.read_csv(input_path, sep=SEP, low_memory=False)
    missing = [attribute for attribute in CANDIDATES if attribute not in df.columns]
    if missing:
        raise KeyError("Atributos candidatos ausentes: " + ", ".join(missing))
    if len(df) != 10_000:
        raise ValueError(f"A amostra deveria ter 10.000 registros, mas possui {len(df)}.")
    if PROTECTED_COLUMNS.intersection(CANDIDATES):
        raise AssertionError("Uma coluna protegida foi incluída entre os candidatos.")

    results_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    labels = load_code_labels(dictionary_path)
    stats = calculate_statistics(df, labels)
    stats.to_csv(stats_path, sep=SEP, index=False, encoding="utf-8", lineterminator="\n")
    plots = create_plots(df, images_dir)
    analysis_path.write_text(generate_markdown(stats, input_path), encoding="utf-8")

    if len(plots) != len(CANDIDATES) * 2:
        raise AssertionError("Quantidade inesperada de gráficos gerados.")
    reloaded_stats = pd.read_csv(stats_path, sep=SEP)
    if reloaded_stats["atributo"].tolist() != CANDIDATES:
        raise AssertionError("A tabela de estatísticas não preservou a ordem dos candidatos.")
    if reloaded_stats["ausentes"].sum() != 0:
        raise AssertionError("Foram encontrados ausentes inesperados nos candidatos.")

    print("Análise exploratória concluída e validada.")
    print(f"Registros analisados: {len(df)}")
    print(f"Atributos analisados: {len(CANDIDATES)}")
    print(f"Gráficos gerados: {len(plots)}")
    print(f"Estatísticas: {stats_path}")
    print(f"Análise: {analysis_path}")
    print(f"Imagens: {images_dir}")


if __name__ == "__main__":
    main()
