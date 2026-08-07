#!/usr/bin/env python3
"""Calcula a Estatística de Hopkins da tentativa 01.

A implementação preserva a lógica do p2.py original e acrescenta seed explícita
à geração dos registros virtuais. Nenhum campo ou peso é alterado neste script.
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
import sklearn
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder


SEP = ";"
SEED = 42
MAX_BASE_SIZE = 10_000
SAMPLE_PERCENTAGE = 0.01
THRESHOLD = 0.7

SCRIPT_DIR = Path(__file__).resolve().parent
TRABALHO_3_DIR = SCRIPT_DIR.parent
DEFAULT_INPUT = TRABALHO_3_DIR / "data" / "preparadas" / "base_clusterizacao_tentativa_01.csv"
DEFAULT_CONFIG = TRABALHO_3_DIR / "resultados" / "configuracoes" / "configuracao_tentativa_01.csv"
DEFAULT_METADATA = TRABALHO_3_DIR / "resultados" / "configuracoes" / "metadados_tentativa_01.json"
DEFAULT_OUTPUT_DIR = TRABALHO_3_DIR / "resultados" / "hopkins"
CSV_FILENAME = "hopkins_tentativa_01.csv"
TXT_FILENAME = "hopkins_tentativa_01.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calcula Hopkins para a base ponderada da tentativa 01."
    )
    parser.add_argument("--entrada", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--configuracao", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--metadados", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--saida-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--sobrescrever",
        action="store_true",
        help="Permite substituir somente os resultados da tentativa 01.",
    )
    return parser.parse_args()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv_atomic(df: pd.DataFrame, path: Path) -> None:
    temporary = path.with_name(path.name + ".tmp")
    try:
        df.to_csv(temporary, sep=SEP, index=False, encoding="utf-8", lineterminator="\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def write_text_atomic(text: str, path: Path) -> None:
    temporary = path.with_name(path.name + ".tmp")
    try:
        temporary.write_text(text, encoding="utf-8")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def prepare_mixed_matrix(
    base: pd.DataFrame,
    real: pd.DataFrame,
    virtual: pd.DataFrame,
    numeric_columns: list[str],
    nominal_columns: list[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    numeric_base = base[numeric_columns].to_numpy(dtype=float) if numeric_columns else np.empty((len(base), 0))
    numeric_real = real[numeric_columns].to_numpy(dtype=float) if numeric_columns else np.empty((len(real), 0))
    numeric_virtual = virtual[numeric_columns].to_numpy(dtype=float) if numeric_columns else np.empty((len(virtual), 0))

    encoded_nominal_columns = 0
    if nominal_columns:
        encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        encoder.fit(base[nominal_columns])
        scale = 1.0 / np.sqrt(2.0)
        nominal_base = encoder.transform(base[nominal_columns]) * scale
        nominal_real = encoder.transform(real[nominal_columns]) * scale
        nominal_virtual = encoder.transform(virtual[nominal_columns]) * scale
        encoded_nominal_columns = int(nominal_base.shape[1])
        matrix_base = np.hstack((numeric_base, nominal_base))
        matrix_real = np.hstack((numeric_real, nominal_real))
        matrix_virtual = np.hstack((numeric_virtual, nominal_virtual))
    else:
        matrix_base = numeric_base
        matrix_real = numeric_real
        matrix_virtual = numeric_virtual

    if matrix_base.shape[1] == 0:
        raise ValueError("Nenhuma coluna válida para calcular Hopkins.")
    if not np.isfinite(matrix_base).all() or not np.isfinite(matrix_virtual).all():
        raise ValueError("A matriz de distância contém valor não finito.")
    return matrix_base, matrix_real, matrix_virtual, encoded_nominal_columns


def calculate_hopkins(df: pd.DataFrame) -> dict[str, object]:
    if len(df) > MAX_BASE_SIZE:
        base = df.sample(n=MAX_BASE_SIZE, random_state=SEED).copy()
    else:
        base = df.copy()
    base = base.reset_index(drop=True)
    base_size = len(base)
    real_virtual_size = max(1, int(base_size * SAMPLE_PERCENTAGE))

    numeric_columns = base.select_dtypes(include=[np.number]).columns.tolist()
    nominal_columns = base.select_dtypes(exclude=[np.number]).columns.tolist()
    real = base.sample(n=real_virtual_size, random_state=SEED).copy()

    rng = np.random.default_rng(SEED)
    virtual_data: dict[str, np.ndarray] = {}
    for column in base.columns:
        if column in numeric_columns:
            minimum = float(base[column].min())
            maximum = float(base[column].max())
            virtual_data[column] = rng.uniform(minimum, maximum, real_virtual_size)
        else:
            categories = base[column].dropna().unique()
            if len(categories) == 0:
                raise ValueError(f"A coluna nominal {column} não possui categoria válida.")
            virtual_data[column] = rng.choice(categories, real_virtual_size)
    virtual = pd.DataFrame(virtual_data, columns=base.columns)

    matrix_base, matrix_real, matrix_virtual, encoded_nominal_columns = prepare_mixed_matrix(
        base, real, virtual, numeric_columns, nominal_columns
    )

    # n_jobs=1 evita criação de filas/processos bloqueada em ambientes Windows
    # restritos; isso não altera vizinhos, distâncias ou o valor de Hopkins.
    nearest_virtual = NearestNeighbors(n_neighbors=1, metric="euclidean", n_jobs=1)
    nearest_virtual.fit(matrix_base)
    distances_u, _ = nearest_virtual.kneighbors(matrix_virtual)
    u = distances_u[:, 0]

    nearest_real = NearestNeighbors(n_neighbors=2, metric="euclidean", n_jobs=1)
    nearest_real.fit(matrix_base)
    distances_w, _ = nearest_real.kneighbors(matrix_real)
    w = distances_w[:, 1]

    sum_u = float(np.sum(u))
    sum_w = float(np.sum(w))
    hopkins = 0.5 if (sum_u + sum_w) == 0 else sum_u / (sum_u + sum_w)
    return {
        "hopkins": float(hopkins),
        "base_size": int(base_size),
        "real_size": int(len(real)),
        "virtual_size": int(len(virtual)),
        "numeric_columns": numeric_columns,
        "nominal_columns": nominal_columns,
        "encoded_dimensions": int(matrix_base.shape[1]),
        "encoded_nominal_columns": encoded_nominal_columns,
        "sum_u": sum_u,
        "sum_w": sum_w,
        "mean_u": float(np.mean(u)),
        "mean_w": float(np.mean(w)),
        "min_u": float(np.min(u)),
        "max_u": float(np.max(u)),
        "min_w": float(np.min(w)),
        "max_w": float(np.max(w)),
    }


def interpretation(hopkins: float) -> tuple[str, str]:
    if hopkins >= THRESHOLD:
        return (
            "APROVADA_PARA_PREPARACAO_WEKA",
            "H >= 0,7: a tentativa apresenta forte tendência de clusterização.",
        )
    if hopkins <= 0.3:
        return (
            "REVISAR_CONFIGURACAO",
            "H <= 0,3: os dados apresentam baixa tendência de clusterização e possível regularidade espacial.",
        )
    return (
        "REVISAR_CONFIGURACAO",
        "0,3 < H < 0,7: a tendência de clusterização não atingiu o limiar exigido pelo trabalho.",
    )


def main() -> None:
    args = parse_args()
    input_path = args.entrada.expanduser().resolve()
    config_path = args.configuracao.expanduser().resolve()
    metadata_path = args.metadados.expanduser().resolve()
    output_dir = args.saida_dir.expanduser().resolve()
    csv_path = output_dir / CSV_FILENAME
    txt_path = output_dir / TXT_FILENAME

    for required in (input_path, config_path, metadata_path):
        if not required.is_file():
            raise FileNotFoundError(f"Arquivo obrigatório não encontrado: {required}")
    existing = [path for path in (csv_path, txt_path) if path.exists()]
    if existing and not args.sobrescrever:
        names = ", ".join(path.name for path in existing)
        raise FileExistsError(
            f"Resultados Hopkins já existentes: {names}. Use --sobrescrever após conferência."
        )

    attempt_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if sha256_file(input_path) != attempt_metadata["output"]["sha256"]:
        raise ValueError("O hash da base preparada diverge dos metadados da Etapa 4.")
    if sha256_file(config_path) != attempt_metadata["configuration_file"]["sha256"]:
        raise ValueError("O hash da configuração diverge dos metadados da Etapa 4.")

    df = pd.read_csv(input_path, sep=SEP, low_memory=False)
    if len(df) != 10_000:
        raise ValueError(f"Esperados 10.000 registros; encontrados {len(df)}.")
    if df.isna().any().any():
        raise ValueError("A base preparada contém valores ausentes.")
    protected = {"SK_ID_CURR", "TARGET", "ROW_ID_AMOSTRA"}.intersection(df.columns)
    if protected:
        raise ValueError(f"Colunas protegidas encontradas: {sorted(protected)}")

    first = calculate_hopkins(df)
    second = calculate_hopkins(df)
    if first != second:
        raise AssertionError("Hopkins não foi reproduzível em duas execuções consecutivas.")

    hopkins = float(first["hopkins"])
    decision, text_interpretation = interpretation(hopkins)
    config = pd.read_csv(config_path, sep=SEP)
    attributes = df.columns.tolist()
    weights = " | ".join(
        f"{row.atributo}={int(row.peso)}" for row in config.itertuples(index=False)
    )
    generated_at = datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(timespec="seconds")

    result = {
        "tentativa": 1,
        "valor_hopkins": hopkins,
        "limiar_exigido": THRESHOLD,
        "decisao": decision,
        "interpretacao": text_interpretation,
        "quantidade_base_entrada": int(len(df)),
        "quantidade_base_hopkins": first["base_size"],
        "tamanho_amostra_real": first["real_size"],
        "tamanho_amostra_virtual": first["virtual_size"],
        "percentual_amostras": SAMPLE_PERCENTAGE * 100,
        "seed": SEED,
        "atributos": " | ".join(attributes),
        "atributos_numericos": " | ".join(first["numeric_columns"]),
        "atributos_nominais": " | ".join(first["nominal_columns"]),
        "pesos": weights,
        "dimensoes_apos_one_hot": first["encoded_dimensions"],
        "soma_distancias_virtuais_u": first["sum_u"],
        "soma_distancias_reais_w": first["sum_w"],
        "media_distancias_virtuais_u": first["mean_u"],
        "media_distancias_reais_w": first["mean_w"],
        "min_distancias_virtuais_u": first["min_u"],
        "max_distancias_virtuais_u": first["max_u"],
        "min_distancias_reais_w": first["min_w"],
        "max_distancias_reais_w": first["max_w"],
        "formula": "H = soma(u) / (soma(u) + soma(w))",
        "distancia": "Euclidiana mista; nominal one-hot multiplicado por 1/sqrt(2)",
        "geracao_virtual": "Uniforme entre mínimo e máximo nos numéricos; escolha uniforme das categorias nominais",
        "reproducivel_duas_execucoes": True,
        "hash_base_entrada": sha256_file(input_path),
        "hash_configuracao": sha256_file(config_path),
        "sklearn_version": sklearn.__version__,
        "generated_at": generated_at,
        "timezone": "America/Sao_Paulo",
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv_atomic(pd.DataFrame([result]), csv_path)
    report_lines = [
        "ESTATÍSTICA DE HOPKINS — TENTATIVA 01",
        "=" * 48,
        f"Data: {generated_at}",
        f"Base: {input_path}",
        f"Hash da base: {result['hash_base_entrada']}",
        f"Registros da base: {first['base_size']}",
        f"Amostra real: {first['real_size']}",
        f"Amostra virtual: {first['virtual_size']}",
        f"Seed: {SEED}",
        f"Atributos: {', '.join(attributes)}",
        f"Pesos: {weights}",
        f"Atributos numéricos: {', '.join(first['numeric_columns'])}",
        f"Atributos nominais: {', '.join(first['nominal_columns'])}",
        f"Dimensões após One-Hot: {first['encoded_dimensions']}",
        "",
        f"Soma u: {float(first['sum_u']):.12f}",
        f"Soma w: {float(first['sum_w']):.12f}",
        f"Média u: {float(first['mean_u']):.12f}",
        f"Média w: {float(first['mean_w']):.12f}",
        "",
        f"H = {hopkins:.12f}",
        f"Limiar: {THRESHOLD:.1f}",
        f"Decisão: {decision}",
        f"Interpretação: {text_interpretation}",
        "",
        "Reprodutibilidade: duas execuções consecutivas com seed 42 produziram resultados idênticos.",
        "Hopkins calculado pela lógica do p2.py, com seed acrescentada aos registros virtuais.",
    ]
    write_text_atomic("\n".join(report_lines) + "\n", txt_path)

    print("Hopkins da tentativa 01 calculado e validado.")
    print(f"H = {hopkins:.12f}")
    print(f"Decisão: {decision}")
    print(f"CSV: {csv_path}")
    print(f"TXT: {txt_path}")


if __name__ == "__main__":
    main()
