#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera graficos comparativos a partir das metricas reais do WEKA."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


SCRIPT_DIR = Path(__file__).resolve().parent
TRABALHO_DIR = SCRIPT_DIR.parent
RESULTS_CSV = TRABALHO_DIR / "resultados" / "comparativo_metricas.csv"
IMAGES_DIR = TRABALHO_DIR / "relatorio" / "imagens"

GRAPH_SPECS = [
    ("acuracia", "Acuracia (%)", "comparativo_acuracia.png"),
    ("recall_classe_1", "Recall da classe 1", "comparativo_recall_classe_1.png"),
    ("f_measure_classe_1", "F-Measure da classe 1", "comparativo_fmeasure_classe_1.png"),
    ("roc_area_classe_1", "ROC Area da classe 1", "comparativo_roc_area.png"),
]


def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.replace("NA", pd.NA), errors="coerce")


def plot_metric(df: pd.DataFrame, metric: str, title: str, filename: str) -> bool:
    if metric not in df.columns:
        return False

    plot_df = df[["metodo", "base", metric]].copy()
    plot_df[metric] = to_numeric(plot_df[metric])
    plot_df = plot_df.dropna(subset=[metric])
    if plot_df.empty:
        return False

    pivot = plot_df.pivot(index="metodo", columns="base", values=metric)
    method_order = ["J48", "RandomForest", "IBk", "NaiveBayes", "BayesNet"]
    pivot = pivot.reindex([method for method in method_order if method in pivot.index])

    ax = pivot.plot(kind="bar", figsize=(10, 5), width=0.78)
    ax.set_title(title)
    ax.set_xlabel("Metodo")
    ax.set_ylabel(title)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(title="Base")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = IMAGES_DIR / filename
    plt.savefig(output_path, dpi=160)
    plt.close()
    print(f"Grafico gerado: {output_path}")
    return True


def main() -> None:
    if not RESULTS_CSV.exists():
        raise FileNotFoundError(f"Arquivo de metricas nao encontrado: {RESULTS_CSV}")

    df = pd.read_csv(RESULTS_CSV, sep=";")
    generated = 0
    for metric, title, filename in GRAPH_SPECS:
        if plot_metric(df, metric, title, filename):
            generated += 1

    if generated == 0:
        print("Nenhum grafico foi gerado porque ainda nao ha metricas numericas reais.")
    else:
        print(f"Graficos gerados: {generated}")


if __name__ == "__main__":
    main()
