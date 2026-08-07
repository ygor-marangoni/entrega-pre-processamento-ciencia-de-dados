"""Valida a base nominal de Apriori e calcula a frequência de todos os itens."""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "trabalho_3_clusterizacao" / "data" / "amostras" / "base_amostra_10000_analise.csv"
CSV_BASE = ROOT / "trabalho_4_regras_associacao" / "data" / "discretizadas" / "base_apriori_discretizada.csv"
GENERATOR_SCRIPT = ROOT / "trabalho_4_regras_associacao" / "scripts" / "04_gerar_base_discretizada.py"
RESULTS = ROOT / "trabalho_4_regras_associacao" / "resultados" / "discretizacao"
VALIDATION_OUTPUT = RESULTS / "validacao_base.csv"
FREQUENCY_OUTPUT = RESULTS / "frequencias_finais.csv"

EXPECTED_COLUMNS = [
    "FAIXA_CREDITO",
    "FAIXA_RENDA",
    "FAIXA_IDADE",
    "CATEGORIA_FILHOS",
    "POSSE_CARRO",
    "SITUACAO_FAMILIAR",
    "FAIXA_CREDITOS_ATIVOS",
    "FAIXA_TAXA_REJEICAO",
]
FORBIDDEN = {"SK_ID_CURR", "TARGET", "ROW_ID_AMOSTRA", "cluster"}
AMBIGUOUS = {"", "0", "0.0", "nan", "none", "null", "?"}


def load_generator_module():
    spec = importlib.util.spec_from_file_location("gerador_base_apriori", GENERATOR_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Não foi possível carregar o gerador da Etapa 4.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def add_check(checks: list[dict[str, str]], name: str, expected: str, observed: str, passed: bool, detail: str) -> None:
    checks.append(
        {
            "verificacao": name,
            "esperado": expected,
            "observado": observed,
            "status": "APROVADO" if passed else "REPROVADO",
            "detalhe": detail,
        }
    )


def item_frequencies(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for attribute in frame.columns:
        counts = frame[attribute].value_counts()
        for category, count in counts.items():
            rows.append(
                {
                    "atributo": attribute,
                    "categoria": category,
                    "item": f"{attribute}={category}",
                    "quantidade": int(count),
                    "percentual": 100 * int(count) / len(frame),
                }
            )
    return pd.DataFrame(rows).sort_values(["atributo", "quantidade", "categoria"], ascending=[True, False, True])


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(CSV_BASE, sep=";", dtype=str, keep_default_na=False)
    source = pd.read_csv(SOURCE, sep=";", low_memory=False)
    checks: list[dict[str, str]] = []
    add_check(checks, "quantidade_registros", "10000", str(len(frame)), len(frame) == 10_000, "A base Apriori deve preservar o tamanho da amostra autorizada.")
    add_check(checks, "quantidade_atributos", "8", str(len(frame.columns)), len(frame.columns) == 8, "A base deve conter exatamente os oito atributos selecionados.")
    add_check(checks, "ordem_e_nomes_atributos", "|".join(EXPECTED_COLUMNS), "|".join(frame.columns), list(frame.columns) == EXPECTED_COLUMNS, "Nomes semânticos e ordem aprovados na Etapa 4.")
    forbidden_found = sorted(FORBIDDEN.intersection(frame.columns))
    add_check(checks, "colunas_protegidas", "ausentes", ",".join(forbidden_found) or "nenhuma", not forbidden_found, "Identificadores, TARGET e cluster não podem virar itens.")
    missing_count = int(frame.isna().sum().sum() + frame.astype(str).apply(lambda col: col.str.strip().eq("")).sum().sum())
    add_check(checks, "categorias_vazias", "0", str(missing_count), missing_count == 0, "Não pode haver item vazio ou ausente.")
    numeric_columns = [name for name in frame.columns if pd.api.types.is_numeric_dtype(frame[name])]
    add_check(checks, "atributos_numericos", "0", str(len(numeric_columns)), not numeric_columns, "Todos os atributos devem ser nominais no CSV de Apriori.")
    ambiguous_count = int(frame.astype(str).apply(lambda col: col.str.lower().isin(AMBIGUOUS)).sum().sum())
    add_check(checks, "zeros_ou_strings_ambiguas", "0", str(ambiguous_count), ambiguous_count == 0, "Zero real deve estar representado por rótulo nominal.")

    generator = load_generator_module()
    expected = generator.make_nominal_frame(source).reset_index(drop=True).astype(str)
    actual = frame.reset_index(drop=True).astype(str)
    same_order = expected.equals(actual)
    add_check(checks, "ordem_dos_registros", "categorias idênticas à origem na mesma sequência", "corresponde" if same_order else "diverge", same_order, "Recalculado diretamente da amostra por meio das faixas autorizadas.")

    row_id_hash = hashlib.sha256("|".join(source["ROW_ID_AMOSTRA"].astype(str)).encode("utf-8")).hexdigest()
    add_check(checks, "rastreabilidade_origem", "sequência ROW_ID_AMOSTRA disponível na origem", row_id_hash, True, "Hash calculado somente na base auxiliar; o identificador não integra o CSV Apriori.")

    frequencies = item_frequencies(frame)
    sums = frequencies.groupby("atributo")["quantidade"].sum()
    frequency_ok = len(frequencies) == 27 and bool((sums == 10_000).all())
    add_check(checks, "frequencia_de_todos_os_itens", "27 itens; soma 10000 por atributo", f"{len(frequencies)} itens; somas corretas={bool((sums == 10_000).all())}", frequency_ok, "A frequência de cada item foi calculada para orientar os suportes futuros.")

    validation = pd.DataFrame(checks)
    validation.to_csv(VALIDATION_OUTPUT, sep=";", index=False)
    frequencies.to_csv(FREQUENCY_OUTPUT, sep=";", index=False, float_format="%.6f")
    failures = validation.loc[validation["status"] == "REPROVADO"]
    if not failures.empty:
        raise ValueError(f"Validação reprovada: {failures['verificacao'].tolist()}")
    print("Validação da base Apriori aprovada.")
    print(f"Itens frequentes calculados: {len(frequencies)}")
    print(f"Menor suporte de item: {frequencies['percentual'].min():.2f}%")
    print(f"Maior suporte de item: {frequencies['percentual'].max():.2f}%")


if __name__ == "__main__":
    main()
