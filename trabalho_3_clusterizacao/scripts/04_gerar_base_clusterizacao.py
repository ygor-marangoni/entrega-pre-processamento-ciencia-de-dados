#!/usr/bin/env python3
"""Gera a base ponderada da tentativa 01 seguindo a lógica do p1.py.

Regras aplicadas:
- peso 0 excluiria o atributo;
- nominal permanece nominal e não é multiplicado pela raiz do peso;
- numérico recebe Min-Max e é multiplicado por sqrt(peso);
- SK_ID_CURR, TARGET e ROW_ID_AMOSTRA nunca entram na saída.

A ordem é vinculada à base auxiliar da Etapa 2 por um hash da sequência de
ROW_ID_AMOSTRA armazenado nos metadados.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd


SEP = ";"
ROW_ID = "ROW_ID_AMOSTRA"
ID_COLUMN = "SK_ID_CURR"
TARGET_COLUMN = "TARGET"
PROTECTED_COLUMNS = {ROW_ID, ID_COLUMN, TARGET_COLUMN}

SCRIPT_DIR = Path(__file__).resolve().parent
TRABALHO_3_DIR = SCRIPT_DIR.parent
REPOSITORY_ROOT = TRABALHO_3_DIR.parent
DEFAULT_INPUT = TRABALHO_3_DIR / "data" / "amostras" / "base_amostra_10000_analise.csv"
DEFAULT_DICTIONARY = (
    REPOSITORY_ROOT
    / "trabalho_1_preprocessamento"
    / "data"
    / "dicionario_codificacao_categorias.csv"
)
DEFAULT_PREPARED_DIR = TRABALHO_3_DIR / "data" / "preparadas"
DEFAULT_CONFIG_DIR = TRABALHO_3_DIR / "resultados" / "configuracoes"

OUTPUT_FILENAME = "base_clusterizacao_tentativa_01.csv"
CONFIG_FILENAME = "configuracao_tentativa_01.csv"
METADATA_FILENAME = "metadados_tentativa_01.json"

APPROVED_CONFIGURATION = [
    {
        "atributo": "AMT_CREDIT",
        "tipo": "Numérico",
        "peso": 6,
        "justificativa": "Captura o porte do empréstimo e diferencia necessidades de crédito.",
    },
    {
        "atributo": "CNT_CHILDREN",
        "tipo": "Numérico",
        "peso": 4,
        "justificativa": "Acrescenta composição familiar e potencial necessidade de mobilidade.",
    },
    {
        "atributo": "FLAG_OWN_CAR_COD",
        "tipo": "Nominal",
        "peso": 1,
        "justificativa": "Separa clientes com e sem veículo, preservando a natureza nominal.",
    },
    {
        "atributo": "AGE_YEARS",
        "tipo": "Numérico",
        "peso": 5,
        "justificativa": "Distingue estágios de vida com boa interpretação comercial.",
    },
    {
        "atributo": "CREDIT_INCOME_RATIO",
        "tipo": "Numérico",
        "peso": 7,
        "justificativa": "Resume o crédito em relação à renda, com peso controlado por ser derivado.",
    },
    {
        "atributo": "SER_CREDITOS_ATIVOS",
        "tipo": "Numérico",
        "peso": 5,
        "justificativa": "Representa a intensidade do histórico externo de crédito.",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera a base ponderada da tentativa 01 para clusterização."
    )
    parser.add_argument("--entrada", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--dicionario", type=Path, default=DEFAULT_DICTIONARY)
    parser.add_argument("--preparadas-dir", type=Path, default=DEFAULT_PREPARED_DIR)
    parser.add_argument("--configuracoes-dir", type=Path, default=DEFAULT_CONFIG_DIR)
    parser.add_argument(
        "--sobrescrever",
        action="store_true",
        help="Permite substituir somente os arquivos da tentativa 01 após validação.",
    )
    return parser.parse_args()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def row_sequence_hash(row_ids: pd.Series) -> str:
    payload = "\n".join(str(int(value)) for value in row_ids).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


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


def load_car_mapping(dictionary_path: Path) -> dict[int, str]:
    if not dictionary_path.is_file():
        raise FileNotFoundError(f"Dicionário não encontrado: {dictionary_path}")
    dictionary = pd.read_csv(dictionary_path, sep=SEP)
    subset = dictionary[dictionary["CAMPO_ORIGINAL"] == "FLAG_OWN_CAR"]
    mapping = {int(row.CODIGO): str(row.CATEGORIA) for row in subset.itertuples(index=False)}
    if mapping != {0: "N", 1: "Y"}:
        raise ValueError(f"Mapeamento inesperado de FLAG_OWN_CAR: {mapping}")
    return mapping


def transform_data(
    source: pd.DataFrame,
    car_mapping: dict[int, str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    prepared = pd.DataFrame(index=source.index)
    config_records: list[dict[str, object]] = []

    for item in APPROVED_CONFIGURATION:
        attribute = str(item["atributo"])
        kind = str(item["tipo"])
        weight = int(item["peso"])
        if weight == 0:
            continue
        root_weight = math.sqrt(weight)
        original = source[attribute]
        original_missing = int(original.isna().sum())

        if kind == "Numérico":
            numeric = pd.to_numeric(original, errors="coerce")
            coerced_missing = int(numeric.isna().sum())
            median = float(numeric.median())
            treated = numeric.fillna(median)
            minimum = float(treated.min())
            maximum = float(treated.max())
            if maximum != minimum:
                scaled = (treated - minimum) / (maximum - minimum)
            else:
                scaled = pd.Series(0.0, index=treated.index)
            prepared[attribute] = scaled.astype(float) * root_weight
            missing_treatment = (
                f"Mediana ({median:.12g}) se ausente; nenhum valor alterado."
                if coerced_missing == 0
                else f"Mediana ({median:.12g}); {coerced_missing} valores tratados."
            )
            final_scale = f"[0, sqrt({weight})] = [0, {root_weight:.12g}]"
            root_applied = True
            final_unique = int(prepared[attribute].nunique(dropna=True))
        elif kind == "Nominal":
            codes = pd.to_numeric(original, errors="coerce")
            labels = codes.map(car_mapping)
            unknown = labels.isna() & codes.notna()
            if unknown.any():
                values = sorted(codes[unknown].unique().tolist())
                raise ValueError(f"Códigos nominais desconhecidos em {attribute}: {values}")
            mode = labels.mode().iloc[0]
            prepared[attribute] = labels.fillna(mode).astype(str)
            minimum = float(codes.min())
            maximum = float(codes.max())
            missing_treatment = (
                f"Moda nominal ({mode}) se ausente; nenhum valor alterado."
                if int(labels.isna().sum()) == 0
                else f"Moda nominal ({mode}); {int(labels.isna().sum())} valores tratados."
            )
            final_scale = "Nominal {N,Y}; preservado sem multiplicação pela raiz do peso."
            root_applied = False
            final_unique = int(prepared[attribute].nunique(dropna=True))
        else:
            raise ValueError(f"Tipo não implementado na tentativa 01: {kind}")

        config_records.append(
            {
                "atributo": attribute,
                "tipo": kind,
                "peso": weight,
                "raiz_peso": root_weight,
                "raiz_peso_aplicada": root_applied,
                "minimo_original": minimum,
                "maximo_original": maximum,
                "ausentes_originais": original_missing,
                "tratamento_ausentes": missing_treatment,
                "justificativa": item["justificativa"],
                "escala_final": final_scale,
                "valores_unicos_finais": final_unique,
            }
        )

    return prepared, pd.DataFrame(config_records)


def validate_prepared(source: pd.DataFrame, prepared: pd.DataFrame) -> None:
    expected_columns = [str(item["atributo"]) for item in APPROVED_CONFIGURATION]
    if len(prepared) != 10_000:
        raise AssertionError(f"Esperados 10.000 registros; encontrados {len(prepared)}.")
    if prepared.columns.tolist() != expected_columns:
        raise AssertionError("A ordem ou seleção dos atributos está incorreta.")
    if PROTECTED_COLUMNS.intersection(prepared.columns):
        raise AssertionError("Uma coluna protegida entrou na base de clusterização.")
    if prepared.isna().any().any():
        raise AssertionError("A base preparada contém valores ausentes.")
    if prepared.columns[prepared.isna().all()].tolist():
        raise AssertionError("A base preparada contém coluna totalmente vazia.")
    if not source.index.equals(prepared.index):
        raise AssertionError("A ordem dos registros foi alterada durante a transformação.")

    for item in APPROVED_CONFIGURATION:
        attribute = str(item["atributo"])
        if item["tipo"] == "Numérico":
            root_weight = math.sqrt(int(item["peso"]))
            series = pd.to_numeric(prepared[attribute], errors="raise")
            if series.min() < -1e-12 or series.max() > root_weight + 1e-12:
                raise AssertionError(f"Escala inesperada em {attribute}.")
        else:
            if set(prepared[attribute].unique()) != {"N", "Y"}:
                raise AssertionError(f"Categorias inesperadas em {attribute}.")


def main() -> None:
    args = parse_args()
    input_path = args.entrada.expanduser().resolve()
    dictionary_path = args.dicionario.expanduser().resolve()
    prepared_dir = args.preparadas_dir.expanduser().resolve()
    config_dir = args.configuracoes_dir.expanduser().resolve()
    output_path = prepared_dir / OUTPUT_FILENAME
    config_path = config_dir / CONFIG_FILENAME
    metadata_path = config_dir / METADATA_FILENAME

    if not input_path.is_file():
        raise FileNotFoundError(f"Base auxiliar da Etapa 2 não encontrada: {input_path}")
    existing = [path for path in (output_path, config_path, metadata_path) if path.exists()]
    if existing and not args.sobrescrever:
        names = ", ".join(path.name for path in existing)
        raise FileExistsError(
            f"Arquivos da tentativa 01 já existem: {names}. Use --sobrescrever após conferência."
        )

    source = pd.read_csv(input_path, sep=SEP, low_memory=False)
    required = PROTECTED_COLUMNS | {
        str(item["atributo"]) for item in APPROVED_CONFIGURATION
    }
    missing = sorted(required.difference(source.columns))
    if missing:
        raise KeyError("Colunas obrigatórias ausentes: " + ", ".join(missing))
    if len(source) != 10_000:
        raise ValueError(f"A base auxiliar deveria ter 10.000 registros; possui {len(source)}.")
    if not source[ROW_ID].is_unique or not source[ID_COLUMN].is_unique:
        raise ValueError("ROW_ID_AMOSTRA e SK_ID_CURR precisam ser únicos.")

    prepared_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)
    car_mapping = load_car_mapping(dictionary_path)
    prepared, configuration = transform_data(source, car_mapping)
    validate_prepared(source, prepared)
    write_csv_atomic(prepared, output_path)
    write_csv_atomic(configuration, config_path)

    reloaded = pd.read_csv(output_path, sep=SEP, low_memory=False)
    validate_prepared(source, reloaded)
    for item in APPROVED_CONFIGURATION:
        attribute = str(item["atributo"])
        if item["tipo"] == "Numérico":
            if not np.allclose(
                prepared[attribute].to_numpy(),
                reloaded[attribute].to_numpy(),
                rtol=1e-12,
                atol=1e-12,
            ):
                raise AssertionError(f"Valores divergiram após gravar {attribute}.")
        elif prepared[attribute].tolist() != reloaded[attribute].tolist():
            raise AssertionError(f"Categorias divergiram após gravar {attribute}.")

    metadata: dict[str, object] = {
        "etapa": 4,
        "tentativa": 1,
        "generated_at": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(
            timespec="seconds"
        ),
        "timezone": "America/Sao_Paulo",
        "csv_separator": SEP,
        "logic_reference": "trabalho_3_clusterizacao/scripts/originais/p1.py",
        "approved_configuration_source": "trabalho_3_clusterizacao/resultados/exploracao/analise_atributos.md",
        "auxiliary_analysis_base": {
            "path": str(input_path),
            "sha256": sha256_file(input_path),
            "rows": int(len(source)),
            "columns": int(len(source.columns)),
            "row_id_sequence_sha256": row_sequence_hash(source[ROW_ID]),
            "SK_ID_CURR_preserved": True,
            "TARGET_preserved": True,
        },
        "output": {
            "path": str(output_path),
            "sha256": sha256_file(output_path),
            "rows": int(len(reloaded)),
            "columns": int(len(reloaded.columns)),
            "column_names": reloaded.columns.tolist(),
        },
        "configuration_file": {
            "path": str(config_path),
            "sha256": sha256_file(config_path),
        },
        "missing_values_policy": {
            "numeric": "Imputação pela mediana somente se necessário.",
            "nominal": "Imputação pela moda somente se necessário.",
            "values_actually_imputed": int(configuration["ausentes_originais"].sum()),
        },
        "nominal_policy": {
            "FLAG_OWN_CAR_COD": "Códigos 0/1 recuperados como N/Y e preservados como nominais.",
            "weight_behavior": "Como no p1.py original, peso nominal > 0 inclui o campo, mas sqrt(peso) não é aplicado.",
        },
        "validations": {
            "exactly_10000_rows": True,
            "only_approved_attributes": True,
            "no_SK_ID_CURR": True,
            "no_TARGET": True,
            "no_ROW_ID_AMOSTRA": True,
            "no_missing_values": True,
            "no_empty_columns": True,
            "numeric_ranges_valid": True,
            "nominal_values_valid": True,
            "order_preserved_by_source_index": True,
            "order_traceable_by_row_id_sequence_hash": True,
        },
        "hopkins_executed": False,
    }
    write_json_atomic(metadata, metadata_path)

    print("Base ponderada da tentativa 01 criada e validada.")
    print(f"Registros: {len(reloaded)}")
    print(f"Atributos: {len(reloaded.columns)}")
    print(f"Base: {output_path}")
    print(f"Configuração: {config_path}")
    print(f"Metadados: {metadata_path}")
    print("Hopkins executado: não")


if __name__ == "__main__":
    main()
