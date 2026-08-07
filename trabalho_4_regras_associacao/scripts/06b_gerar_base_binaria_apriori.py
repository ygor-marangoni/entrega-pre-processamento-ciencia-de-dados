"""Gera a representação transacional binária para Apriori com -Z.

As oito dimensões semânticas não são alteradas: cada categoria da base nominal
se torna um item binário {0,1}, em que 0 é ausência e 1 é presença.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
NOMINAL_CSV = ROOT / "trabalho_4_regras_associacao" / "data" / "discretizadas" / "base_apriori_discretizada.csv"
BINARY_DIR = ROOT / "trabalho_4_regras_associacao" / "data" / "preparadas"
BINARY_CSV = BINARY_DIR / "base_apriori_binaria.csv"
BINARY_ARFF = BINARY_DIR / "base_apriori_binaria.arff"
FREQUENCIES = ROOT / "trabalho_4_regras_associacao" / "resultados" / "discretizacao" / "frequencias_finais.csv"
MAPPING_OUTPUT = ROOT / "trabalho_4_regras_associacao" / "resultados" / "discretizacao" / "mapeamento_itens_binarios.csv"
VALIDATION_OUTPUT = ROOT / "trabalho_4_regras_associacao" / "resultados" / "discretizacao" / "validacao_base_binaria.csv"
FORBIDDEN = {"TARGET", "SK_ID_CURR", "ROW_ID_AMOSTRA", "cluster"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_binary_frame(nominal: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    binary_columns: dict[str, pd.Series] = {}
    mapping_rows: list[dict[str, object]] = []
    groups: dict[str, list[str]] = {}
    for attribute in nominal.columns:
        categories = sorted(nominal[attribute].unique())
        groups[attribute] = []
        for category in categories:
            column_name = f"{attribute}__{category}"
            if column_name in binary_columns:
                raise ValueError(f"Nome binário duplicado: {column_name}")
            binary_columns[column_name] = nominal[attribute].eq(category).astype("int8")
            groups[attribute].append(column_name)
            count = int(binary_columns[column_name].sum())
            mapping_rows.append(
                {
                    "atributo_original": attribute,
                    "categoria": category,
                    "coluna_binaria": column_name,
                    "quantidade": count,
                    "percentual": 100 * count / len(nominal),
                }
            )
    return pd.DataFrame(binary_columns, index=nominal.index), pd.DataFrame(mapping_rows), groups


def write_arff(binary: pd.DataFrame) -> None:
    lines = ["@relation base_apriori_binaria", ""]
    lines.extend(f"@attribute {column} {{0,1}}" for column in binary.columns)
    lines += ["", "@data"]
    lines.extend(",".join(str(value) for value in row)
        for row in binary.itertuples(index=False, name=None)
    )
    BINARY_ARFF.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def validate_arff(binary: pd.DataFrame) -> bool:
    lines = BINARY_ARFF.read_text(encoding="utf-8").splitlines()
    attributes = [line for line in lines if line.lower().startswith("@attribute ")]
    correct_declarations = len(attributes) == len(binary.columns) and all(line.endswith(" {0,1}") for line in attributes)
    data_index = next((index for index, line in enumerate(lines) if line.lower() == "@data"), None)
    if data_index is None:
        return False
    rows = [line for line in lines[data_index + 1 :] if line]
    return (
        correct_declarations
        and len(rows) == len(binary)
        and all(len(row.split(",")) == len(binary.columns) for row in rows)
        and all(value in {"0", "1"} for row in rows for value in row.split(","))
        and not any("?" in row for row in rows)
    )


def add_check(checks: list[dict[str, str]], verification: str, expected: str, observed: str, passed: bool, detail: str) -> None:
    checks.append(
        {
            "verificacao": verification,
            "esperado": expected,
            "observado": observed,
            "status": "APROVADO" if passed else "REPROVADO",
            "detalhe": detail,
        }
    )


def main() -> None:
    BINARY_DIR.mkdir(parents=True, exist_ok=True)
    nominal_hash_before = sha256(NOMINAL_CSV)
    nominal = pd.read_csv(NOMINAL_CSV, sep=";", dtype=str, keep_default_na=False)
    checks: list[dict[str, str]] = []
    add_check(checks, "base_nominal_registros", "10000", str(len(nominal)), len(nominal) == 10_000, "A amostra autorizada deve ser preservada.")
    add_check(checks, "base_nominal_atributos", "8", str(len(nominal.columns)), len(nominal.columns) == 8, "As oito dimensões conceituais devem permanecer as mesmas.")
    forbidden_nominal = sorted(FORBIDDEN.intersection(nominal.columns))
    add_check(checks, "base_nominal_colunas_protegidas", "nenhuma", ",".join(forbidden_nominal) or "nenhuma", not forbidden_nominal, "A entrada técnica não pode conter campos protegidos.")

    binary, mapping, groups = build_binary_frame(nominal)
    expected_columns = int(nominal.nunique().sum())
    add_check(checks, "quantidade_itens_binarios", f"{expected_columns} (soma programática das categorias)", str(len(binary.columns)), len(binary.columns) == expected_columns, "Não há quantidade codificada manualmente.")
    add_check(checks, "registros_base_binaria", "10000", str(len(binary)), len(binary) == 10_000, "Nenhuma linha pode ser perdida ou adicionada.")
    only_binary = bool(binary.isin([0, 1]).all().all())
    add_check(checks, "valores_binarios", "somente 0 e 1", "somente 0 e 1" if only_binary else "valores inválidos", only_binary, "0 representa ausência e 1 representa presença do item.")
    active_per_row = binary.sum(axis=1)
    add_check(checks, "itens_ativos_por_transacao", "mínimo=8; máximo=8", f"mínimo={int(active_per_row.min())}; máximo={int(active_per_row.max())}", bool(active_per_row.eq(len(nominal.columns)).all()), "Cada dimensão original deve ativar exatamente um item.")
    group_valid = all(binary[columns].sum(axis=1).eq(1).all() for columns in groups.values())
    add_check(checks, "exclusividade_por_dimensao", "1 item ativo em cada uma das 8 dimensões", "confirmada" if group_valid else "divergente", group_valid, "One-hot preserva exclusividade interna de cada atributo nominal.")

    reconstructed = pd.DataFrame(index=nominal.index)
    for attribute, columns in groups.items():
        active = binary[columns].idxmax(axis=1)
        reconstructed[attribute] = active.str.removeprefix(f"{attribute}__")
    same_order = reconstructed.equals(nominal)
    add_check(checks, "ordem_e_reconstrucao_nominal", "reconstrução idêntica na mesma ordem", "corresponde" if same_order else "diverge", same_order, "A comparação linha a linha detecta omissão, duplicação ou alteração de categoria.")

    expected_frequencies = pd.read_csv(FREQUENCIES, sep=";")
    frequency_reference = expected_frequencies[["atributo", "categoria", "quantidade", "percentual"]].rename(columns={"atributo": "atributo_original"})
    comparison = mapping.merge(frequency_reference, on=["atributo_original", "categoria"], how="outer", suffixes=("_binaria", "_nominal"), indicator=True)
    frequencies_equal = (
        len(comparison) == len(mapping)
        and bool(comparison["_merge"].eq("both").all())
        and bool(comparison["quantidade_binaria"].eq(comparison["quantidade_nominal"]).all())
        and bool((comparison["percentual_binaria"] - comparison["percentual_nominal"]).abs().lt(1e-9).all())
    )
    add_check(checks, "frequencias_iguais_base_nominal", "igualdade exata para todos os itens", "confirmada" if frequencies_equal else "divergente", frequencies_equal, "Cada coluna binária deve reproduzir a frequência da categoria de origem.")

    binary.to_csv(BINARY_CSV, sep=";", index=False, lineterminator="\n")
    saved = pd.read_csv(BINARY_CSV, sep=";", dtype="int8")
    saved_equals = saved.equals(binary.reset_index(drop=True))
    add_check(checks, "csv_binario_salvo", "idêntico à matriz gerada", "corresponde" if saved_equals else "diverge", saved_equals, "Confere valores e ordem após a escrita do CSV.")
    write_arff(binary)
    arff_valid = validate_arff(binary)
    add_check(checks, "arff_binario", "27 atributos {0,1}; 10000 linhas sem ?", "válido" if arff_valid else "inválido", arff_valid, "Formato técnico para o Apriori com -Z.")
    nominal_hash_after = sha256(NOMINAL_CSV)
    add_check(checks, "base_nominal_preservada", nominal_hash_before, nominal_hash_after, nominal_hash_before == nominal_hash_after, "A representação semântica não foi modificada.")

    mapping.to_csv(MAPPING_OUTPUT, sep=";", index=False, float_format="%.6f")
    validation = pd.DataFrame(checks)
    validation.to_csv(VALIDATION_OUTPUT, sep=";", index=False)
    failures = validation.loc[validation["status"] == "REPROVADO"]
    if not failures.empty:
        raise ValueError(f"Validação bloqueada: {failures['verificacao'].tolist()}")
    print("Base binária transacional criada e validada.")
    print(f"Registros: {len(binary)}")
    print(f"Itens binários: {len(binary.columns)}")
    print(f"Itens ativos por transação: mínimo={int(active_per_row.min())}; máximo={int(active_per_row.max())}; esperado=8")
    print(f"Hash da base nominal preservada: {nominal_hash_after}")


if __name__ == "__main__":
    main()
