#!/usr/bin/env python3
"""Cria a amostra reproduzível e rastreável usada no Trabalho 3.

Saídas:
- base_amostra_10000_completa.csv: atributos disponíveis para as etapas futuras,
  sem SK_ID_CURR e TARGET, mas com ROW_ID_AMOSTRA.
- base_amostra_10000_analise.csv: base auxiliar com todas as colunas originais,
  incluindo SK_ID_CURR e TARGET, além de ROW_ID_AMOSTRA.
- metadados_amostra_10000.json: proveniência, configuração e hashes SHA-256.

Nenhum atributo é selecionado nesta etapa. ROW_ID_AMOSTRA corresponde à posição
1-based do registro na base de origem, desconsiderando o cabeçalho.
"""

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


SEED = 42
SAMPLE_SIZE = 10_000
SEP = ";"
ROW_ID = "ROW_ID_AMOSTRA"
ID_COLUMN = "SK_ID_CURR"
TARGET_COLUMN = "TARGET"

SCRIPT_DIR = Path(__file__).resolve().parent
TRABALHO_3_DIR = SCRIPT_DIR.parent
REPOSITORY_ROOT = TRABALHO_3_DIR.parent
DEFAULT_INPUT = (
    REPOSITORY_ROOT
    / "trabalho_1_preprocessamento"
    / "data"
    / "base_final_preprocessada.csv"
)
DEFAULT_OUTPUT_DIR = TRABALHO_3_DIR / "data" / "amostras"

