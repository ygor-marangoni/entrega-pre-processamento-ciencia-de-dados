#!/usr/bin/env python3
"""Gera os gráficos técnicos da Etapa 12 a partir dos resumos validados."""

from __future__ import annotations

import argparse
import atexit
import os
import re
import shutil
from pathlib import Path

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
TRABALHO_3_DIR = SCRIPT_DIR.parent
_MPL_TEMP = TRABALHO_3_DIR / "resultados" / ".matplotlib_cache_runtime"
_MPL_TEMP.mkdir(parents=True, exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(_MPL_TEMP)
atexit.register(lambda: shutil.rmtree(_MPL_TEMP, ignore_errors=True))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402


SEP = ";"
DEFAULT_CLUSTER_DIR = TRABALHO_3_DIR / "resultados" / "clusters"
DEFAULT_COMPARE = TRABALHO_3_DIR / "resultados" / "comparativos" / "comparativo_metodos.csv"
DEFAULT_OUTPUT_DIR = TRABALHO_3_DIR / "relatorio" / "imagens" / "clusters"
METHODS = ["dbscan", "kmeans", "em"]
METHOD_LABELS = {"dbscan": "DBSCAN", "kmeans": "SimpleKMeans", "em": "EM"}
METHOD_COLORS = {"dbscan": "#4472C4", "kmeans": "#70AD47", "em": "#ED7D31"}

PROFILE_COLUMNS = {
    "AMT_CREDIT_media": "Crédito",
    "AMT_INCOME_TOTAL_media": "Renda",
    "CNT_CHILDREN_media": "Filhos",
    "AGE_YEARS_media": "Idade",
    "CREDIT_INCOME_RATIO_media": "Crédito/renda",
    "SER_CREDITOS_ATIVOS_media": "Créditos ativos",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera gráficos dos clusters finais.")
    parser.add_argument("--clusters-dir", type=Path, default=DEFAULT_CLUSTER_DIR)
    parser.add_argument("--comparativo", type=Path, default=DEFAULT_COMPARE)
    parser.add_argument("--saida-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--sobrescrever", action="store_true")
    return parser.parse_args()


def label_cluster(value: str) -> str:
    if value == "ruido":
        return "Ruído"
    match = re.fullmatch(r"cluster(\d+)", value)
    return f"C{match.group(1)}" if match else value


def save_figure(fig: plt.Figure, path: Path, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Gráfico já existe: {path}")
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def graph_distribution(method: str, summary: pd.DataFrame, output: Path, overwrite: bool) -> None:
    labels = [label_cluster(value) for value in summary["cluster"].astype(str)]
    colors = ["#C00000" if value == "ruido" else METHOD_COLORS[method] for value in summary["cluster"]]
    fig, ax = plt.subplots(figsize=(12, 6.8))
    bars = ax.bar(labels, summary["quantidade"], color=colors, edgecolor="#333333", linewidth=0.5)
    ax.bar_label(bars, labels=[f"{int(v):,}".replace(",", ".") for v in summary["quantidade"]], padding=3, fontsize=9)
    ax.set_title(f"Distribuição dos registros por grupo — {METHOD_LABELS[method]}")
    ax.set_xlabel("Grupo")
    ax.set_ylabel("Quantidade de registros")
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    save_figure(fig, output / f"distribuicao_clusters_{method}.png", overwrite)


def graph_target(method: str, summary: pd.DataFrame, output: Path, overwrite: bool) -> None:
    labels = [label_cluster(value) for value in summary["cluster"].astype(str)]
    colors = ["#C00000" if value == "ruido" else METHOD_COLORS[method] for value in summary["cluster"]]
    fig, ax = plt.subplots(figsize=(12, 6.8))
    bars = ax.bar(labels, summary["target_1_percentual"], color=colors, edgecolor="#333333", linewidth=0.5)
    ax.bar_label(bars, labels=[f"{v:.1f}%" for v in summary["target_1_percentual"]], padding=3, fontsize=9)
    ax.axhline(summary.eval("target_1_quantidade").sum() / summary["quantidade"].sum() * 100, color="#555555", linestyle="--", linewidth=1, label="Taxa global")
    ax.set_title(f"Proporção posterior de TARGET=1 por grupo — {METHOD_LABELS[method]}")
    ax.set_xlabel("Grupo")
    ax.set_ylabel("TARGET=1 (%)")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    save_figure(fig, output / f"target_por_cluster_{method}.png", overwrite)


def graph_profile(method: str, summary: pd.DataFrame, output: Path, overwrite: bool) -> None:
    values = summary[list(PROFILE_COLUMNS)].astype(float).copy()
    standard = (values - values.mean(axis=0)) / values.std(axis=0, ddof=0).replace(0, 1)
    standard.columns = list(PROFILE_COLUMNS.values())
    standard.index = [label_cluster(value) for value in summary["cluster"].astype(str)]
    fig, ax = plt.subplots(figsize=(12, max(6.8, 0.52 * len(standard) + 2.5)))
    sns.heatmap(
        standard,
        cmap="vlag",
        center=0,
        annot=True,
        fmt=".2f",
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "Desvio-padrão em relação aos grupos"},
        ax=ax,
    )
    ax.set_title(f"Perfil médio padronizado dos grupos — {METHOD_LABELS[method]}")
    ax.set_xlabel("Atributo")
    ax.set_ylabel("Grupo")
    save_figure(fig, output / f"perfil_padronizado_{method}.png", overwrite)


def graph_comparative(comparative: pd.DataFrame, output: Path, overwrite: bool) -> None:
    frame = comparative.set_index("metodo").loc[METHODS].reset_index()
    labels = [METHOD_LABELS[value] for value in frame["metodo"]]
    colors = [METHOD_COLORS[value] for value in frame["metodo"]]
    metrics = [
        ("silhouette", "Silhouette (maior é melhor)", ".3f"),
        ("davies_bouldin", "Davies–Bouldin (menor é melhor)", ".3f"),
        ("calinski_harabasz", "Calinski–Harabasz (maior é melhor)", ".1f"),
    ]
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 11.5))
    for ax, (column, title, fmt) in zip(axes, metrics, strict=True):
        bars = ax.bar(labels, frame[column], color=colors, edgecolor="#333333", linewidth=0.5)
        ax.bar_label(
            bars,
            labels=[format(value, fmt) for value in frame[column]],
            padding=4,
            fontsize=11,
        )
        ax.set_title(title, fontsize=12, pad=8)
        ax.tick_params(axis="both", labelsize=10)
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
    fig.suptitle("Comparação técnica dos métodos nas atribuições finais", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.97), h_pad=2.0)
    save_figure(fig, output / "comparativo_metricas.png", overwrite)


def main() -> None:
    args = parse_args()
    cluster_dir = args.clusters_dir.expanduser().resolve()
    compare_path = args.comparativo.expanduser().resolve()
    output_dir = args.saida_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook")

    for method in METHODS:
        summary = pd.read_csv(cluster_dir / f"resumo_{method}.csv", sep=SEP, low_memory=False)
        graph_distribution(method, summary, output_dir, args.sobrescrever)
        graph_target(method, summary, output_dir, args.sobrescrever)
        graph_profile(method, summary, output_dir, args.sobrescrever)
    comparative = pd.read_csv(compare_path, sep=SEP, low_memory=False)
    graph_comparative(comparative, output_dir, args.sobrescrever)
    print("Gráficos da Etapa 12 gerados.")
    for path in sorted(output_dir.glob("*.png")):
        print(path)


if __name__ == "__main__":
    main()
