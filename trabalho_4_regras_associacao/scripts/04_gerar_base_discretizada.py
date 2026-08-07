"""Gera a base nominal de Apriori a partir das faixas aprovadas na Etapa 3.

Não executa WEKA nem Apriori. A fonte é a amostra original do Trabalho 3 e os
identificadores permanecem exclusivamente na origem, para rastreabilidade.
"""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "trabalho_3_clusterizacao" / "data" / "amostras" / "base_amostra_10000_analise.csv"
DISCRETIZATION_SCRIPT = ROOT / "trabalho_4_regras_associacao" / "scripts" / "03_propor_discretizacao.py"
OUTPUT_DIR = ROOT / "trabalho_4_regras_associacao" / "data" / "discretizadas"
CSV_OUTPUT = OUTPUT_DIR / "base_apriori_discretizada.csv"
ARFF_OUTPUT = OUTPUT_DIR / "base_apriori_discretizada.arff"

OUTPUT_COLUMNS = {
    "AMT_CREDIT": "FAIXA_CREDITO",
    "AMT_INCOME_TOTAL": "FAIXA_RENDA",
    "AGE_YEARS": "FAIXA_IDADE",
    "CNT_CHILDREN": "CATEGORIA_FILHOS",
    "FLAG_OWN_CAR_COD": "POSSE_CARRO",
    "NAME_FAMILY_STATUS_COD": "SITUACAO_FAMILIAR",
    "SER_CREDITOS_ATIVOS": "FAIXA_CREDITOS_ATIVOS",
    "PREV_TAXA_REJEICAO": "FAIXA_TAXA_REJEICAO",
}
FORBIDDEN = {"SK_ID_CURR", "TARGET", "ROW_ID_AMOSTRA", "cluster"}
AMBIGUOUS_VALUES = {"", "0", "0.0", "nan", "none", "null", "?"}


def load_discretization_module():
    spec = importlib.util.spec_from_file_location("proposta_discretizacao", DISCRETIZATION_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Não foi possível carregar a proposta de discretização aprovada.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_nominal_frame(data: pd.DataFrame) -> pd.DataFrame:
    proposal = load_discretization_module()
    categories = proposal.as_categories(data)
    if list(OUTPUT_COLUMNS) != proposal.ATTRIBUTES:
        raise ValueError("A ordem dos atributos da base final diverge da proposta aprovada na Etapa 3.")
    result = pd.DataFrame(
        {output_name: categories[source_name].astype(str) for source_name, output_name in OUTPUT_COLUMNS.items()},
        index=data.index,
    )
    return result


def write_arff(frame: pd.DataFrame) -> None:
    lines = ["@relation base_apriori_discretizada", ""]
    for column in frame.columns:
        values = sorted(frame[column].unique())
        lines.append(f"@attribute {column} {{{','.join(values)}}}")
    lines += ["", "@data"]
    lines.extend(",".join(row) for row in frame.itertuples(index=False, name=None))
    ARFF_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def validate_arff(frame: pd.DataFrame) -> None:
    lines = ARFF_OUTPUT.read_text(encoding="utf-8").splitlines()
    attribute_lines = [line for line in lines if line.lower().startswith("@attribute ")]
    if len(attribute_lines) != len(frame.columns):
        raise ValueError("ARFF não possui exatamente oito atributos declarados.")
    data_position = next((index for index, line in enumerate(lines) if line.lower() == "@data"), None)
    if data_position is None:
        raise ValueError("ARFF sem marcador @data.")
    rows = [line for line in lines[data_position + 1 :] if line.strip()]
    if len(rows) != len(frame):
        raise ValueError("Quantidade de registros do ARFF diverge do CSV.")
    if any(len(row.split(",")) != len(frame.columns) for row in rows):
        raise ValueError("ARFF contém uma linha com quantidade incorreta de atributos.")


def validate(source: pd.DataFrame, expected: pd.DataFrame, saved: pd.DataFrame) -> str:
    if len(source) != 10_000 or len(saved) != 10_000:
        raise ValueError("A base discretizada deve conter exatamente 10.000 registros.")
    if list(saved.columns) != list(OUTPUT_COLUMNS.values()):
        raise ValueError("A base discretizada não contém exatamente os oito atributos aprovados.")
    if FORBIDDEN.intersection(saved.columns):
        raise ValueError("A base discretizada contém coluna protegida ou cluster.")
    if any(pd.api.types.is_numeric_dtype(saved[column]) for column in saved.columns):
        raise ValueError("Todo atributo destinado ao Apriori deve ser nominal.")
    if saved.isna().any().any() or (saved.astype(str).apply(lambda column: column.str.strip().eq(""))).any().any():
        raise ValueError("A base discretizada contém categoria vazia.")
    if saved.astype(str).apply(lambda column: column.str.lower().isin(AMBIGUOUS_VALUES)).any().any():
        raise ValueError("A base discretizada contém valor ambíguo ou zero numérico.")
    if not expected.reset_index(drop=True).equals(saved.reset_index(drop=True)):
        raise ValueError("O CSV salvo diverge das categorias calculadas na mesma ordem da origem.")
    if not source.index.equals(expected.index):
        raise ValueError("A geração alterou a ordem dos registros da origem.")
    row_id_sequence = "|".join(source["ROW_ID_AMOSTRA"].astype(str)).encode("utf-8")
    return hashlib.sha256(row_id_sequence).hexdigest()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    source = pd.read_csv(SOURCE, sep=";", low_memory=False)
    expected = make_nominal_frame(source)
    expected.to_csv(CSV_OUTPUT, sep=";", index=False, encoding="utf-8", lineterminator="\n")
    saved = pd.read_csv(CSV_OUTPUT, sep=";", dtype=str, keep_default_na=False)
    row_id_hash = validate(source, expected, saved)
    write_arff(saved)
    validate_arff(saved)
    print("Base Apriori discretizada criada e validada.")
    print(f"CSV: {CSV_OUTPUT}")
    print(f"ARFF: {ARFF_OUTPUT}")
    print("Registros: 10000; atributos nominais: 8")
    print(f"Hash da sequência ROW_ID_AMOSTRA na origem: {row_id_hash}")


if __name__ == "__main__":
    main()