COMPLETE_FILENAME = "base_amostra_10000_completa.csv"
ANALYSIS_FILENAME = "base_amostra_10000_analise.csv"
METADATA_FILENAME = "metadados_amostra_10000.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cria uma amostra reproduzível de 10.000 registros para o Trabalho 3."
    )
    parser.add_argument(
        "--entrada",
        type=Path,
        default=DEFAULT_INPUT,
        help="Base preprocessada do Trabalho 1.",
    )
    parser.add_argument(
        "--saida-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Diretório para os dois CSVs e o arquivo de metadados.",
    )
    parser.add_argument(
        "--sobrescrever",
        action="store_true",
        help="Permite substituir saídas existentes após todas as validações.",
    )
    return parser.parse_args()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_paths(input_path: Path, output_dir: Path, overwrite: bool) -> tuple[Path, Path, Path]:
    if not input_path.is_file():
        raise FileNotFoundError(f"Base de origem não encontrada: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    complete_path = output_dir / COMPLETE_FILENAME
    analysis_path = output_dir / ANALYSIS_FILENAME
    metadata_path = output_dir / METADATA_FILENAME

    existing = [path for path in (complete_path, analysis_path, metadata_path) if path.exists()]
    if existing and not overwrite:
        names = ", ".join(path.name for path in existing)
        raise FileExistsError(
            f"Saídas já existentes: {names}. Use --sobrescrever somente após conferir os arquivos."
        )
    return complete_path, analysis_path, metadata_path


def write_csv_atomic(df: pd.DataFrame, path: Path) -> None:
    temporary = path.with_name(path.name + ".tmp")
    try:
        df.to_csv(temporary, sep=SEP, index=False, encoding="utf-8", lineterminator="\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def write_json_atomic(data: dict[str, object], path: Path) -> None:
    temporary = path.with_name(path.name + ".tmp")
    try:
        temporary.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def validate_frames(
    source: pd.DataFrame,
    sampled_analysis: pd.DataFrame,
    sampled_complete: pd.DataFrame,
) -> None:
    if len(sampled_analysis) != SAMPLE_SIZE or len(sampled_complete) != SAMPLE_SIZE:
        raise AssertionError("As duas saídas precisam conter exatamente 10.000 registros.")
    if not sampled_analysis[ROW_ID].is_unique or not sampled_complete[ROW_ID].is_unique:
        raise AssertionError("ROW_ID_AMOSTRA precisa ser único nas duas saídas.")
    if sampled_analysis[ROW_ID].tolist() != sampled_complete[ROW_ID].tolist():
        raise AssertionError("A ordem dos registros diverge entre as duas saídas.")
    if ID_COLUMN not in sampled_analysis or TARGET_COLUMN not in sampled_analysis:
        raise AssertionError("A base de análise precisa preservar SK_ID_CURR e TARGET.")
    if ID_COLUMN in sampled_complete or TARGET_COLUMN in sampled_complete:
        raise AssertionError("A base completa não pode expor SK_ID_CURR ou TARGET.")
    if not sampled_analysis[ID_COLUMN].is_unique:
        raise AssertionError("A seleção contém SK_ID_CURR duplicado.")

    source_positions = sampled_analysis[ROW_ID].to_numpy(dtype=np.int64) - 1
    if (source_positions < 0).any() or (source_positions >= len(source)).any():
        raise AssertionError("ROW_ID_AMOSTRA aponta para posição inexistente na origem.")

    expected = source.iloc[source_positions].reset_index(drop=True)
    actual = sampled_analysis.drop(columns=[ROW_ID]).reset_index(drop=True)
    pd.testing.assert_frame_equal(actual, expected, check_dtype=True, check_exact=True)


def main() -> None:
    args = parse_args()
    input_path = args.entrada.expanduser().resolve()
    output_dir = args.saida_dir.expanduser().resolve()
    complete_path, analysis_path, metadata_path = validate_paths(
        input_path, output_dir, args.sobrescrever
    )

    source = pd.read_csv(input_path, sep=SEP, low_memory=False)
    if len(source) < SAMPLE_SIZE:
        raise ValueError(
            f"A base possui {len(source)} registros; são necessários pelo menos {SAMPLE_SIZE}."
        )
    required = [column for column in (ID_COLUMN, TARGET_COLUMN) if column not in source]
    if required:
        raise KeyError("Colunas obrigatórias ausentes: " + ", ".join(required))
    if ROW_ID in source:
        raise KeyError(f"A origem já contém a coluna reservada {ROW_ID}.")

    traceable_source = source.copy()
    traceable_source.insert(0, ROW_ID, np.arange(1, len(source) + 1, dtype=np.int64))
    sampled_analysis = traceable_source.sample(
        n=SAMPLE_SIZE,
        replace=False,
        random_state=SEED,
    ).reset_index(drop=True)
    sampled_complete = sampled_analysis.drop(columns=[ID_COLUMN, TARGET_COLUMN]).copy()

    validate_frames(source, sampled_analysis, sampled_complete)
    write_csv_atomic(sampled_complete, complete_path)
    write_csv_atomic(sampled_analysis, analysis_path)

    reloaded_complete = pd.read_csv(complete_path, sep=SEP, low_memory=False)
    reloaded_analysis = pd.read_csv(analysis_path, sep=SEP, low_memory=False)
    validate_frames(source, reloaded_analysis, reloaded_complete)

    generated_at = datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(timespec="seconds")
    metadata: dict[str, object] = {
        "etapa": 2,
        "descricao": "Amostra aleatória, reproduzível e rastreável de 10.000 registros.",
        "generated_at": generated_at,
        "timezone": "America/Sao_Paulo",
        "seed": SEED,
        "random_state": SEED,
        "sample_size": SAMPLE_SIZE,
        "sampling_without_replacement": True,
        "csv_separator": SEP,
        "row_id": {
            "column": ROW_ID,
            "semantics": "Posição 1-based do registro na base de origem, sem contar o cabeçalho.",
            "unique": True,
            "minimum_sampled": int(sampled_analysis[ROW_ID].min()),
            "maximum_sampled": int(sampled_analysis[ROW_ID].max()),
        },
        "source": {
            "path": str(input_path),
            "rows": int(len(source)),
            "columns": int(len(source.columns)),
            "size_bytes": input_path.stat().st_size,
            "sha256": sha256_file(input_path),
        },
        "outputs": {
            "complete": {
                "path": str(complete_path),
                "rows": int(len(sampled_complete)),
                "columns": int(len(sampled_complete.columns)),
                "contains_SK_ID_CURR": False,
                "contains_TARGET": False,
                "sha256": sha256_file(complete_path),
            },
            "analysis": {
                "path": str(analysis_path),
                "rows": int(len(sampled_analysis)),
                "columns": int(len(sampled_analysis.columns)),
                "contains_SK_ID_CURR": True,
                "contains_TARGET": True,
                "sha256": sha256_file(analysis_path),
            },
        },
        "validations": {
            "exactly_10000_rows": True,
            "row_id_unique": True,
            "same_order_in_both_outputs": True,
            "records_match_source_by_row_id": True,
            "sampled_SK_ID_CURR_unique": True,
            "protected_columns_only_in_analysis": True,
        },
    }
    write_json_atomic(metadata, metadata_path)

    print("Amostra criada e validada com sucesso.")
    print(f"Origem: {input_path}")
    print(f"Registros: {SAMPLE_SIZE}")
    print(f"Seed: {SEED}")
    print(f"Base completa: {complete_path}")
    print(f"Base de análise: {analysis_path}")
    print(f"Metadados: {metadata_path}")


if __name__ == "__main__":
    main()
