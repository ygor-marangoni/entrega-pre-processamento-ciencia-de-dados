#!/usr/bin/env python3
"""Converte a base final ponderada da Etapa 6 para ARFF compatível com o WEKA.

A conversão preserva a ordem das linhas e dos atributos, declara atributos
numéricos como ``numeric`` e atributos nominais com suas categorias explícitas.
Colunas de identificação e TARGET são rejeitadas caso apareçam na entrada.
"""

from __future__ import annotations

import argparse
import hashlib
import math
import os
import re
from pathlib import Path

import pandas as pd


SEP = ";"
PROTECTED_COLUMNS = {"SK_ID_CURR", "TARGET", "ROW_ID_AMOSTRA"}
RELATION_NAME = "base_clusterizacao_final"

SCRIPT_DIR = Path(__file__).resolve().parent
TRABALHO_3_DIR = SCRIPT_DIR.parent
DEFAULT_INPUT = TRABALHO_3_DIR / "data" / "preparadas" / "base_clusterizacao_final.csv"
DEFAULT_CONFIG = TRABALHO_3_DIR / "resultados" / "configuracoes" / "configuracao_final.csv"
DEFAULT_OUTPUT = TRABALHO_3_DIR / "data" / "preparadas" / "base_clusterizacao_final.arff"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Converte a base ponderada final para ARFF compatível com o WEKA."
    )
    parser.add_argument("--entrada", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--configuracao", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--saida", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--sobrescrever",
        action="store_true",
        help="Permite substituir o ARFF existente após validação explícita.",
    )
    return parser.parse_args()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def quote_arff_name(value: str) -> str:
    """Usa identificador simples quando seguro; caso contrário, aplica aspas."""
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        return value
    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def quote_nominal_value(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_+\-.]+", value) and value != "?":
        return value
    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def format_numeric(value: object) -> str:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"Valor numérico não finito encontrado: {value!r}")
    return format(number, ".17g")


def load_and_validate(
    input_path: Path, config_path: Path
) -> tuple[pd.DataFrame, list[tuple[str, str, list[str]]]]:
    if not input_path.is_file():
        raise FileNotFoundError(f"Base final não encontrada: {input_path}")
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuração final não encontrada: {config_path}")

    base = pd.read_csv(input_path, sep=SEP, low_memory=False)
    config = pd.read_csv(config_path, sep=SEP, low_memory=False)
    required_config = {"atributo", "tipo", "peso"}
    missing_config = sorted(required_config.difference(config.columns))
    if missing_config:
        raise KeyError("Colunas ausentes na configuração: " + ", ".join(missing_config))
    config = config[pd.to_numeric(config["peso"], errors="raise") > 0].copy()

    if len(base) != 10_000:
        raise ValueError(f"Esperados 10.000 registros; encontrados {len(base)}.")
    if base.columns.duplicated().any():
        raise ValueError("A base contém nomes de atributos duplicados.")
    protected = sorted(PROTECTED_COLUMNS.intersection(base.columns))
    if protected:
        raise ValueError("Colunas protegidas encontradas na base: " + ", ".join(protected))
    if base.empty or len(base.columns) == 0:
        raise ValueError("A base de entrada está vazia.")
    if base.isna().any().any():
        raise ValueError("A base contém valores ausentes; a Etapa 4 deveria tê-los tratado.")
    if base.columns[base.isna().all()].tolist():
        raise ValueError("A base contém coluna totalmente vazia.")

    configured_columns = config["atributo"].astype(str).tolist()
    if configured_columns != base.columns.tolist():
        raise ValueError(
            "A ordem ou o conjunto de atributos da configuração final diverge da base final."
        )

    schema: list[tuple[str, str, list[str]]] = []
    for row in config.itertuples(index=False):
        attribute = str(row.atributo)
        kind = str(row.tipo).strip().casefold()
        if kind in {"numérico", "numerico", "ordinal"}:
            numeric = pd.to_numeric(base[attribute], errors="raise")
            if not numeric.map(math.isfinite).all():
                raise ValueError(f"O atributo {attribute} contém valor não finito.")
            base[attribute] = numeric.astype(float)
            schema.append((attribute, "numeric", []))
        elif kind == "nominal":
            values = base[attribute].astype(str)
            categories = sorted(values.unique().tolist())
            if not categories or any(value in {"", "?"} for value in categories):
                raise ValueError(f"Categorias inválidas no atributo nominal {attribute}.")
            base[attribute] = values
            schema.append((attribute, "nominal", categories))
        else:
            raise ValueError(f"Tipo não suportado na configuração: {row.tipo!r}")
    return base, schema


