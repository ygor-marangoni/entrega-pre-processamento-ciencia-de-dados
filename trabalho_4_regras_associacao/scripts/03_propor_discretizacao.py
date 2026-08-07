"""Projeta e valida faixas de discretização para os oito atributos recomendados.

Esta etapa apenas simula categorias em memória e registra a proposta. Não cria
a base final de Apriori, não altera a origem e não executa o WEKA.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "trabalho_3_clusterizacao" / "data" / "amostras" / "base_amostra_10000_analise.csv"
RESULTS = ROOT / "trabalho_4_regras_associacao" / "resultados" / "discretizacao"
DECISIONS = ROOT / "trabalho_4_regras_associacao" / "docs" / "decisoes_discretizacao.md"

ATTRIBUTES = [
    "AMT_CREDIT",
    "AMT_INCOME_TOTAL",
    "AGE_YEARS",
    "CNT_CHILDREN",
    "FLAG_OWN_CAR_COD",
    "NAME_FAMILY_STATUS_COD",
    "SER_CREDITOS_ATIVOS",
    "PREV_TAXA_REJEICAO",
]


def as_categories(data: pd.DataFrame) -> dict[str, pd.Series]:
    """Aplica em memória as faixas propostas, preservando o índice original."""
    categories: dict[str, pd.Series] = {}
    categories["AMT_CREDIT"] = pd.cut(
        data["AMT_CREDIT"],
        bins=[-np.inf, 270000, 512721, 810000, np.inf],
        labels=["CREDITO_BAIXO", "CREDITO_MEDIO", "CREDITO_ALTO", "CREDITO_MUITO_ALTO"],
        include_lowest=True,
    )
    categories["AMT_INCOME_TOTAL"] = pd.cut(
        data["AMT_INCOME_TOTAL"],
        bins=[-np.inf, 112500, 148500, 202500, np.inf],
        labels=["RENDA_BAIXA", "RENDA_MEDIA", "RENDA_ALTA", "RENDA_MUITO_ALTA"],
        include_lowest=True,
    )
    categories["AGE_YEARS"] = pd.cut(
        data["AGE_YEARS"],
        bins=[20, 29, 39, 49, 59, np.inf],
        labels=["IDADE_21_A_29", "IDADE_30_A_39", "IDADE_40_A_49", "IDADE_50_A_59", "IDADE_60_OU_MAIS"],
        include_lowest=True,
    )
    categories["CNT_CHILDREN"] = pd.Series(
        np.select(
            [data["CNT_CHILDREN"].eq(0), data["CNT_CHILDREN"].eq(1), data["CNT_CHILDREN"].ge(2)],
            ["SEM_FILHOS", "UM_FILHO", "DOIS_OU_MAIS_FILHOS"],
            default=None,
        ),
        index=data.index,
        dtype="object",
    )
    categories["FLAG_OWN_CAR_COD"] = data["FLAG_OWN_CAR_COD"].map({0: "SEM_CARRO", 1: "COM_CARRO"})
    categories["NAME_FAMILY_STATUS_COD"] = data["NAME_FAMILY_STATUS_COD"].map(
        {
            1: "CASADO_OU_UNIAO_CIVIL",
            2: "CASADO_OU_UNIAO_CIVIL",
            4: "SOLTEIRO",
            0: "SEPARADO_VIUVO_OU_NAO_INFORMADO",
            3: "SEPARADO_VIUVO_OU_NAO_INFORMADO",
            5: "SEPARADO_VIUVO_OU_NAO_INFORMADO",
        }
    )
    categories["SER_CREDITOS_ATIVOS"] = pd.Series(
        np.select(
            [data["SER_CREDITOS_ATIVOS"].eq(0), data["SER_CREDITOS_ATIVOS"].between(1, 2), data["SER_CREDITOS_ATIVOS"].ge(3)],
            ["SEM_CREDITOS_ATIVOS", "UM_A_DOIS_CREDITOS_ATIVOS", "TRES_OU_MAIS_CREDITOS_ATIVOS"],
            default=None,
        ),
        index=data.index,
        dtype="object",
    )
    categories["PREV_TAXA_REJEICAO"] = pd.Series(
        np.select(
            [data["PREV_TAXA_REJEICAO"].eq(0), data["PREV_TAXA_REJEICAO"].gt(0) & data["PREV_TAXA_REJEICAO"].le(0.25), data["PREV_TAXA_REJEICAO"].gt(0.25)],
            ["SEM_REJEICAO_PREVIA", "REJEICAO_PREVIA_ATE_25_PCT", "REJEICAO_PREVIA_ACIMA_25_PCT"],
            default=None,
        ),
        index=data.index,
        dtype="object",
    )
    return categories


def proposal_rows() -> list[dict[str, str]]:
    return [
        {"atributo": "AMT_CREDIT", "tipo": "NUMERICO", "categoria": "CREDITO_BAIXO", "regra": "AMT_CREDIT <= 270000", "criterio": "P25", "justificativa": "Primeiro quartil; isola créditos de menor porte.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "AMT_CREDIT", "tipo": "NUMERICO", "categoria": "CREDITO_MEDIO", "regra": "270000 < AMT_CREDIT <= 512721", "criterio": "P25 a P50", "justificativa": "Faixa central inferior da distribuição.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "AMT_CREDIT", "tipo": "NUMERICO", "categoria": "CREDITO_ALTO", "regra": "512721 < AMT_CREDIT <= 810000", "criterio": "P50 a P75", "justificativa": "Faixa central superior da distribuição.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "AMT_CREDIT", "tipo": "NUMERICO", "categoria": "CREDITO_MUITO_ALTO", "regra": "AMT_CREDIT > 810000", "criterio": "Acima de P75", "justificativa": "Cauda superior preservada sem criar faixa rara.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "AMT_INCOME_TOTAL", "tipo": "NUMERICO", "categoria": "RENDA_BAIXA", "regra": "AMT_INCOME_TOTAL <= 112500", "criterio": "P25", "justificativa": "Primeiro quartil; corte robusto diante de extremos.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "AMT_INCOME_TOTAL", "tipo": "NUMERICO", "categoria": "RENDA_MEDIA", "regra": "112500 < AMT_INCOME_TOTAL <= 148500", "criterio": "P25 a P50", "justificativa": "Faixa central inferior observada.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "AMT_INCOME_TOTAL", "tipo": "NUMERICO", "categoria": "RENDA_ALTA", "regra": "148500 < AMT_INCOME_TOTAL <= 202500", "criterio": "P50 a P75", "justificativa": "Faixa central superior observada.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "AMT_INCOME_TOTAL", "tipo": "NUMERICO", "categoria": "RENDA_MUITO_ALTA", "regra": "AMT_INCOME_TOTAL > 202500", "criterio": "Acima de P75", "justificativa": "Agrupa cauda extrema sem faixas definidas pela largura do intervalo.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "AGE_YEARS", "tipo": "NUMERICO", "categoria": "IDADE_21_A_29", "regra": "21 <= AGE_YEARS <= 29", "criterio": "Semântico", "justificativa": "Início da vida adulta; limite inferior observado é 21,07.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "AGE_YEARS", "tipo": "NUMERICO", "categoria": "IDADE_30_A_39", "regra": "29 < AGE_YEARS <= 39", "criterio": "Semântico", "justificativa": "Faixa adulta inicial com frequência suficiente.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "AGE_YEARS", "tipo": "NUMERICO", "categoria": "IDADE_40_A_49", "regra": "39 < AGE_YEARS <= 49", "criterio": "Semântico", "justificativa": "Faixa adulta intermediária com frequência suficiente.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "AGE_YEARS", "tipo": "NUMERICO", "categoria": "IDADE_50_A_59", "regra": "49 < AGE_YEARS <= 59", "criterio": "Semântico", "justificativa": "Faixa madura com frequência suficiente.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "AGE_YEARS", "tipo": "NUMERICO", "categoria": "IDADE_60_OU_MAIS", "regra": "AGE_YEARS > 59", "criterio": "Semântico", "justificativa": "Faixa sênior; preserva interpretação de ciclo de vida.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "CNT_CHILDREN", "tipo": "CONTAGEM", "categoria": "SEM_FILHOS", "regra": "CNT_CHILDREN = 0", "criterio": "Zero semântico", "justificativa": "Maior grupo e significado real explícito.", "zero_semantico_rotulado": "SIM"},
        {"atributo": "CNT_CHILDREN", "tipo": "CONTAGEM", "categoria": "UM_FILHO", "regra": "CNT_CHILDREN = 1", "criterio": "Semântico", "justificativa": "Grupo natural e frequente.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "CNT_CHILDREN", "tipo": "CONTAGEM", "categoria": "DOIS_OU_MAIS_FILHOS", "regra": "CNT_CHILDREN >= 2", "criterio": "Frequência", "justificativa": "Agrupa contagens raras de 3 a 5 com dois filhos.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "FLAG_OWN_CAR_COD", "tipo": "CATEGORICO", "categoria": "SEM_CARRO", "regra": "codigo 0", "criterio": "Dicionário do Trabalho 1", "justificativa": "Rótulo semântico recuperado; não usar o código numérico.", "zero_semantico_rotulado": "SIM"},
        {"atributo": "FLAG_OWN_CAR_COD", "tipo": "CATEGORICO", "categoria": "COM_CARRO", "regra": "codigo 1", "criterio": "Dicionário do Trabalho 1", "justificativa": "Rótulo semântico recuperado.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "NAME_FAMILY_STATUS_COD", "tipo": "CATEGORICO", "categoria": "CASADO_OU_UNIAO_CIVIL", "regra": "codigos 1 ou 2", "criterio": "Semântica e frequência", "justificativa": "Combina situações com parceiro formal para reduzir fragmentação.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "NAME_FAMILY_STATUS_COD", "tipo": "CATEGORICO", "categoria": "SOLTEIRO", "regra": "codigo 4", "criterio": "Dicionário do Trabalho 1", "justificativa": "Categoria individual frequente e interpretável.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "NAME_FAMILY_STATUS_COD", "tipo": "CATEGORICO", "categoria": "SEPARADO_VIUVO_OU_NAO_INFORMADO", "regra": "codigos 0, 3 ou 5", "criterio": "Frequência", "justificativa": "Evita a categoria Unknown isolada com apenas um registro.", "zero_semantico_rotulado": "SIM"},
        {"atributo": "SER_CREDITOS_ATIVOS", "tipo": "CONTAGEM", "categoria": "SEM_CREDITOS_ATIVOS", "regra": "SER_CREDITOS_ATIVOS = 0", "criterio": "Zero semântico", "justificativa": "Ausência real de créditos ativos, não valor ausente.", "zero_semantico_rotulado": "SIM"},
        {"atributo": "SER_CREDITOS_ATIVOS", "tipo": "CONTAGEM", "categoria": "UM_A_DOIS_CREDITOS_ATIVOS", "regra": "1 <= SER_CREDITOS_ATIVOS <= 2", "criterio": "Frequência", "justificativa": "Agrupa a maior massa de valores positivos.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "SER_CREDITOS_ATIVOS", "tipo": "CONTAGEM", "categoria": "TRES_OU_MAIS_CREDITOS_ATIVOS", "regra": "SER_CREDITOS_ATIVOS >= 3", "criterio": "Frequência", "justificativa": "Evita uma categoria rara para seis ou mais créditos.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "PREV_TAXA_REJEICAO", "tipo": "PROPORCAO", "categoria": "SEM_REJEICAO_PREVIA", "regra": "PREV_TAXA_REJEICAO = 0", "criterio": "Zero semântico", "justificativa": "Taxa nula representa histórico sem rejeição registrada.", "zero_semantico_rotulado": "SIM"},
        {"atributo": "PREV_TAXA_REJEICAO", "tipo": "PROPORCAO", "categoria": "REJEICAO_PREVIA_ATE_25_PCT", "regra": "0 < PREV_TAXA_REJEICAO <= 0.25", "criterio": "P25 entre valores positivos", "justificativa": "Distingue rejeição positiva menor ou igual a 25%.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
        {"atributo": "PREV_TAXA_REJEICAO", "tipo": "PROPORCAO", "categoria": "REJEICAO_PREVIA_ACIMA_25_PCT", "regra": "PREV_TAXA_REJEICAO > 0.25", "criterio": "P50 aproximado entre valores positivos", "justificativa": "Agrupa taxas moderadas e altas com suporte suficiente.", "zero_semantico_rotulado": "NAO_SE_APLICA"},
    ]


def frequency_table(categories: dict[str, pd.Series]) -> pd.DataFrame:
    records = []
    for attribute, values in categories.items():
        counts = values.value_counts(dropna=False)
        non_null = counts[counts.index.notna()]
        lowest = int(non_null.min())
        highest = int(non_null.max())
        for category, count in counts.items():
            records.append(
                {
                    "atributo": attribute,
                    "categoria": "AUSENTE" if pd.isna(category) else str(category),
                    "quantidade": int(count),
                    "percentual": 100 * int(count) / len(values),
                    "menor_categoria_atributo": lowest,
                    "maior_categoria_atributo": highest,
                    "razao_maior_menor": highest / lowest,
                    "menos_de_1_pct": 100 * int(count) / len(values) < 1,
                    "menos_de_5_pct": 100 * int(count) / len(values) < 5,
                }
            )
    return pd.DataFrame(records)


def validate(data: pd.DataFrame, categories: dict[str, pd.Series], frequencies: pd.DataFrame) -> None:
    if len(data) != 10_000:
        raise ValueError(f"Esperados 10.000 registros; encontrados {len(data)}")
    if set(categories) != set(ATTRIBUTES):
        raise ValueError("A simulação não contém exatamente os oito atributos aprováveis.")
    for attribute, values in categories.items():
        if len(values) != len(data) or values.isna().any():
            raise ValueError(f"A discretização simulada de {attribute} não cobre todos os registros.")
        if values.astype(str).str.fullmatch(r"0(?:\.0+)?").any():
            raise ValueError(f"{attribute} reteve zero numérico como categoria.")
    if frequencies["menos_de_1_pct"].any() or frequencies["menos_de_5_pct"].any():
        rare = frequencies.loc[frequencies["menos_de_5_pct"], ["atributo", "categoria", "percentual"]]
        raise ValueError(f"Categorias raras exigem revisão da proposta: {rare.to_dict('records')}")


def decisions_markdown(frequencies: pd.DataFrame) -> str:
    summary = frequencies.groupby("atributo").agg(
        categorias=("categoria", "count"),
        menor_percentual=("percentual", "min"),
        maior_percentual=("percentual", "max"),
        razao_maior_menor=("razao_maior_menor", "max"),
    )
    lines = [
        "# Decisões de discretização — Etapa 3",
        "",
        "## Situação",
        "",
        "Esta é uma proposta simulada sobre a amostra original de 10.000 registros. Nenhuma base Apriori foi criada nesta etapa. A aplicação efetiva das faixas depende de aprovação expressa.",
        "",
        "## Princípios aplicados",
        "",
        "- Não foram usados intervalos de mesma largura.",
        "- Crédito e renda usam quartis reais para resistir às caudas e aos outliers; renda possui máximo de R$ 117.000.000.",
        "- Idade usa grupos de ciclo de vida e foi comparada aos quartis, mantendo todas as faixas acima de 12% da amostra.",
        "- Contagens e taxas preservam zero real como rótulo nominal, requisito indispensável antes do futuro `treatZeroAsMissing=true`.",
        "- Códigos categóricos foram recuperados em rótulos e não são tratados como magnitudes numéricas.",
        "- A categoria familiar `Unknown` (um registro) foi incorporada a `SEPARADO_VIUVO_OU_NAO_INFORMADO`, eliminando categoria menor que 1%.",
        "",
        "## Validação de frequências simuladas",
        "",
        "| Atributo | Categorias | Menor categoria | Maior categoria | Razão maior/menor |",
        "|---|---:|---:|---:|---:|",
    ]
    for attribute, row in summary.loc[ATTRIBUTES].iterrows():
        lines.append(f"| {attribute} | {int(row['categorias'])} | {row['menor_percentual']:.2f}% | {row['maior_percentual']:.2f}% | {row['razao_maior_menor']:.2f} |")
    lines += [
        "",
        "Nenhuma categoria simulada ficou abaixo de 5% da amostra; portanto, não há exceção de baixa frequência a justificar nesta proposta.",
        "",
        "## Decisão pendente",
        "",
        "A lista de oito atributos e as faixas descritas em `resultados/discretizacao/proposta_faixas.csv` aguardam aprovação. A próxima etapa somente poderá criar a base discretizada após essa autorização.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(SOURCE, sep=";", low_memory=False)
    missing = sorted(set(ATTRIBUTES) - set(data.columns))
    if missing:
        raise ValueError(f"Atributos recomendados ausentes da origem: {missing}")
    categories = as_categories(data)
    frequencies = frequency_table(categories)
    validate(data, categories, frequencies)
    pd.DataFrame(proposal_rows()).to_csv(RESULTS / "proposta_faixas.csv", sep=";", index=False)
    frequencies.to_csv(RESULTS / "frequencias_simuladas.csv", sep=";", index=False, float_format="%.6f")
    DECISIONS.write_text(decisions_markdown(frequencies), encoding="utf-8")
    print("Proposta de discretização validada para 8 atributos e 10.000 registros.")
    print("Categorias raras (<5%): 0")
    print(f"Resultados: {RESULTS}")


if __name__ == "__main__":
    main()
