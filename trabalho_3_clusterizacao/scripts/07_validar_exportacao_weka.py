#!/usr/bin/env python3
"""Valida as três bases finais realmente exportadas pelo WEKA."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import arff


SEP = ";"
PROTECTED_COLUMNS = {"SK_ID_CURR", "TARGET", "ROW_ID_AMOSTRA"}
SCRIPT_DIR = Path(__file__).resolve().parent
TRABALHO_3_DIR = SCRIPT_DIR.parent
DEFAULT_PREPARED = TRABALHO_3_DIR / "data" / "preparadas" / "base_clusterizacao_final.csv"
DEFAULT_EXPORT_DIR = TRABALHO_3_DIR / "data" / "clusterizadas_weka"
DEFAULT_RESULT = TRABALHO_3_DIR / "resultados" / "clusters" / "validacao_exportacoes_weka.csv"

EXPORTS = {
    "dbscan": "base_clusterizada_dbscan.arff",
    "kmeans": "base_clusterizada_kmeans_final.csv",
    "em": "base_clusterizada_em_final.csv",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Valida as exportações finais do WEKA.")
    parser.add_argument("--base-preparada", type=Path, default=DEFAULT_PREPARED)
    parser.add_argument("--exportacoes-dir", type=Path, default=DEFAULT_EXPORT_DIR)
    parser.add_argument("--resultado", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--sobrescrever", action="store_true")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_weka_export(path: Path) -> pd.DataFrame:
    if path.suffix.casefold() == ".arff":
        records, _ = arff.loadarff(path)
        frame = pd.DataFrame(records)
        for column in frame.columns:
            if frame[column].dtype == object:
                frame[column] = frame[column].map(
                    lambda value: value.decode("utf-8") if isinstance(value, bytes) else value
                )
        return frame
    if path.suffix.casefold() == ".csv":
        return pd.read_csv(path, sep=SEP, low_memory=False)
    raise ValueError(f"Formato não suportado: {path}")


def normalize_cluster(series: pd.Series, method: str) -> pd.Series:
    values = series.copy()
    if method == "dbscan":
        values = values.fillna("ruido").replace("?", "ruido")
    elif values.isna().any() or (values.astype(str) == "?").any():
        raise ValueError(f"{method} contém cluster ausente inesperado.")
    return values.astype(str)


def validate_export(
    method: str, path: Path, prepared: pd.DataFrame
) -> tuple[pd.DataFrame, dict[str, object]]:
    if not path.is_file():
        raise FileNotFoundError(f"Exportação final de {method} não encontrada: {path}")
    exported = load_weka_export(path)
    if exported.shape != (10_000, len(prepared.columns) + 1):
        raise ValueError(f"Dimensão inesperada em {method}: {exported.shape}")
    expected_columns = prepared.columns.tolist() + ["cluster"]
    if exported.columns.tolist() != expected_columns:
        raise ValueError(f"Colunas ou ordem inesperadas em {method}.")
    if PROTECTED_COLUMNS.intersection(exported.columns):
        raise ValueError(f"Coluna protegida encontrada em {method}.")

    for column in prepared.columns:
        if not pd.api.types.is_numeric_dtype(prepared[column]):
            if exported[column].astype(str).tolist() != prepared[column].astype(str).tolist():
                raise ValueError(f"Ordem/valores divergentes em {method}/{column}.")
        elif not np.allclose(
            pd.to_numeric(exported[column], errors="raise"),
            pd.to_numeric(prepared[column], errors="raise"),
            rtol=0,
            atol=1e-15,
        ):
            raise ValueError(f"Ordem/valores divergentes em {method}/{column}.")

    exported["cluster"] = normalize_cluster(exported["cluster"], method)
    labels = sorted(exported.loc[exported["cluster"] != "ruido", "cluster"].unique())
    noise_count = int((exported["cluster"] == "ruido").sum())
    if len(labels) != 9:
        raise ValueError(f"Esperados 9 clusters finais em {method}; encontrados {len(labels)}.")
    if method == "dbscan" and noise_count == 0:
        raise ValueError("O DBSCAN final deveria preservar os registros de ruído.")
    if method != "dbscan" and noise_count != 0:
        raise ValueError(f"Ruído inesperado em {method}.")

    record = {
        "metodo": method,
        "arquivo": path.name,
        "sha256": sha256_file(path),
        "registros": len(exported),
        "atributos_entrada": len(prepared.columns),
        "atributos_exportados": len(exported.columns),
        "coluna_cluster_presente": True,
        "clusters": len(labels),
        "ruidos": noise_count,
        "percentual_ruidos": noise_count / len(exported) * 100,
        "ordem_preservada": True,
        "valores_entrada_preservados": True,
        "colunas_protegidas_ausentes": True,
    }
    return exported, record


def write_csv_atomic(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_name(path.name + ".tmp")
    try:
        frame.to_csv(temporary, sep=SEP, index=False, encoding="utf-8", lineterminator="\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    args = parse_args()
    prepared_path = args.base_preparada.expanduser().resolve()
    export_dir = args.exportacoes_dir.expanduser().resolve()
    result_path = args.resultado.expanduser().resolve()
    if result_path.exists() and not args.sobrescrever:
        raise FileExistsError(f"Resultado já existe: {result_path}")
    prepared = pd.read_csv(prepared_path, sep=SEP, low_memory=False)
    if prepared.shape != (10_000, 6):
        raise ValueError(f"Base preparada inesperada: {prepared.shape}")

    records = []
    for method, filename in EXPORTS.items():
        _, record = validate_export(method, export_dir / filename, prepared)
        records.append(record)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result = pd.DataFrame(records)
    write_csv_atomic(result, result_path)
    print("Exportações finais do WEKA validadas.")
    print(result.to_string(index=False))
    print(f"Resultado: {result_path}")


if __name__ == "__main__":
    main()