def build_arff(base: pd.DataFrame, schema: list[tuple[str, str, list[str]]]) -> str:
    lines = [f"@relation {quote_arff_name(RELATION_NAME)}", ""]
    for attribute, kind, categories in schema:
        if kind == "numeric":
            declaration = "numeric"
        else:
            declaration = "{" + ",".join(quote_nominal_value(v) for v in categories) + "}"
        lines.append(f"@attribute {quote_arff_name(attribute)} {declaration}")
    lines.extend(("", "@data"))

    for row in base.itertuples(index=False, name=None):
        values: list[str] = []
        for value, (_, kind, _) in zip(row, schema, strict=True):
            values.append(format_numeric(value) if kind == "numeric" else quote_nominal_value(str(value)))
        lines.append(",".join(values))
    return "\n".join(lines) + "\n"


def validate_written_arff(
    path: Path, expected_rows: int, schema: list[tuple[str, str, list[str]]]
) -> None:
    text = path.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("%")]
    relation_lines = [line for line in lines if line.casefold().startswith("@relation ")]
    attribute_lines = [line for line in lines if line.casefold().startswith("@attribute ")]
    data_positions = [i for i, line in enumerate(lines) if line.casefold() == "@data"]
    if len(relation_lines) != 1:
        raise AssertionError("O ARFF deve possuir exatamente uma declaração @relation.")
    if len(attribute_lines) != len(schema):
        raise AssertionError("Quantidade de atributos divergente no ARFF gravado.")
    if len(data_positions) != 1:
        raise AssertionError("O ARFF deve possuir exatamente uma seção @data.")
    data_lines = lines[data_positions[0] + 1 :]
    if len(data_lines) != expected_rows:
        raise AssertionError(
            f"Esperados {expected_rows} registros no ARFF; encontrados {len(data_lines)}."
        )
    for line_number, line in enumerate(data_lines, start=1):
        if len(line.split(",")) != len(schema):
            raise AssertionError(f"Registro ARFF {line_number} possui quantidade incorreta de valores.")


def main() -> None:
    args = parse_args()
    input_path = args.entrada.expanduser().resolve()
    config_path = args.configuracao.expanduser().resolve()
    output_path = args.saida.expanduser().resolve()
    if output_path.exists() and not args.sobrescrever:
        raise FileExistsError(
            f"O arquivo já existe: {output_path}. Use --sobrescrever somente após conferência."
        )

    base, schema = load_and_validate(input_path, config_path)
    payload = build_arff(base, schema)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_name(output_path.name + ".tmp")
    try:
        temporary.write_text(payload, encoding="utf-8", newline="\n")
        os.replace(temporary, output_path)
    finally:
        temporary.unlink(missing_ok=True)

    validate_written_arff(output_path, len(base), schema)
    numeric_count = sum(kind == "numeric" for _, kind, _ in schema)
    nominal_count = sum(kind == "nominal" for _, kind, _ in schema)
    print("ARFF da configuração final criado e validado.")
    print(f"Registros: {len(base)}")
    print(f"Atributos: {len(schema)} ({numeric_count} numeric, {nominal_count} nominal)")
    print(f"SHA-256 da entrada: {sha256_file(input_path)}")
    print(f"SHA-256 do ARFF: {sha256_file(output_path)}")
    print(f"Saída: {output_path}")


if __name__ == "__main__":
    main()
