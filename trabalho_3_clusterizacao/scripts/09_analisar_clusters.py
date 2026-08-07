#!/usr/bin/env python3
"""Calcula perfis e métricas técnicas dos clusters finais dos três métodos."""

from __future__ import annotations

import argparse
import math
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)


SEP = ";"
SILHOUETTE_SAMPLE = 3_000
SEED = 42
SCRIPT_DIR = Path(__file__).resolve().parent
TRABALHO_3_DIR = SCRIPT_DIR.parent
DEFAULT_ANALYSIS_DIR = TRABALHO_3_DIR / "data" / "analise"
DEFAULT_CLUSTER_DIR = TRABALHO_3_DIR / "resultados" / "clusters"
DEFAULT_COMPARE_DIR = TRABALHO_3_DIR / "resultados" / "comparativos"

METHOD_FILES = {
    "dbscan": "analise_cluster_dbscan.csv",
    "kmeans": "analise_cluster_kmeans.csv",
    "em": "analise_cluster_em.csv",
}

TRANSFORMED_COLUMNS = [
    "AMT_CREDIT_TRANSFORMADO",
    "CNT_CHILDREN_TRANSFORMADO",
    "FLAG_OWN_CAR_COD_TRANSFORMADO",
    "AGE_YEARS_TRANSFORMADO",
    "CREDIT_INCOME_RATIO_TRANSFORMADO",
    "SER_CREDITOS_ATIVOS_TRANSFORMADO",
]

PROFILE_NUMERIC = [
    "AMT_CREDIT",
    "AMT_INCOME_TOTAL",
    "CNT_CHILDREN",
    "AGE_YEARS",
    "CREDIT_INCOME_RATIO",
    "REGION_RATING_CLIENT",
    "SER_CREDITOS_ATIVOS",
    "SER_DIVIDA_ATRASADA",
]

