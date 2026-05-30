#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pré-processamento do trabalho de Ciência de Dados.

Entradas esperadas:
- emprestimos.csv
- serasa.csv
- emprestimos_anteriores.csv

Saídas:
- base_final_preprocessada.csv
- base_final_com_metrica.csv
- dicionario_codificacao_categorias.csv
- resumo_estatistico_preprocessamento.csv
- preprocessamento_credito.db

Este script usa Python, pandas e SQLite para permitir a reprodução do pré-processamento.
"""

import argparse
import json
import os
import sqlite3
from pathlib import Path
from typing import cast

import pandas as pd
import numpy as np

REQUIRED_INPUTS = ["emprestimos.csv", "serasa.csv", "emprestimos_anteriores.csv"]


def parse_args():
    parser = argparse.ArgumentParser(description="Pré-processamento de crédito.")
    parser.add_argument(
        "--base-dir",
        type=str,
        default=None,
        help="Diretório onde estão os arquivos de entrada (emprestimos.csv, serasa.csv e emprestimos_anteriores.csv).",
    )
    return parser.parse_args()


def resolve_base_dir(base_dir_arg=None):
    if base_dir_arg:
        base_path = Path(base_dir_arg).expanduser().resolve()
        if not base_path.exists():
            raise FileNotFoundError(f"Diretório informado não existe: {base_path}")
        if not base_path.is_dir():
            raise NotADirectoryError(f"Caminho informado não é um diretório: {base_path}")
        return base_path

    cwd = Path.cwd().resolve()
    for directory in [cwd, *cwd.parents]:
        required = [directory / filename for filename in REQUIRED_INPUTS]
        if all(path.exists() for path in required):
            return directory

    raise FileNotFoundError(
        "Arquivos de entrada não encontrados. Coloque os arquivos "
        f"{', '.join(REQUIRED_INPUTS)} no diretório atual ou informe --base-dir."
    )


BASE_DIR = "."
PATH_EMPRESTIMOS = os.path.join(BASE_DIR, "emprestimos.csv")
PATH_SERASA = os.path.join(BASE_DIR, "serasa.csv")
PATH_PREV = os.path.join(BASE_DIR, "emprestimos_anteriores.csv")

OUT_FINAL = os.path.join(BASE_DIR, "base_final_preprocessada.csv")
OUT_METRIC = os.path.join(BASE_DIR, "base_final_com_metrica.csv")
OUT_DICT = os.path.join(BASE_DIR, "dicionario_codificacao_categorias.csv")
OUT_SUMMARY = os.path.join(BASE_DIR, "resumo_estatistico_preprocessamento.csv")
OUT_JSON = os.path.join(BASE_DIR, "resumo_processamento.json")
OUT_DB = os.path.join(BASE_DIR, "preprocessamento_credito.db")

SEP = ";"

MAIN_COLS = [
    "SK_ID_CURR", "TARGET", "CODE_GENDER", "FLAG_OWN_CAR", "FLAG_OWN_REALTY",
    "CNT_CHILDREN", "AMT_INCOME_TOTAL", "AMT_CREDIT", "NAME_INCOME_TYPE",
    "NAME_EDUCATION_TYPE", "NAME_FAMILY_STATUS", "NAME_HOUSING_TYPE", "DAYS_BIRTH",
    "FLAG_MOBIL", "FLAG_EMP_PHONE", "FLAG_EMAIL", "OCCUPATION_TYPE",
    "REGION_RATING_CLIENT", "ORGANIZATION_TYPE", "EXT_SOURCE_1", "EXT_SOURCE_2",
    "EXT_SOURCE_3",
]

CAT_COLS = [
    "CODE_GENDER", "FLAG_OWN_CAR", "FLAG_OWN_REALTY", "NAME_INCOME_TYPE",
    "NAME_EDUCATION_TYPE", "NAME_FAMILY_STATUS", "NAME_HOUSING_TYPE",
    "OCCUPATION_TYPE", "ORGANIZATION_TYPE",
]

NUM_COLS_BASE = [
    "CNT_CHILDREN", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AGE_YEARS", "FLAG_MOBIL",
    "FLAG_EMP_PHONE", "FLAG_EMAIL", "REGION_RATING_CLIENT", "EXT_SOURCE_1",
    "EXT_SOURCE_2", "EXT_SOURCE_3", "CREDIT_INCOME_RATIO",
]

SERASA_COLS = [
    "SER_QTDE_EMPRESTIMOS", "SER_DIVIDA_ATRASADA", "SER_CREDITOS_ATIVOS",
    "SER_DAYS_CREDIT_MEDIO", "SER_DIAS_ATRASO_MAX", "SER_CREDITO_TOTAL",
    "SER_DIVIDA_TOTAL", "SER_MAX_OVERDUE", "SER_QTDE_PRORROGACOES",
]

PREV_COLS = [
    "PREV_QTDE_TENTATIVAS", "PREV_QTDE_REJEITADAS", "PREV_TAXA_REJEICAO",
    "PREV_VALOR_SOLICITADO_TOTAL", "PREV_VALOR_APROVADO_TOTAL",
    "PREV_RAZAO_APROVADO_SOLICITADO", "PREV_QTDE_COM_SEGURO",
    "PREV_QTDE_CLIENTE_REPETIDOR", "PREV_QTDE_CANCELADO",
]

METRIC_FIELDS = [
    "AMT_INCOME_TOTAL", "AMT_CREDIT", "CREDIT_INCOME_RATIO", "EXT_SOURCE_1",
    "EXT_SOURCE_2", "EXT_SOURCE_3", "SER_QTDE_EMPRESTIMOS", "SER_DIVIDA_ATRASADA",
    "SER_CREDITOS_ATIVOS", "PREV_TAXA_REJEICAO",
]

METRIC_WEIGHTS = {
    "AMT_INCOME_TOTAL": 0.08,
    "AMT_CREDIT": 0.08,
    "CREDIT_INCOME_RATIO": 0.15,
    "EXT_SOURCE_1": 0.10,
    "EXT_SOURCE_2": 0.15,
    "EXT_SOURCE_3": 0.15,
    "SER_QTDE_EMPRESTIMOS": 0.02,
    "SER_DIVIDA_ATRASADA": 0.12,
    "SER_CREDITOS_ATIVOS": 0.03,
    "PREV_TAXA_REJEICAO": 0.12,
}
LOWER_IS_RISK = {"AMT_INCOME_TOTAL", "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"}


def robust_normalize(series: pd.Series, inverse: bool = False) -> pd.Series:
    p01 = series.quantile(0.01)
    p99 = series.quantile(0.99)
    if p99 <= p01:
        norm = pd.Series(0.0, index=series.index)
    else:
        norm = ((series.clip(p01, p99) - p01) / (p99 - p01)).clip(0, 1)
    if inverse:
        norm = 1 - norm
    return norm


def column_as_series(df: pd.DataFrame, column: str) -> pd.Series:
    return cast(pd.Series, df.loc[:, column])


def hopkins_statistic(df: pd.DataFrame, fields: list[str], sample_size: int = 1000, random_state: int = 42) -> float:
    """Calcula Hopkins em uma amostra para avaliar tendência de agrupamento."""
    fields_df = cast(pd.DataFrame, df.loc[:, fields])
    sample = fields_df.sample(n=min(sample_size, len(df)), random_state=random_state)
    x = sample.to_numpy(dtype=float)
    std = np.std(x, axis=0)
    x = x[:, std > 0]
    n = len(x)
    if n < 10 or x.shape[1] == 0:
        return float("nan")

    mins = np.min(x, axis=0)
    maxs = np.max(x, axis=0)
    ranges = np.where(maxs > mins, maxs - mins, 1)
    x = (x - mins) / ranges

    rng = np.random.default_rng(random_state)
    m = min(max(int(0.1 * n), 1), 100)
    real_idx = rng.choice(n, size=m, replace=False)
    artificial = rng.uniform(0, 1, size=(m, x.shape[1]))

    u_dist = []
    w_dist = []
    for i, idx in enumerate(real_idx):
        artificial_dist = np.sqrt(np.sum((x - artificial[i]) ** 2, axis=1))
        u_dist.append(float(np.min(artificial_dist)))

        real_dist = np.sqrt(np.sum((x - x[idx]) ** 2, axis=1))
        real_dist[idx] = np.inf
        w_dist.append(float(np.min(real_dist)))

    denom = sum(u_dist) + sum(w_dist)
    if denom == 0:
        return float("nan")
    return float(sum(u_dist) / denom)


def load_and_aggregate_serasa() -> pd.DataFrame:
    usecols = [
        "SK_ID_CURR", "SK_ID_BUREAU", "CREDIT_ACTIVE", "DAYS_CREDIT",
        "CREDIT_DAY_OVERDUE", "AMT_CREDIT_MAX_OVERDUE", "CNT_CREDIT_PROLONG",
        "AMT_CREDIT_SUM", "AMT_CREDIT_SUM_DEBT", "AMT_CREDIT_SUM_OVERDUE",
    ]
    serasa = pd.read_csv(PATH_SERASA, sep=SEP, usecols=usecols, low_memory=False)
    for col in [c for c in usecols if c not in {"SK_ID_CURR", "SK_ID_BUREAU", "CREDIT_ACTIVE"}]:
        serasa[col] = pd.to_numeric(serasa[col], errors="coerce")
    serasa["CREDITO_ATIVO_FLAG"] = (serasa["CREDIT_ACTIVE"].astype(str).str.lower() == "active").astype(int)
    agg = serasa.groupby("SK_ID_CURR").agg(
        SER_QTDE_EMPRESTIMOS=("SK_ID_BUREAU", "count"),
        SER_DIVIDA_ATRASADA=("AMT_CREDIT_SUM_OVERDUE", "sum"),
        SER_CREDITOS_ATIVOS=("CREDITO_ATIVO_FLAG", "sum"),
        SER_DAYS_CREDIT_MEDIO=("DAYS_CREDIT", "mean"),
        SER_DIAS_ATRASO_MAX=("CREDIT_DAY_OVERDUE", "max"),
        SER_CREDITO_TOTAL=("AMT_CREDIT_SUM", "sum"),
        SER_DIVIDA_TOTAL=("AMT_CREDIT_SUM_DEBT", "sum"),
        SER_MAX_OVERDUE=("AMT_CREDIT_MAX_OVERDUE", "max"),
        SER_QTDE_PRORROGACOES=("CNT_CREDIT_PROLONG", "sum"),
    ).reset_index()
    return agg


def load_and_aggregate_previous() -> pd.DataFrame:
    usecols = [
        "SK_ID_PREV", "SK_ID_CURR", "AMT_APPLICATION", "AMT_CREDIT",
        "NAME_CONTRACT_STATUS", "NAME_CLIENT_TYPE", "NFLAG_INSURED_ON_APPROVAL",
    ]
    prev = pd.read_csv(PATH_PREV, sep=SEP, usecols=usecols, low_memory=False)
    for col in ["AMT_APPLICATION", "AMT_CREDIT", "NFLAG_INSURED_ON_APPROVAL"]:
        prev[col] = pd.to_numeric(prev[col], errors="coerce")
    prev["REJEITADA_FLAG"] = (prev["NAME_CONTRACT_STATUS"].astype(str).str.lower() == "refused").astype(int)
    prev["CANCELADO_FLAG"] = prev["NAME_CONTRACT_STATUS"].astype(str).str.lower().isin(["canceled", "cancelled"]).astype(int)
    prev["COM_SEGURO_FLAG"] = (prev["NFLAG_INSURED_ON_APPROVAL"].fillna(0) > 0).astype(int)
    prev["CLIENTE_REPETIDOR_FLAG"] = (prev["NAME_CLIENT_TYPE"].astype(str).str.lower() == "repeater").astype(int)
    agg = prev.groupby("SK_ID_CURR").agg(
        PREV_QTDE_TENTATIVAS=("SK_ID_PREV", "count"),
        PREV_QTDE_REJEITADAS=("REJEITADA_FLAG", "sum"),
        PREV_VALOR_SOLICITADO_TOTAL=("AMT_APPLICATION", "sum"),
        PREV_VALOR_APROVADO_TOTAL=("AMT_CREDIT", "sum"),
        PREV_QTDE_COM_SEGURO=("COM_SEGURO_FLAG", "sum"),
        PREV_QTDE_CLIENTE_REPETIDOR=("CLIENTE_REPETIDOR_FLAG", "sum"),
        PREV_QTDE_CANCELADO=("CANCELADO_FLAG", "sum"),
    ).reset_index()
    agg["PREV_TAXA_REJEICAO"] = np.where(
        agg["PREV_QTDE_TENTATIVAS"] > 0,
        agg["PREV_QTDE_REJEITADAS"] / agg["PREV_QTDE_TENTATIVAS"],
        0,
    )
    agg["PREV_RAZAO_APROVADO_SOLICITADO"] = np.where(
        agg["PREV_VALOR_SOLICITADO_TOTAL"] > 0,
        agg["PREV_VALOR_APROVADO_TOTAL"] / agg["PREV_VALOR_SOLICITADO_TOTAL"],
        0,
    )
    return agg


def create_sqlite_db(df: pd.DataFrame) -> None:
    if os.path.exists(OUT_DB):
        os.remove(OUT_DB)
    conn = sqlite3.connect(OUT_DB)
    df.to_sql("base_final_metrica", conn, index=False, if_exists="replace")
    conn.execute("CREATE INDEX idx_base_final_sk ON base_final_metrica (SK_ID_CURR);")
    conn.commit()
    conn.close()


def main() -> None:
    args = parse_args()
    global BASE_DIR, PATH_EMPRESTIMOS, PATH_SERASA, PATH_PREV
    global OUT_FINAL, OUT_METRIC, OUT_DICT, OUT_SUMMARY, OUT_JSON, OUT_DB

    BASE_DIR = resolve_base_dir(args.base_dir)
    PATH_EMPRESTIMOS = str(BASE_DIR / "emprestimos.csv")
    PATH_SERASA = str(BASE_DIR / "serasa.csv")
    PATH_PREV = str(BASE_DIR / "emprestimos_anteriores.csv")
    OUT_FINAL = str(BASE_DIR / "base_final_preprocessada.csv")
    OUT_METRIC = str(BASE_DIR / "base_final_com_metrica.csv")
    OUT_DICT = str(BASE_DIR / "dicionario_codificacao_categorias.csv")
    OUT_SUMMARY = str(BASE_DIR / "resumo_estatistico_preprocessamento.csv")
    OUT_JSON = str(BASE_DIR / "resumo_processamento.json")
    OUT_DB = str(BASE_DIR / "preprocessamento_credito.db")

    print("1/9 Lendo base principal...")
    main_df = pd.read_csv(PATH_EMPRESTIMOS, sep=SEP, usecols=MAIN_COLS, low_memory=False)
    rows_main = len(main_df)
    target_counts = main_df["TARGET"].value_counts(dropna=False).to_dict()

    print("2/9 Agregando Serasa...")
    serasa_agg = load_and_aggregate_serasa()
    print("3/9 Agregando empréstimos anteriores...")
    prev_agg = load_and_aggregate_previous()

    print("4/9 Juntando bases...")
    df: pd.DataFrame = cast(
        pd.DataFrame,
        main_df.merge(serasa_agg, on="SK_ID_CURR", how="left").merge(prev_agg, on="SK_ID_CURR", how="left"),
    )
    df["AGE_YEARS"] = (df["DAYS_BIRTH"].abs() / 365.25).round(2)
    df["CREDIT_INCOME_RATIO"] = np.where(df["AMT_INCOME_TOTAL"] > 0, df["AMT_CREDIT"] / df["AMT_INCOME_TOTAL"], np.nan)
    df = df.drop(columns=["DAYS_BIRTH"])

    print("5/9 Tratando ausentes e codificando categóricas...")
    missing_before = df.isna().sum().to_dict()
    for col in SERASA_COLS + PREV_COLS:
        numeric_series = cast(pd.Series, pd.to_numeric(column_as_series(df, col), errors="coerce"))
        df[col] = numeric_series.fillna(0)
    for col in NUM_COLS_BASE:
        df[col] = cast(pd.Series, pd.to_numeric(column_as_series(df, col), errors="coerce"))
        numeric_col = column_as_series(df, col)
        median = numeric_col.median()
        df[col] = numeric_col.fillna(median)
    category_rows = []
    for col in CAT_COLS:
        df[col] = df[col].fillna("Unknown").replace("", "Unknown").astype(str)
        cats = sorted(str(cat) for cat in df[col].unique().tolist())
        if "Unknown" in cats:
            cats.remove("Unknown")
            cats.insert(0, "Unknown")
        mapping: dict[str, int] = {cat: code for code, cat in enumerate(cats)}
        counts = df[col].value_counts().to_dict()
        for cat, code in mapping.items():
            category_rows.append({
                "CAMPO_ORIGINAL": col,
                "CATEGORIA": cat,
                "CODIGO": code,
                "FREQUENCIA": int(counts.get(cat, 0)),
            })
        df[col + "_COD"] = df[col].astype(str).map(lambda value: mapping[value]).astype(int)
    dict_df = pd.DataFrame(category_rows)
    dict_df.to_csv(OUT_DICT, sep=SEP, index=False, encoding="utf-8")

    final_cols = ["SK_ID_CURR", "TARGET"] + NUM_COLS_BASE + [c + "_COD" for c in CAT_COLS] + SERASA_COLS + PREV_COLS
    final_df: pd.DataFrame = cast(pd.DataFrame, df.loc[:, final_cols].copy())
    # Arredondamento controlado para reduzir tamanho e manter legibilidade.
    float_cols = final_df.select_dtypes(include=["float", "float64", "float32"]).columns
    final_df[float_cols] = final_df[float_cols].round(6)

    print("6/9 Criando métrica ponderada...")
    metric = pd.Series(0.0, index=final_df.index)
    bounds = {}
    for field, weight in METRIC_WEIGHTS.items():
        inverse = field in LOWER_IS_RISK
        field_series: pd.Series = column_as_series(final_df, field)
        p01 = float(field_series.quantile(0.01))
        p99 = float(field_series.quantile(0.99))
        bounds[field] = {"p01": p01, "p99": p99, "inverse": inverse, "weight": weight}
        metric += robust_normalize(field_series, inverse=inverse) * weight
    metric_df: pd.DataFrame = cast(pd.DataFrame, final_df.copy())
    metric_df["METRICA_RISCO_0_100"] = (metric * 100).round(2)
    risk_class: pd.Series = cast(pd.Series, pd.cut(
        column_as_series(metric_df, "METRICA_RISCO_0_100"),
        bins=[-0.01, 33, 66, 100],
        labels=["Baixo", "Medio", "Alto"],
    ))
    metric_df["CLASSE_METRICA"] = risk_class.astype(str)

    print("7/9 Calculando estatística de Hopkins...")
    hopkins_value = hopkins_statistic(final_df, METRIC_FIELDS)

    print("8/9 Salvando CSVs...")
    final_df.to_csv(OUT_FINAL, sep=SEP, index=False, encoding="utf-8")
    metric_df.to_csv(OUT_METRIC, sep=SEP, index=False, encoding="utf-8")

    metric_score: pd.Series = column_as_series(metric_df, "METRICA_RISCO_0_100")
    metric_class: pd.Series = column_as_series(metric_df, "CLASSE_METRICA")
    metric_class_counts: pd.Series = metric_class.value_counts().sort_index()
    metric_desc = metric_score.describe(percentiles=[0.25, 0.50, 0.75]).to_dict()
    summary_rows = []
    summary_rows.append(["Linhas", "Base principal", rows_main])
    summary_rows.append(["Linhas", "Base final", len(final_df)])
    summary_rows.append(["Agregacao", "Clientes com registros no Serasa", len(serasa_agg)])
    summary_rows.append(["Agregacao", "Clientes com emprestimos anteriores", len(prev_agg)])
    for target, count in sorted(target_counts.items()):
        summary_rows.append(["TARGET", f"Classe {target}", f"{int(count)} ({count/rows_main*100:.2f}%)"])
    for col, count in sorted(missing_before.items()):
        if count > 0:
            summary_rows.append(["Ausentes antes", col, f"{int(count)} ({count/rows_main*100:.2f}%)"])
    for item, val in metric_desc.items():
        summary_rows.append(["Metrica", item, round(float(val), 4)])
    for band, count in metric_class_counts.items():
        summary_rows.append(["Faixa da metrica", band, f"{int(count)} ({count/len(metric_df)*100:.2f}%)"])
    summary_rows.append(["Qualidade", "Estatistica de Hopkins", round(float(hopkins_value), 4)])
    pd.DataFrame(summary_rows, columns=["GRUPO", "ITEM", "VALOR"]).to_csv(OUT_SUMMARY, sep=SEP, index=False, encoding="utf-8")

    summary = {
        "linhas_base_principal": rows_main,
        "linhas_base_final": len(final_df),
        "target_counts": {str(k): int(v) for k, v in target_counts.items()},
        "serasa_clientes_agregados": int(len(serasa_agg)),
        "emprestimos_anteriores_clientes_agregados": int(len(prev_agg)),
        "missing_before": {str(k): int(v) for k, v in missing_before.items() if int(v) > 0},
        "metric_bounds": bounds,
        "metric_summary": {str(k): float(v) for k, v in metric_desc.items()},
        "hopkins_statistic": float(hopkins_value),
        "risk_bands": {str(k): int(v) for k, v in metric_class_counts.items()},
        "final_columns": final_cols,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("9/9 Criando banco SQLite...")
    create_sqlite_db(metric_df)
    print("Concluído")


if __name__ == "__main__":
    main()
