"""Audita atributos candidatos para regras de associação (Etapa 2).

Lê exclusivamente a amostra auxiliar original do Trabalho 3, sem alterá-la.
Os resultados são exploratórios: a recomendação dos oito atributos depende de
aprovação expressa antes de qualquer discretização ou geração de base Apriori.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "trabalho_3_clusterizacao" / "data" / "amostras" / "base_amostra_10000_analise.csv"
DICTIONARY = ROOT / "trabalho_1_preprocessamento" / "data" / "dicionario_codificacao_categorias.csv"
RESULTS = ROOT / "trabalho_4_regras_associacao" / "resultados" / "exploracao"
IMAGES = ROOT / "trabalho_4_regras_associacao" / "relatorio" / "imagens" / "exploracao"

CANDIDATES = [
    "AMT_CREDIT", "AMT_INCOME_TOTAL", "AGE_YEARS", "CNT_CHILDREN",
    "FLAG_OWN_CAR_COD", "NAME_FAMILY_STATUS_COD", "CREDIT_INCOME_RATIO",
    "REGION_RATING_CLIENT", "SER_CREDITOS_ATIVOS", "SER_QTDE_EMPRESTIMOS",
    "PREV_QTDE_TENTATIVAS", "PREV_TAXA_REJEICAO", "SER_DIVIDA_ATRASADA",
]
CATEGORICAL = {"FLAG_OWN_CAR_COD", "NAME_FAMILY_STATUS_COD", "REGION_RATING_CLIENT"}

RECOMMENDED = {
    "AMT_CREDIT": ("Incluído por representar diretamente o porte do crédito solicitado.", "Faixas robustas por percentis/quartis, avaliando a cauda superior."),
    "AMT_INCOME_TOTAL": ("Incluído por ser indicador central da capacidade econômica do cliente.", "Faixas por percentis, com atenção explícita aos extremos de renda."),
    "AGE_YEARS": ("Incluído para representar estágio de vida com interpretação direta.", "Comparar grupos etários semânticos com quartis observados."),
    "CNT_CHILDREN": ("Incluído por sintetizar composição familiar em poucas categorias naturais.", "Agrupar em sem filhos, um filho e dois ou mais, se as frequências confirmarem."),
    "FLAG_OWN_CAR_COD": ("Incluído como dimensão patrimonial simples e comercialmente interpretável.", "Recuperar como SEM_CARRO e COM_CARRO; não manter códigos numéricos."),
    "NAME_FAMILY_STATUS_COD": ("Incluído para complementar a composição familiar com rótulos recuperados.", "Usar categorias nominais do dicionário; fundir somente categorias raras justificadas."),
    "SER_CREDITOS_ATIVOS": ("Incluído por medir intensidade do relacionamento de crédito ativo.", "Criar faixas a partir de zero semântico e agrupamentos frequentes positivos."),
    "PREV_TAXA_REJEICAO": ("Incluído por trazer histórico de rejeição em dimensão distinta de renda e crédito.", "Separar zero semântico de faixas positivas definidas por percentis e frequência."),
}
DISCARDED = {
    "CREDIT_INCOME_RATIO": ("Descartado por ser derivado matematicamente de crédito e renda, já incluídos.", "Sua inclusão tenderia a produzir associações estruturalmente óbvias."),
    "REGION_RATING_CLIENT": ("Descartado por ter baixa granularidade e risco de concentração dominante.", "Pode limitar a diversidade das regras frente a atributos de perfil e histórico."),
    "SER_QTDE_EMPRESTIMOS": ("Descartado para reduzir sobreposição com SER_CREDITOS_ATIVOS no histórico Serasa.", "Permanece como alternativa caso a etapa de discretização revele baixa utilidade do atributo incluído."),
    "PREV_QTDE_TENTATIVAS": ("Descartado para evitar sobreposição com PREV_TAXA_REJEICAO, que resume o resultado das tentativas.", "A taxa preserva melhor a comparabilidade entre diferentes volumes de tentativas."),
    "SER_DIVIDA_ATRASADA": ("Descartado devido à concentração esperada em zero, a ser confirmada pelas estatísticas.", "A categoria dominante poderia produzir regras frequentes, porém pouco informativas."),
}


def code_key(value: object) -> str:
    try:
        numeric = float(value)
        return str(int(numeric)) if numeric.is_integer() else str(numeric)
    except (TypeError, ValueError):
        return str(value)


def category_labels() -> dict[str, dict[str, str]]:
    dictionary = pd.read_csv(DICTIONARY, sep=";", dtype={"CODIGO": str})
    labels: dict[str, dict[str, str]] = {}
    for field, rows in dictionary.groupby("CAMPO_ORIGINAL"):
        labels[field] = {code_key(code): str(category) for code, category in zip(rows["CODIGO"], rows["CATEGORIA"])}
    labels["FLAG_OWN_CAR_COD"] = {"0": "SEM_CARRO", "1": "COM_CARRO"}
    labels["NAME_FAMILY_STATUS_COD"] = labels.get("NAME_FAMILY_STATUS", {})
    labels["REGION_RATING_CLIENT"] = {"1": "REGIAO_RATING_1", "2": "REGIAO_RATING_2", "3": "REGIAO_RATING_3"}
    return labels


def fmt(value: object, decimals: int = 6) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, (int, float, np.integer, np.floating)):
        return f"{float(value):.{decimals}f}"
    return str(value)


def numeric_statistics(series: pd.Series) -> dict[str, object]:
    numeric = pd.to_numeric(series, errors="coerce")
    valid = numeric.dropna()
    q1, q3 = valid.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers = int(((valid < lower) | (valid > upper)).sum())
    mode = valid.mode()
    mode_value = mode.iloc[0] if not mode.empty else np.nan
    dominant_count = int((valid == mode_value).sum()) if not mode.empty else 0
    return {
        "minimo": valid.min(), "maximo": valid.max(), "media": valid.mean(), "mediana": valid.median(), "moda": mode_value,
        "p05": valid.quantile(0.05), "p10": valid.quantile(0.10), "p25": q1, "p50": valid.quantile(0.50),
        "p75": q3, "p90": valid.quantile(0.90), "p95": valid.quantile(0.95), "p99": valid.quantile(0.99),
        "valores_unicos": int(valid.nunique()), "ausentes": int(numeric.isna().sum()), "zeros": int((valid == 0).sum()),
        "percentual_zeros": 100 * float((valid == 0).mean()), "assimetria": valid.skew(), "outliers_iqr": outliers,
        "percentual_outliers_iqr": 100 * outliers / len(valid), "categoria_dominante": mode_value,
        "frequencia_dominante": dominant_count, "concentracao_dominante_pct": 100 * dominant_count / len(valid),
    }


def categorical_statistics(series: pd.Series, labels: dict[str, str]) -> tuple[dict[str, object], pd.DataFrame]:
    normalized = series.map(code_key)
    frequencies = normalized.value_counts(dropna=False)
    rows = []
    for code, count in frequencies.items():
        is_missing = code == "nan"
        rows.append({"codigo": "" if is_missing else code, "categoria": "AUSENTE" if is_missing else labels.get(code, f"CODIGO_{code}"), "frequencia": int(count), "percentual": 100 * int(count) / len(series)})
    frequency_df = pd.DataFrame(rows)
    valid = frequency_df[frequency_df["categoria"] != "AUSENTE"].copy()
    dominant = valid.iloc[0] if not valid.empty else None
    zero_count = int((normalized == "0").sum())
    stats = {key: np.nan for key in ["minimo", "maximo", "media", "mediana", "p05", "p10", "p25", "p50", "p75", "p90", "p95", "p99", "assimetria", "outliers_iqr", "percentual_outliers_iqr"]}
    stats.update({"moda": dominant["categoria"] if dominant is not None else np.nan, "valores_unicos": int(valid.shape[0]), "ausentes": int(series.isna().sum()), "zeros": zero_count, "percentual_zeros": 100 * zero_count / len(series), "categoria_dominante": dominant["categoria"] if dominant is not None else np.nan, "frequencia_dominante": int(dominant["frequencia"]) if dominant is not None else 0, "concentracao_dominante_pct": float(dominant["percentual"]) if dominant is not None else np.nan})
    return stats, frequency_df


def make_charts(data: pd.DataFrame, labels: dict[str, dict[str, str]]) -> None:
    numeric_columns = [column for column in CANDIDATES if column not in CATEGORICAL]
    fig, axes = plt.subplots(5, 2, figsize=(15, 24))
    for axis, column in zip(axes.flat, numeric_columns):
        axis.hist(pd.to_numeric(data[column], errors="coerce").dropna(), bins=35, color="#2f6690", edgecolor="white")
        axis.set_title(column); axis.set_ylabel("Frequência"); axis.grid(axis="y", alpha=0.25)
    fig.suptitle("Histogramas dos atributos numéricos candidatos", fontsize=16, y=0.995)
    fig.tight_layout(); fig.savefig(IMAGES / "histogramas_atributos_numericos.png", dpi=180, bbox_inches="tight"); plt.close(fig)

    fig, axes = plt.subplots(5, 2, figsize=(15, 24))
    for axis, column in zip(axes.flat, numeric_columns):
        axis.boxplot(pd.to_numeric(data[column], errors="coerce").dropna(), vert=False, showfliers=True, flierprops={"markersize": 2})
        axis.set_title(column); axis.grid(axis="x", alpha=0.25)
    fig.suptitle("Boxplots dos atributos numéricos candidatos", fontsize=16, y=0.995)
    fig.tight_layout(); fig.savefig(IMAGES / "boxplots_atributos_numericos.png", dpi=180, bbox_inches="tight"); plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    for axis, column in zip(axes, sorted(CATEGORICAL)):
        frequencies = data[column].map(code_key).value_counts()
        axis.bar([labels[column].get(code, f"CODIGO_{code}") for code in frequencies.index], frequencies.values, color="#5b8c5a")
        axis.set_title(column); axis.tick_params(axis="x", rotation=30); axis.set_ylabel("Frequência"); axis.grid(axis="y", alpha=0.25)
    fig.suptitle("Frequências dos atributos categóricos candidatos", fontsize=16)
    fig.tight_layout(); fig.savefig(IMAGES / "frequencias_atributos_categoricos.png", dpi=180, bbox_inches="tight"); plt.close(fig)


def markdown_report(stats: pd.DataFrame) -> str:
    lookup = stats.set_index("atributo")
    lines = ["# Análise de atributos candidatos — Etapa 2", "", "## Base analisada", "", "- Origem: `trabalho_3_clusterizacao/data/amostras/base_amostra_10000_analise.csv`.", "- Registros: 10.000; separador: `;`.", "- A leitura é exclusivamente exploratória: nenhuma linha ou valor foi alterado.", "- `TARGET`, `SK_ID_CURR` e `ROW_ID_AMOSTRA` não foram analisados como candidatos e não integrarão o Apriori.", "", "## Oito atributos recomendados — sujeitos a aprovação", ""]
    for attribute, (reason, discretization) in RECOMMENDED.items():
        row = lookup.loc[attribute]
        lines += [f"### {attribute}", "", f"- Motivo: {reason}", f"- Distribuição observada: {int(row['valores_unicos'])} valores/categorias; zeros = {row['percentual_zeros']:.2f}%; concentração dominante = {row['concentracao_dominante_pct']:.2f}%.", "- Vantagem: acrescenta uma dimensão interpretável ao perfil do cliente.", f"- Risco: assimetria = {fmt(row['assimetria'])}; outliers pelo IQR = {fmt(row['percentual_outliers_iqr'])}% quando aplicável.", f"- Discretização provável: {discretization}", ""]
    lines += ["## Cinco atributos descartados — sujeitos a revisão", ""]
    for attribute, (reason, risk) in DISCARDED.items():
        row = lookup.loc[attribute]
        lines += [f"### {attribute}", "", f"- Motivo: {reason}", f"- Distribuição observada: {int(row['valores_unicos'])} valores/categorias; zeros = {row['percentual_zeros']:.2f}%; concentração dominante = {row['concentracao_dominante_pct']:.2f}%.", f"- Risco/decisão: {risk}", ""]
    lines += ["## Observações metodológicas", "", "- `CREDIT_INCOME_RATIO` não é recomendado porque já é função de `AMT_CREDIT` e `AMT_INCOME_TOTAL`; incluí-lo pode produzir regras tautológicas.", "- Zeros ainda são valores originais nesta etapa. Se um zero tiver significado real, a etapa de discretização deverá convertê-lo em rótulo nominal, pois o Apriori será configurado posteriormente com `treatZeroAsMissing=true`.", "- As categorias de carro e estado familiar foram interpretadas com o dicionário do Trabalho 1; códigos não serão tratados como grandezas numéricas.", "- Esta recomendação não gera a base final: a escolha dos oito atributos depende de aprovação expressa."]
    return "\n".join(lines) + "\n"


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True); IMAGES.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(SOURCE, sep=";", low_memory=False)
    missing_columns = sorted(set(CANDIDATES) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Colunas candidatas ausentes: {missing_columns}")
    if len(data) != 10_000:
        raise ValueError(f"A amostra deveria ter 10.000 registros; encontrado: {len(data)}")
    labels = category_labels(); statistics = []; frequencies = []
    for attribute in CANDIDATES:
        if attribute in CATEGORICAL:
            metrics, frequency = categorical_statistics(data[attribute], labels[attribute])
            frequency.insert(0, "atributo", attribute); frequency["dominante"] = frequency["frequencia"].eq(frequency["frequencia"].max()); frequencies.append(frequency); kind = "CATEGORICO"
        else:
            metrics = numeric_statistics(data[attribute]); kind = "NUMERICO"
        statistics.append({"atributo": attribute, "tipo": kind, **metrics})
    stats_df = pd.DataFrame(statistics)
    stats_df.to_csv(RESULTS / "estatisticas_candidatos.csv", sep=";", index=False, float_format="%.6f")
    pd.concat(frequencies, ignore_index=True).to_csv(RESULTS / "frequencias_categoricas.csv", sep=";", index=False, float_format="%.6f")
    (RESULTS / "analise_candidatos.md").write_text(markdown_report(stats_df), encoding="utf-8")
    make_charts(data, labels)
    print(f"Análise concluída: {len(data)} registros e {len(CANDIDATES)} candidatos.")
    print(f"Resultados: {RESULTS}")
    print(f"Gráficos: {IMAGES}")


if __name__ == "__main__":
    main()