OUTLIER_COLUMNS = [
    "AMT_CREDIT",
    "AMT_INCOME_TOTAL",
    "CNT_CHILDREN",
    "AGE_YEARS",
    "CREDIT_INCOME_RATIO",
    "SER_CREDITOS_ATIVOS",
    "SER_DIVIDA_ATRASADA",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analisa clusters finais.")
    parser.add_argument("--analise-dir", type=Path, default=DEFAULT_ANALYSIS_DIR)
    parser.add_argument("--clusters-dir", type=Path, default=DEFAULT_CLUSTER_DIR)
    parser.add_argument("--comparativos-dir", type=Path, default=DEFAULT_COMPARE_DIR)
    parser.add_argument("--sobrescrever", action="store_true")
    return parser.parse_args()


def write_csv_atomic(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_name(path.name + ".tmp")
    try:
        frame.to_csv(temporary, sep=SEP, index=False, encoding="utf-8", lineterminator="\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def cluster_sort_key(label: str) -> tuple[int, int | str]:
    if label == "ruido":
        return (1, 0)
    match = re.fullmatch(r"cluster(\d+)", label)
    return (0, int(match.group(1))) if match else (0, label)


def metric_matrix(frame: pd.DataFrame) -> np.ndarray:
    matrix = pd.DataFrame(index=frame.index)
    for column in TRANSFORMED_COLUMNS:
        if column == "FLAG_OWN_CAR_COD_TRANSFORMADO":
            encoded = frame[column].map({"N": 0.0, "Y": 1.0})
            if encoded.isna().any():
                raise ValueError("Categoria inesperada em FLAG_OWN_CAR_COD_TRANSFORMADO.")
            matrix[column] = encoded
        else:
            matrix[column] = pd.to_numeric(frame[column], errors="raise")
    values = matrix.to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Matriz de métricas contém valor não finito.")
    return values


def outlier_mask(group: pd.DataFrame) -> pd.Series:
    result = pd.Series(False, index=group.index)
    for column in OUTLIER_COLUMNS:
        values = pd.to_numeric(group[column], errors="coerce")
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1
        if pd.isna(iqr):
            continue
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        result |= (values < lower) | (values > upper)
    return result


def cluster_profiles(method: str, frame: pd.DataFrame, matrix: np.ndarray) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    labels = frame["cluster"].astype(str)
    for label in sorted(labels.unique(), key=cluster_sort_key):
        positions = np.flatnonzero(labels.to_numpy() == label)
        group = frame.iloc[positions]
        is_noise = label == "ruido"
        record: dict[str, object] = {
            "metodo": method,
            "cluster": label,
            "eh_ruido": is_noise,
            "quantidade": len(group),
            "percentual_base": len(group) / len(frame) * 100,
            "target_0_quantidade": int((group["TARGET"] == 0).sum()),
            "target_1_quantidade": int((group["TARGET"] == 1).sum()),
            "target_1_percentual": float(group["TARGET"].mean() * 100),
            "posse_carro_quantidade": int((group["FLAG_OWN_CAR_COD"] == 1).sum()),
            "posse_carro_percentual": float((group["FLAG_OWN_CAR_COD"] == 1).mean() * 100),
            "name_family_status_cod_moda": group["NAME_FAMILY_STATUS_COD"].mode().iloc[0],
            "name_family_status_cod_moda_frequencia": int(
                (group["NAME_FAMILY_STATUS_COD"] == group["NAME_FAMILY_STATUS_COD"].mode().iloc[0]).sum()
            ),
        }
        for column in PROFILE_NUMERIC:
            values = pd.to_numeric(group[column], errors="raise")
            record[f"{column}_media"] = float(values.mean())
            record[f"{column}_mediana"] = float(values.median())
            record[f"{column}_desvio_padrao"] = float(values.std(ddof=1)) if len(values) > 1 else 0.0

        points = matrix[positions]
        if is_noise:
            record["distancia_media_centro"] = np.nan
            record["distancia_mediana_centro"] = np.nan
            record["dispersao_interna_media_quadratica"] = np.nan
        else:
            center = points.mean(axis=0)
            distances = np.linalg.norm(points - center, axis=1)
            record["distancia_media_centro"] = float(distances.mean())
            record["distancia_mediana_centro"] = float(np.median(distances))
            record["dispersao_interna_media_quadratica"] = float(np.mean(distances**2))
            for index, column in enumerate(TRANSFORMED_COLUMNS):
                record[f"centro_{column}"] = float(center[index])

        outliers = outlier_mask(group)
        record["possiveis_outliers_iqr"] = int(outliers.sum())
        record["percentual_possiveis_outliers_iqr"] = float(outliers.mean() * 100)
        records.append(record)
    return pd.DataFrame(records)


def method_metrics(method: str, frame: pd.DataFrame, matrix: np.ndarray) -> dict[str, object]:
    labels = frame["cluster"].astype(str).to_numpy()
    valid = labels != "ruido"
    clean_matrix = matrix[valid]
    clean_labels = labels[valid]
    codes, uniques = pd.factorize(clean_labels, sort=True)
    if len(uniques) < 2:
        raise ValueError(f"{method} não possui clusters suficientes para métricas.")
    sample_size = min(SILHOUETTE_SAMPLE, len(clean_matrix))
    silhouette = silhouette_score(
        clean_matrix,
        codes,
        metric="euclidean",
        sample_size=sample_size,
        random_state=SEED,
    )
    db = davies_bouldin_score(clean_matrix, codes)
    ch = calinski_harabasz_score(clean_matrix, codes)

    distances_all: list[np.ndarray] = []
    squared_all: list[np.ndarray] = []
    sizes: list[int] = []
    for code in range(len(uniques)):
        points = clean_matrix[codes == code]
        center = points.mean(axis=0)
        distances = np.linalg.norm(points - center, axis=1)
        distances_all.append(distances)
        squared_all.append(distances**2)
        sizes.append(len(points))
    probabilities = np.asarray(sizes, dtype=float) / sum(sizes)
    normalized_entropy = float(-np.sum(probabilities * np.log(probabilities)) / math.log(len(sizes)))
    noise_count = int((~valid).sum())
    return {
        "metodo": method,
        "registros_base": len(frame),
        "registros_metricas_sem_ruido": len(clean_matrix),
        "clusters": len(uniques),
        "ruidos": noise_count,
        "percentual_ruidos": noise_count / len(frame) * 100,
        "silhouette": float(silhouette),
        "silhouette_amostra": sample_size,
        "silhouette_seed": SEED,
        "davies_bouldin": float(db),
        "calinski_harabasz": float(ch),
        "distancia_media_centro": float(np.concatenate(distances_all).mean()),
        "dispersao_interna_media_quadratica": float(np.concatenate(squared_all).mean()),
        "menor_cluster": min(sizes),
        "maior_cluster": max(sizes),
        "razao_maior_menor_cluster": max(sizes) / min(sizes),
        "entropia_tamanhos_normalizada": normalized_entropy,
        "observacao": (
            "Métricas calculadas sem os ruídos; ruído analisado separadamente."
            if method == "dbscan"
            else "Métricas calculadas com todos os registros e rótulos rígidos exportados pelo WEKA."
        ),
    }


def main() -> None:
    args = parse_args()
    analysis_dir = args.analise_dir.expanduser().resolve()
    cluster_dir = args.clusters_dir.expanduser().resolve()
    compare_dir = args.comparativos_dir.expanduser().resolve()
    outputs = {method: cluster_dir / f"resumo_{method}.csv" for method in METHOD_FILES}
    compare_path = compare_dir / "comparativo_metodos.csv"
    existing = [path for path in [*outputs.values(), compare_path] if path.exists()]
    if existing and not args.sobrescrever:
        raise FileExistsError("Saídas já existem: " + ", ".join(path.name for path in existing))
    cluster_dir.mkdir(parents=True, exist_ok=True)
    compare_dir.mkdir(parents=True, exist_ok=True)

    comparisons = []
    for method, filename in METHOD_FILES.items():
        path = analysis_dir / filename
        frame = pd.read_csv(path, sep=SEP, low_memory=False)
        required = set(TRANSFORMED_COLUMNS + PROFILE_NUMERIC + [
            "cluster", "TARGET", "FLAG_OWN_CAR_COD", "NAME_FAMILY_STATUS_COD",
            "ROW_ID_AMOSTRA", "SK_ID_CURR",
        ])
        missing = sorted(required.difference(frame.columns))
        if missing:
            raise KeyError(f"Colunas ausentes em {method}: {missing}")
        if frame.shape != (10_000, 49) or not frame["ROW_ID_AMOSTRA"].is_unique:
            raise ValueError(f"Base de análise inesperada em {method}: {frame.shape}")
        matrix = metric_matrix(frame)
        profiles = cluster_profiles(method, frame, matrix)
        write_csv_atomic(profiles, outputs[method])
        comparisons.append(method_metrics(method, frame, matrix))

    comparative = pd.DataFrame(comparisons)
    write_csv_atomic(comparative, compare_path)
    print("Análise técnica dos clusters concluída.")
    print(comparative.to_string(index=False))
    for method, path in outputs.items():
        print(f"{method}: {path}")
    print(f"Comparativo: {compare_path}")


if __name__ == "__main__":
    main()
