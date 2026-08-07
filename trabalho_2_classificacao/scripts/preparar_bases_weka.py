#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepara a base do Trabalho 1 para uso no WEKA no Trabalho 2.

Entrada principal:
- trabalho_1_preprocessamento/data/base_final_preprocessada.csv.

Saidas:
- trabalho_2_classificacao/data/base_weka_completa.csv
- trabalho_2_classificacao/data/base_weka_completa.arff

Tambem expoe funcoes reutilizadas por outros scripts para gerar a base reduzida.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import pandas as pd


SEP = ";"
TARGET_COL = "TARGET"
ID_COL = "SK_ID_CURR"
RELATION_NAME = "risco_credito"

SCRIPT_DIR = Path(__file__).resolve().parent
TRABALHO_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = TRABALHO_DIR.parent
DATA_DIR = TRABALHO_DIR / "data"

DEFAULT_INPUT = PROJECT_ROOT / "trabalho_1_preprocessamento" / "data" / "base_final_preprocessada.csv"
DEFAULT_COMPLETE_CSV = DATA_DIR / "base_weka_completa.csv"
DEFAULT_COMPLETE_ARFF = DATA_DIR / "base_weka_completa.arff"
DEFAULT_REDUCED_CSV = DATA_DIR / "base_weka_reduzida.csv"
DEFAULT_REDUCED_ARFF = DATA_DIR / "base_weka_reduzida.arff"


def normalize_target(value: object) -> str:
    """Converte a classe para os rotulos nominais esperados pelo WEKA."""
    if pd.isna(value):
        raise ValueError("A coluna TARGET possui valor ausente. Corrija a base antes de gerar o ARFF.")
    text = str(value).strip()
    if text in {"0", "0.0"}:
        return "0"
    if text in {"1", "1.0"}:
        return "1"
    raise ValueError(f"Valor invalido em TARGET: {value!r}. Esperado apenas 0 ou 1.")


def quote_arff_name(name: str) -> str:
    """Aspas simples evitam problemas caso o atributo contenha caracteres especiais."""
    return "'" + str(name).replace("\\", "\\\\").replace("'", "\\'") + "'"


def format_arff_value(value: object, is_target: bool = False) -> str:
    if pd.isna(value):
        return "?"
    if is_target:
        return normalize_target(value)
    if isinstance(value, str):
        text = value.strip()
        if text == "":
            return "?"
        if re.fullmatch(r"[-+]?\d+(\.\d+)?([eE][-+]?\d+)?", text):
            return text
        return quote_arff_name(text)
    return str(value)


def load_base(input_path: Path) -> pd.DataFrame:
    if not input_path.exists():
        raise FileNotFoundError(
            f"Base nao encontrada: {input_path}. Rode primeiro o Trabalho 1 ou confira o caminho informado."
        )

    df = pd.read_csv(input_path, sep=SEP, low_memory=False)
    if TARGET_COL not in df.columns:
        raise KeyError(f"A coluna obrigatoria {TARGET_COL!r} nao foi encontrada na base.")

    if ID_COL in df.columns:
        df = df.drop(columns=[ID_COL])

    df[TARGET_COL] = df[TARGET_COL].map(normalize_target)
    ordered_cols = [col for col in df.columns if col != TARGET_COL] + [TARGET_COL]
    df = df.loc[:, ordered_cols].copy()
    return df


def save_csv_for_weka(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, sep=SEP, index=False, encoding="utf-8", lineterminator="\n")


def write_arff(df: pd.DataFrame, output_path: Path, relation_name: str = RELATION_NAME) -> None:
    if TARGET_COL not in df.columns:
        raise KeyError(f"A coluna {TARGET_COL!r} precisa estar presente para gerar o ARFF.")
    if list(df.columns)[-1] != TARGET_COL:
        df = df.loc[:, [col for col in df.columns if col != TARGET_COL] + [TARGET_COL]].copy()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        f.write(f"@RELATION {relation_name}\n\n")
        for col in df.columns:
            if col == TARGET_COL:
                f.write(f"@ATTRIBUTE {quote_arff_name(col)} {{0,1}}\n")
            else:
                f.write(f"@ATTRIBUTE {quote_arff_name(col)} NUMERIC\n")
        f.write("\n@DATA\n")

        writer = csv.writer(f, lineterminator="\n")
        for row in df.itertuples(index=False, name=None):
            values = [
                format_arff_value(value, is_target=(col == TARGET_COL))
                for col, value in zip(df.columns, row)
            ]
            writer.writerow(values)


def prepare_complete_base(input_path: Path = DEFAULT_INPUT) -> pd.DataFrame:
    df = load_base(input_path)
    save_csv_for_weka(df, DEFAULT_COMPLETE_CSV)
    write_arff(df, DEFAULT_COMPLETE_ARFF)
    return df


def prepare_reduced_base(attributes: list[str], input_csv: Path = DEFAULT_COMPLETE_CSV) -> pd.DataFrame:
    if not attributes:
        raise ValueError("Nenhum atributo relevante foi informado para gerar a base reduzida.")
    if not input_csv.exists():
        raise FileNotFoundError(f"Base completa do WEKA nao encontrada: {input_csv}")

    df = pd.read_csv(input_csv, sep=SEP, low_memory=False)
    missing = [attr for attr in attributes if attr not in df.columns]
    if missing:
        raise KeyError("Atributos ausentes na base completa: " + ", ".join(missing))

    reduced = df.loc[:, attributes + [TARGET_COL]].copy()
    save_csv_for_weka(reduced, DEFAULT_REDUCED_CSV)
    write_arff(reduced, DEFAULT_REDUCED_ARFF)
    return reduced


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepara CSV e ARFF para classificacao no WEKA.")
    parser.add_argument(
        "--entrada",
        type=Path,
        default=DEFAULT_INPUT,
        help="Caminho para base_final_preprocessada.csv. Padrao: pasta data do Trabalho 1.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = prepare_complete_base(args.entrada.resolve())
    print("Base completa preparada para o WEKA.")
    print(f"Linhas: {len(df)}")
    print(f"Colunas de entrada: {len(df.columns) - 1}")
    print(f"Classe: {TARGET_COL}")
    print(f"CSV: {DEFAULT_COMPLETE_CSV}")
    print(f"ARFF: {DEFAULT_COMPLETE_ARFF}")


if __name__ == "__main__":
    main()
