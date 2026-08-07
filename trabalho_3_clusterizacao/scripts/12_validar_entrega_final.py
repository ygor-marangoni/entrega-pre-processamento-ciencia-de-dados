#!/usr/bin/env python3
"""Gera evidências reproduzíveis da validação final sem alterar resultados do WEKA."""

from __future__ import annotations

import argparse
import atexit
import math
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_MATPLOTLIB_CONFIG_DIR = ROOT / ".matplotlib_cache"
_MATPLOTLIB_CONFIG_DIR.mkdir(exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(_MATPLOTLIB_CONFIG_DIR)
atexit.register(shutil.rmtree, _MATPLOTLIB_CONFIG_DIR, ignore_errors=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.io import arff
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.neighbors import NearestNeighbors


SEP = ";"
SEED = 42
SILHOUETTE_SAMPLE = 3_000
EPSILON_WEKA = 0.274264329676
PREPARED = ROOT / "data" / "preparadas" / "base_clusterizacao_final.csv"
WEKA_DIR = ROOT / "data" / "clusterizadas_weka"
RESULT_DIR = ROOT / "resultados" / "validacao_final"
IMAGE_DIR = ROOT / "relatorio" / "imagens" / "clusters"
FINAL_METRICS = ROOT / "resultados" / "comparativos" / "comparativo_metodos.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sobrescrever", action="store_true")
    return parser.parse_args()


def load_arff(path: Path) -> pd.DataFrame:
    records, _ = arff.loadarff(path)
    frame = pd.DataFrame(records)
    for column in frame.columns:
        if frame[column].dtype == object:
            frame[column] = frame[column].map(
                lambda value: value.decode("utf-8") if isinstance(value, bytes) else value
            )
    return frame


def metric_matrix(frame: pd.DataFrame) -> np.ndarray:
    matrix = frame.copy()
    nominal = matrix["FLAG_OWN_CAR_COD"].map({"N": 0.0, "Y": 1.0})
    if nominal.isna().any():
        raise ValueError("Categoria nominal inesperada em FLAG_OWN_CAR_COD.")
    matrix["FLAG_OWN_CAR_COD"] = nominal
    values = matrix.to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Matriz de distâncias contém valor não finito.")
    return values


def normalized_labels(series: pd.Series, method: str) -> np.ndarray:
    if method == "dbscan":
        return series.fillna("ruido").replace("?", "ruido").astype(str).to_numpy()
    if series.isna().any() or (series.astype(str) == "?").any():
        raise ValueError(f"{method} contém rótulo ausente.")
    return series.astype(str).to_numpy()


def calculate_metrics(method: str, frame: pd.DataFrame) -> dict[str, object]:
    labels = normalized_labels(frame["cluster"], method)
    valid = labels != "ruido"
    matrix = metric_matrix(frame.drop(columns="cluster"))[valid]
    clean_labels = labels[valid]
    codes, unique = pd.factorize(clean_labels, sort=True)
    counts = pd.Series(clean_labels).value_counts()
    probabilities = counts.to_numpy(dtype=float) / counts.sum()
    entropy = -np.sum(probabilities * np.log(probabilities)) / math.log(len(counts))
    return {
        "metodo": method,
        "registros": len(frame),
        "registros_metricas": int(valid.sum()),
        "clusters": len(unique),
        "ruidos": int((~valid).sum()),
        "silhouette": float(
            silhouette_score(
                matrix,
                codes,
                metric="euclidean",
                sample_size=min(SILHOUETTE_SAMPLE, len(matrix)),
                random_state=SEED,
            )
        ),
        "davies_bouldin": float(davies_bouldin_score(matrix, codes)),
        "calinski_harabasz": float(calinski_harabasz_score(matrix, codes)),
        "entropia_tamanhos_normalizada": float(entropy),
        "menor_cluster": int(counts.min()),
        "maior_cluster": int(counts.max()),
        "soma_clusters_sem_ruido": int(counts.sum()),
        "silhouette_amostra": min(SILHOUETTE_SAMPLE, len(matrix)),
        "seed": SEED,
    }


def require_writable(path: Path, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Arquivo já existe; use --sobrescrever: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)


def save_k_distance(prepared: pd.DataFrame, overwrite: bool) -> tuple[float, float]:
    matrix = metric_matrix(prepared)
    distances = np.sort(
        NearestNeighbors(n_neighbors=6, metric="euclidean")
        .fit(matrix)
        .kneighbors(matrix)[0][:, -1]
    )
    x = np.arange(len(distances), dtype=float)
    x_normalized = (x - x.min()) / (x.max() - x.min())
    y_normalized = (distances - distances.min()) / (distances.max() - distances.min())
    # Joelho geométrico: maior distância vertical entre a curva normalizada e
    # a reta que une seus extremos. Em uma curva crescente e convexa, equivale
    # a maximizar x_normalizado - y_normalizado.
    knee_index = int(np.argmax(x_normalized - y_normalized))
    knee = float(distances[knee_index])
    percentile = knee_index / (len(distances) - 1) * 100

    curve_path = RESULT_DIR / "k_distance_dbscan.csv"
    graph_path = IMAGE_DIR / "k_distance_dbscan.png"
    require_writable(curve_path, overwrite)
    require_writable(graph_path, overwrite)
    pd.DataFrame(
        {
            "ordem": np.arange(1, len(distances) + 1),
            "percentil": x_normalized * 100,
            "distancia_sexto_vizinho": distances,
            "distancia_geometrica_normalizada": x_normalized - y_normalized,
            "eh_joelho": np.arange(len(distances)) == knee_index,
        }
    ).to_csv(curve_path, sep=SEP, index=False, encoding="utf-8", lineterminator="\n")

    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.plot(x_normalized * 100, distances, color="#276FBF", linewidth=1.8)
    ax.scatter([percentile], [knee], color="#C23B22", s=55, zorder=3)
    ax.axvline(percentile, color="#C23B22", linestyle="--", linewidth=1)
    ax.axhline(knee, color="#C23B22", linestyle="--", linewidth=1)
    ax.annotate(
        f"Joelho: ε = {knee:.12f}\nPercentil = {percentile:.2f}%",
        xy=(percentile, knee),
        xytext=(61, knee + 0.18),
        arrowprops={"arrowstyle": "->", "color": "#C23B22"},
        fontsize=11,
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.95},
    )
    ax.set_title("Curva k-distance do DBSCAN (sexto vizinho)", fontsize=14)
    ax.set_xlabel("Percentil dos registros ordenados")
    ax.set_ylabel("Distância euclidiana ao sexto vizinho")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(graph_path, dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return knee, percentile


def main() -> None:
    args = parse_args()
    prepared = pd.read_csv(PREPARED, sep=SEP, low_memory=False)
    if prepared.shape != (10_000, 6):
        raise ValueError(f"Base preparada inesperada: {prepared.shape}")

    knee, percentile = save_k_distance(prepared, args.sobrescrever)
    if abs(knee - EPSILON_WEKA) > 1e-10:
        raise ValueError(f"Joelho não reproduz o epsilon do WEKA: {knee:.15f}")

    dbscan_arff = WEKA_DIR / "base_clusterizada_dbscan.arff"
    dbscan = load_arff(dbscan_arff)
    dbscan["cluster"] = dbscan["cluster"].fillna("ruido").replace("?", "ruido")
    dbscan_csv = WEKA_DIR / "base_clusterizada_dbscan.csv"
    require_writable(dbscan_csv, args.sobrescrever)
    dbscan.to_csv(dbscan_csv, sep=SEP, index=False, encoding="utf-8", lineterminator="\n")

    records: list[dict[str, object]] = []
    for method in ("kmeans", "em"):
        for k in (8, 9, 10):
            path = WEKA_DIR / f"base_clusterizada_{method}_k{k}.csv"
            record = calculate_metrics(method, pd.read_csv(path, sep=SEP, low_memory=False))
            record["configuracao"] = f"K={k}"
            record["arquivo"] = path.name
            records.append(record)
    tests_path = RESULT_DIR / "metricas_testes_kmeans_em.csv"
    require_writable(tests_path, args.sobrescrever)
    pd.DataFrame(records).to_csv(
        tests_path, sep=SEP, index=False, encoding="utf-8", lineterminator="\n"
    )

    finals = {
        "dbscan": dbscan,
        "kmeans": pd.read_csv(WEKA_DIR / "base_clusterizada_kmeans_final.csv", sep=SEP),
        "em": pd.read_csv(WEKA_DIR / "base_clusterizada_em_final.csv", sep=SEP),
    }
    saved = pd.read_csv(FINAL_METRICS, sep=SEP).set_index("metodo")
    difference_rows: list[dict[str, object]] = []
    for method, frame in finals.items():
        recalculated = calculate_metrics(method, frame)
        for metric in (
            "silhouette",
            "davies_bouldin",
            "calinski_harabasz",
            "entropia_tamanhos_normalizada",
            "menor_cluster",
            "maior_cluster",
            "ruidos",
        ):
            original = float(saved.at[method, metric])
            current = float(recalculated[metric])
            difference_rows.append(
                {
                    "metodo": method,
                    "metrica": metric,
                    "valor_registrado": original,
                    "valor_recalculado": current,
                    "diferenca_absoluta": abs(original - current),
                    "status": "OK" if abs(original - current) <= 1e-10 else "DIVERGENTE",
                }
            )
    differences_path = RESULT_DIR / "diferencas_metricas_finais.csv"
    require_writable(differences_path, args.sobrescrever)
    pd.DataFrame(difference_rows).to_csv(
        differences_path, sep=SEP, index=False, encoding="utf-8", lineterminator="\n"
    )

    print(f"Joelho geométrico: {knee:.12f} (percentil {percentile:.4f}%)")
    print(f"CSV DBSCAN derivado do ARFF: {dbscan_csv}")
    print(f"Métricas dos testes: {tests_path}")
    print(f"Diferenças finais: {differences_path}")


if __name__ == "__main__":
    main()
