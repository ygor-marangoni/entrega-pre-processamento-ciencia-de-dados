#!/usr/bin/env python3
"""Mescla os clusters finais com a amostra rastreável da Etapa 2."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from scipy.io import arff


SEP = ";"
SCRIPT_DIR = Path(__file__).resolve().parent
TRABALHO_3_DIR = SCRIPT_DIR.parent
DEFAULT_ANALYSIS = TRABALHO_3_DIR / "data" / "amostras" / "base_amostra_10000_analise.csv"
DEFAULT_PREPARED = TRABALHO_3_DIR / "data" / "preparadas" / "base_clusterizacao_final.csv"
DEFAULT_EXPORT_DIR = TRABALHO_3_DIR / "data" / "clusterizadas_weka"
DEFAULT_OUTPUT_DIR = TRABALHO_3_DIR / "data" / "analise"
DEFAULT_METADATA = TRABALHO_3_DIR / "resultados" / "clusters" / "metadados_juncao_clusters.json"

EXPORTS = {
    "dbscan": "base_clusterizada_dbscan.arff",
    "kmeans": "base_clusterizada_kmeans_final.csv",
    "em": "base_clusterizada_em_final.csv",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mescla os clusters com a base auxiliar.")
    parser.add_argument("--base-analise", type=Path, default=DEFAULT_ANALYSIS)
    parser.add_argument("--base-preparada", type=Path, default=DEFAULT_PREPARED)
    parser.add_argument("--exportacoes-dir", type=Path, default=DEFAULT_EXPORT_DIR)
    parser.add_argument("--saida-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--metadados", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--sobrescrever", action="store_true")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_export(path: Path) -> pd.DataFrame:
    if path.suffix.casefold() == ".arff":
        records, _ = arff.loadarff(path)
        frame = pd.DataFrame(records)
        for column in frame.columns:
            if frame[column].dtype == object:
                frame[column] = frame[column].map(
                    lambda value: value.decode("utf-8") if isinstance(value, bytes) else value
                )
        return frame
    return pd.read_csv(path, sep=SEP, low_memory=False)


def normalize_cluster(series: pd.Series, method: str) -> pd.Series:
    if method == "dbscan":
        return series.fillna("ruido").replace("?", "ruido").astype(str)
    if series.isna().any() or (series.astype(str) == "?").any():
        raise ValueError(f"Cluster ausente inesperado em {method}.")
    return series.astype(str)


def write_csv_atomic(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_name(path.name + ".tmp")
    try:
        frame.to_csv(temporary, sep=SEP, index=False, encoding="utf-8", lineterminator="\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def write_json_atomic(data: dict[str, object], path: Path) -> None:
    temporary = path.with_name(path.name + ".tmp")
    try:
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    args = parse_args()
    analysis_path = args.base_analise.expanduser().resolve()
    prepared_path = args.base_preparada.expanduser().resolve()
    export_dir = args.exportacoes_dir.expanduser().resolve()
    output_dir = args.saida_dir.expanduser().resolve()
    metadata_path = args.metadados.expanduser().resolve()
    outputs = {method: output_dir / f"analise_cluster_{method}.csv" for method in EXPORTS}
    existing = [path for path in [*outputs.values(), metadata_path] if path.exists()]
    if existing and not args.sobrescrever:
        raise FileExistsError("Saídas já existem: " + ", ".join(path.name for path in existing))

    analysis = pd.read_csv(analysis_path, sep=SEP, low_memory=False)
    prepared = pd.read_csv(prepared_path, sep=SEP, low_memory=False)
    if analysis.shape != (10_000, 42) or prepared.shape != (10_000, 6):
        raise ValueError(f"Dimensões inesperadas: análise={analysis.shape}, preparada={prepared.shape}")
    if not analysis["ROW_ID_AMOSTRA"].is_unique or not analysis["SK_ID_CURR"].is_unique:
        raise ValueError("Identificadores da amostra não são únicos.")
    if analysis[["ROW_ID_AMOSTRA", "SK_ID_CURR"]].isna().any().any():
        raise ValueError("Identificador ausente na base de análise.")

    transformed = prepared.rename(columns={column: f"{column}_TRANSFORMADO" for column in prepared.columns})
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    output_metadata: dict[str, object] = {}

    for method, filename in EXPORTS.items():
        export_path = export_dir / filename
        exported = load_export(export_path)
        expected_columns = prepared.columns.tolist() + ["cluster"]
        if exported.shape != (10_000, 7) or exported.columns.tolist() != expected_columns:
            raise ValueError(f"Exportação inesperada em {method}.")
        for column in prepared.columns:
            if not pd.api.types.is_numeric_dtype(prepared[column]):
                equal = exported[column].astype(str).tolist() == prepared[column].astype(str).tolist()
            else:
                equal = np.allclose(exported[column], prepared[column], rtol=0, atol=1e-15)
            if not equal:
                raise ValueError(f"A ordem divergiu em {method}/{column}.")
        cluster = normalize_cluster(exported["cluster"], method).rename("cluster")
        merged = pd.concat(
            [analysis.reset_index(drop=True), transformed.reset_index(drop=True), cluster.reset_index(drop=True)],
            axis=1,
        )
        if merged.shape != (10_000, 49) or len(merged) != len(analysis):
            raise AssertionError(f"Junção inesperada em {method}: {merged.shape}")
        if not merged["ROW_ID_AMOSTRA"].equals(analysis["ROW_ID_AMOSTRA"]):
            raise AssertionError(f"ROW_ID_AMOSTRA foi alterado em {method}.")
        write_csv_atomic(merged, outputs[method])
        reloaded = pd.read_csv(outputs[method], sep=SEP, low_memory=False)
        if reloaded.shape != merged.shape or not reloaded["ROW_ID_AMOSTRA"].equals(analysis["ROW_ID_AMOSTRA"]):
            raise AssertionError(f"Saída gravada inválida em {method}.")
        output_metadata[method] = {
            "exportacao_weka": str(export_path),
            "sha256_exportacao": sha256_file(export_path),
            "saida": str(outputs[method]),
            "sha256_saida": sha256_file(outputs[method]),
            "registros": len(reloaded),
            "colunas": len(reloaded.columns),
            "clusters": int(reloaded.loc[reloaded["cluster"] != "ruido", "cluster"].nunique()),
            "ruidos": int((reloaded["cluster"] == "ruido").sum()),
        }

    metadata = {
        "etapa": 11,
        "generated_at": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(timespec="seconds"),
        "timezone": "America/Sao_Paulo",
        "base_analise": {"path": str(analysis_path), "sha256": sha256_file(analysis_path)},
        "base_preparada": {"path": str(prepared_path), "sha256": sha256_file(prepared_path)},
        "transformados_com_sufixo": "_TRANSFORMADO",
        "target_usado_no_agrupamento": False,
        "outputs": output_metadata,
    }
    write_json_atomic(metadata, metadata_path)
    print("Clusters mesclados com a base auxiliar de análise.")
    for method, path in outputs.items():
        print(f"{method}: {path}")
    print(f"Metadados: {metadata_path}")


if __name__ == "__main__":
    main()
