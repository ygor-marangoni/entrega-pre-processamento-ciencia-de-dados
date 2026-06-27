#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atualiza o relatorio Markdown e DOCX com resultados reais do WEKA."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape
import re

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
TRABALHO_DIR = SCRIPT_DIR.parent
RESULTS_DIR = TRABALHO_DIR / "resultados"
REPORT_DIR = TRABALHO_DIR / "relatorio"
REPORT_MD = REPORT_DIR / "relatorio_classificacao.md"
REPORT_DOCX = REPORT_DIR / "relatorio_classificacao_abnt.docx"
RESULTS_CSV = RESULTS_DIR / "resultados_classificacao.csv"
COMPARISON_CSV = RESULTS_DIR / "comparativo_metricas.csv"
ATTRIBUTES_TXT = RESULTS_DIR / "atributos_relevantes_j48.txt"
IMAGES_DIR = REPORT_DIR / "imagens"


METRIC_COLUMNS = [
    "acuracia",
    "tp_rate_classe_1",
    "fp_rate_classe_1",
    "precision_classe_1",
    "recall_classe_1",
    "f_measure_classe_1",
    "roc_area_classe_1",
]


def numeric(value: object) -> float | None:
    try:
        if pd.isna(value) or str(value) == "NA":
            return None
        return float(str(value).replace(",", "."))
    except ValueError:
        return None


def fmt(value: object) -> str:
    number = numeric(value)
    if number is None:
        return "NA"
    return f"{number:.4f}".rstrip("0").rstrip(".")


def read_attributes() -> list[str]:
    if not ATTRIBUTES_TXT.exists():
        return []
    attrs = []
    for raw_line in ATTRIBUTES_TXT.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#"):
            attrs.append(line)
    return attrs


def has_real_results(df: pd.DataFrame) -> bool:
    if df.empty or "status" not in df.columns:
        return False
    ok = df[df["status"].astype(str).str.upper() == "OK"].copy()
    if ok.empty:
        return False
    return ok["acuracia"].apply(numeric).notna().any()


def result_table(df: pd.DataFrame, base_name: str) -> str:
    rows = [
        "| Método | Base | Acurácia | TP Rate classe 1 | FP Rate classe 1 | Precision classe 1 | Recall classe 1 | F-Measure classe 1 | ROC Area classe 1 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    order = ["J48", "RandomForest", "IBk", "NaiveBayes", "BayesNet"]
    for method in order:
        match = df[(df["metodo"] == method) & (df["base"] == base_name)]
        if match.empty:
            values = ["NA"] * 7
        else:
            row = match.iloc[0]
            values = [fmt(row[col]) for col in METRIC_COLUMNS]
        rows.append(f"| {method} | {base_name} | " + " | ".join(values) + " |")
    return "\n".join(rows)


def confusion_text(df: pd.DataFrame, base_name: str) -> str:
    lines = []
    for _, row in df[df["base"] == base_name].iterrows():
        matrix = row.get("matriz_confusao", "NA")
        if pd.isna(matrix):
            matrix = "NA"
        lines.append(f"**{row['metodo']}**: `{matrix}`")
    return "\n\n".join(lines) if lines else "Matrizes não disponíveis."


def best_rows(comparison: pd.DataFrame) -> tuple[str, str]:
    df = comparison.copy()
    for col in ["acuracia", "f_measure_classe_1", "recall_classe_1"]:
        df[col + "_num"] = df[col].apply(numeric)

    best_general = df.dropna(subset=["acuracia_num"]).sort_values("acuracia_num", ascending=False).head(1)
    best_class = df.dropna(subset=["f_measure_classe_1_num"]).sort_values(
        ["f_measure_classe_1_num", "recall_classe_1_num"], ascending=False
    ).head(1)

    general = "não identificado"
    class_one = "não identificado"
    if not best_general.empty:
        row = best_general.iloc[0]
        general = f"{row['metodo']} na base {row['base']} (acurácia {fmt(row['acuracia'])})"
    if not best_class.empty:
        row = best_class.iloc[0]
        class_one = (
            f"{row['metodo']} na base {row['base']} "
            f"(F-Measure classe 1 {fmt(row['f_measure_classe_1'])}; Recall {fmt(row['recall_classe_1'])})"
        )
    return general, class_one


def bayesnet_note(results: pd.DataFrame) -> str:
    notes = []
    match = results[(results["metodo"] == "BayesNet") & (results["base"] == "Completa")]

    if not match.empty:
        row = match.iloc[0]
        status = str(row.get("status", "")).upper()
        output_file = str(row.get("arquivo", ""))

        if status == "OK" and "BayesNet_retry" in output_file:
            notes.append(
                "O BayesNet da base completa foi concluido em nova tentativa com configuracao ajustada "
                "para reduzir consumo de memoria: ADTree desativada, busca K2 com no maximo 1 pai "
                "e SimpleEstimator com alpha 1.0. A execucao continuou sendo feita no WEKA real "
                "com validacao cruzada de 10 folds."
            )
        elif status == "FALHA":
            notes.append(
                "BayesNet nao foi concluido na base completa devido a OutOfMemoryError, mesmo apos "
                "tentativa com configuracao mais economica de memoria."
            )

    reduced = results[(results["metodo"] == "BayesNet") & (results["base"] == "Reduzida")]
    if not reduced.empty and str(reduced.iloc[0].get("status", "")).upper() == "OK":
        notes.append(
            "Na base reduzida, o BayesNet tambem foi executado com a configuracao ajustada "
            "para manter a comparacao viavel computacionalmente."
        )

    return "\n\n".join(notes)


def image_links() -> str:
    files = [
        ("Comparativo de acurácia", "comparativo_acuracia.png"),
        ("Comparativo de Recall da classe 1", "comparativo_recall_classe_1.png"),
        ("Comparativo de F-Measure da classe 1", "comparativo_fmeasure_classe_1.png"),
        ("Comparativo de ROC Area", "comparativo_roc_area.png"),
    ]
    lines = []
    for title, filename in files:
        if (IMAGES_DIR / filename).exists():
            lines.append(f"![{title}](imagens/{filename})")
    return "\n\n".join(lines)


def build_report(results: pd.DataFrame, comparison: pd.DataFrame, attributes: list[str]) -> str:
    best_general, best_class_one = best_rows(comparison)
    bayesnet_adjustment = bayesnet_note(results)
    bayesnet_paragraph = f"\n\n{bayesnet_adjustment}" if bayesnet_adjustment else ""
    attrs_md = "\n".join(f"| {i} | `{attr}` |" for i, attr in enumerate(attributes, 1))
    if not attrs_md:
        attrs_md = "| 1 | Não foi possível extrair atributos automaticamente. Revisar `J48.txt`. |"

    graphs = image_links()
    graph_section = f"\n### 11.1 Visualização dos resultados\n\n{graphs}\n" if graphs else ""

    return f"""# UNIVERSIDADE FEDERAL DE UBERLÂNDIA
# FACULDADE DE COMPUTAÇÃO

**Gil Antony Borba**  
**Raphael Muniz Varela**  
**Victor Leal**  
**Ygor Marangoni**

# RELATÓRIO DE CLASSIFICAÇÃO PARA CONCESSÃO DE CRÉDITO

Trabalho Prático 2 apresentado à disciplina de Ciência de Dados da Universidade Federal de Uberlândia, como requisito parcial de avaliação.

Professor: Carlos Cesar Mansur Tuma

Monte Carmelo - MG  
2026

---

# SUMÁRIO

1. Introdução  
2. Descrição do problema  
3. Descrição da tarefa de classificação  
4. Descrição da base utilizada  
5. Pré-processamento herdado do Trabalho 1  
6. Métodos de classificação  
7. Configurações das execuções  
8. Resultados da base completa  
9. Seleção de atributos com J48  
10. Resultados da base reduzida  
11. Comparação dos resultados  
12. Análise crítica  
13. Conclusão  
14. Referências  
15. Apêndices  

## 1. Introdução

Este relatório apresenta o Trabalho Prático 2 da disciplina de Ciência de Dados, cujo foco foi aplicar e comparar métodos de classificação sobre a base final gerada no Trabalho Prático 1. A tarefa foi executada no WEKA real, via `weka.jar`, com validação cruzada de 10 folds.

## 2. Descrição do problema

O problema tratado é uma classificação binária para concessão de crédito. A variável alvo é `TARGET`, em que `0` representa cliente saudável e `1` representa cliente de risco. Como a classe `1` é minoritária, a análise não pode depender apenas da acurácia.

## 3. Descrição da tarefa de classificação

Foram executadas duas rodadas. Na primeira, os classificadores usaram a base completa. Na segunda, os classificadores foram reexecutados com uma base reduzida formada pelos atributos encontrados na árvore J48.

## 4. Descrição da base utilizada

A base usada foi `base_final_preprocessada.csv`, produzida no Trabalho 1. O campo `SK_ID_CURR` foi removido por ser apenas identificador. A variável `TARGET` foi mantida como última coluna e usada como classe no WEKA.

| Item | Valor |
|---|---:|
| Registros | 307.511 |
| Atributos de entrada | 39 |
| Classe | `TARGET` |
| Classe 0 | 282.686 (91,93%) |
| Classe 1 | 24.825 (8,07%) |

## 5. Pré-processamento herdado do Trabalho 1

O Trabalho 2 não refez o pré-processamento. Foram reaproveitadas as etapas do Trabalho 1: integração das três bases, agregação dos históricos externo e interno, tratamento de ausentes, codificação de categorias e geração da base final.

## 6. Métodos de classificação

Foram avaliados cinco classificadores do WEKA: J48, RandomForest, IBk, NaiveBayes e BayesNet. O J48 também foi usado para auxiliar na seleção de atributos relevantes.

## 7. Configurações das execuções

As execuções foram feitas por linha de comando com `java -Xmx8g -cp weka.jar`, validação cruzada com 10 folds, classe na última coluna e seed 42. As configurações específicas foram: J48 com `-C 0.25 -M 2`, RandomForest com `-I 100 -S 42`, IBk com `-K 5`, NaiveBayes padrão e BayesNet padrão na primeira tentativa.{bayesnet_paragraph}

## 8. Resultados da base completa

{result_table(comparison, "Completa")}

### 8.1 Matrizes de confusão da base completa

{confusion_text(results, "Completa")}

## 9. Seleção de atributos com J48

Os atributos abaixo foram extraídos da árvore gerada pelo J48 na primeira rodada.

| Ordem | Atributo selecionado pelo J48 |
|---:|---|
{attrs_md}

## 10. Resultados da base reduzida

{result_table(comparison, "Reduzida")}

## 11. Comparação dos resultados

{result_table(comparison, "Completa")}

{result_table(comparison, "Reduzida")}
{graph_section}
## 12. Análise crítica

O melhor desempenho geral por acurácia foi obtido por {best_general}. Para a classe `1`, mais importante neste problema por representar clientes de risco, o melhor desempenho observado foi {best_class_one}.

Como a base é fortemente desbalanceada, a acurácia foi analisada com cautela. As métricas da classe `1`, principalmente Recall, F-Measure e ROC Area, são mais adequadas para avaliar a capacidade de identificar clientes de risco.

## 13. Conclusão

O trabalho executou os cinco métodos solicitados no WEKA, comparou os resultados na base completa e na base reduzida e utilizou o J48 para apoiar a seleção de atributos. A análise reforça que, em bases desbalanceadas, a escolha do melhor classificador deve considerar métricas específicas da classe minoritária.

## 14. Referências

HAN, J.; KAMBER, M.; PEI, J. Data Mining: Concepts and Techniques. 3. ed. Waltham: Morgan Kaufmann, 2011.

QUINLAN, J. R. C4.5: Programs for Machine Learning. San Mateo: Morgan Kaufmann, 1993.

WITTEN, I. H.; FRANK, E.; HALL, M. A.; PAL, C. J. Data Mining: Practical Machine Learning Tools and Techniques. 4. ed. Cambridge: Morgan Kaufmann, 2016.

## 15. Apêndices

### Apêndice A - Comandos utilizados

```bash
cd trabalho_2_classificacao/scripts
python localizar_weka.py
python pipeline_trabalho_2.py
```

### Apêndice B - Arquivos gerados

- `data/base_weka_completa.arff`
- `data/base_weka_reduzida.arff`
- `resultados/rodada_1_base_completa/*.txt`
- `resultados/rodada_2_base_reduzida/*.txt`
- `resultados/resultados_classificacao.csv`
- `resultados/comparativo_metricas.csv`
- `resultados/atributos_relevantes_j48.txt`
"""


def clean_inline(value: str) -> str:
    value = value.replace("**", "").replace("`", "")
    value = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", value)
    return value.strip()


def p_xml(value: str, style: str | None = None, align: str | None = None) -> str:
    value = clean_inline(value)
    ppr = ""
    if style or align:
        parts = []
        if style:
            parts.append(f'<w:pStyle w:val="{style}"/>')
        if align:
            parts.append(f'<w:jc w:val="{align}"/>')
        ppr = "<w:pPr>" + "".join(parts) + "</w:pPr>"
    return f'<w:p>{ppr}<w:r><w:t xml:space="preserve">{escape(value)}</w:t></w:r></w:p>'


def markdown_to_docx(markdown: str, output_path: Path) -> None:
    body = []
    in_code = False
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if not line or line == "---":
            body.append("<w:p/>")
        elif in_code:
            body.append(p_xml(line, style="Code"))
        elif line.startswith("# "):
            body.append(p_xml(line[2:], style="Title", align="center"))
        elif line.startswith("## "):
            body.append(p_xml(line[3:], style="Heading1"))
        elif line.startswith("### "):
            body.append(p_xml(line[4:], style="Heading2"))
        elif line.startswith("|"):
            body.append(p_xml(line, style="Code"))
        elif line.startswith("- "):
            body.append(p_xml(line))
        else:
            body.append(p_xml(line))

    sect = (
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1701" w:right="1134" w:bottom="1134" w:left="1701" '
        'w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>'
    )
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>" + "".join(body) + sect + "</w:body></w:document>"
    )
    styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:pPr><w:spacing w:after="160" w:line="360" w:lineRule="auto"/><w:jc w:val="both"/></w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="24"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="240"/><w:jc w:val="center"/></w:pPr><w:rPr><w:b/><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="28"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="320" w:after="160"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:b/><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="28"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="240" w:after="120"/><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:b/><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="26"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Code"><w:name w:val="Code"/><w:basedOn w:val="Normal"/><w:pPr><w:jc w:val="left"/></w:pPr><w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/><w:sz w:val="18"/></w:rPr></w:style>
</w:styles>"""
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        "</Relationships>"
    )
    doc_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        "</Relationships>"
    )
    with ZipFile(output_path, "w", ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", document_xml)
        z.writestr("word/styles.xml", styles_xml)
        z.writestr("word/_rels/document.xml.rels", doc_rels)


def main() -> None:
    if not RESULTS_CSV.exists() or not COMPARISON_CSV.exists():
        raise FileNotFoundError("Execute gerar_tabelas_relatorio.py antes de atualizar o relatorio.")

    results = pd.read_csv(RESULTS_CSV, sep=";")
    comparison = pd.read_csv(COMPARISON_CSV, sep=";")
    if not has_real_results(results):
        print("Relatorio nao foi atualizado porque ainda nao ha resultados reais do WEKA.")
        return

    markdown = build_report(results, comparison, read_attributes())
    REPORT_MD.write_text(markdown, encoding="utf-8")
    markdown_to_docx(markdown, REPORT_DOCX)
    print(f"Relatorio Markdown atualizado: {REPORT_MD}")
    print(f"Relatorio DOCX atualizado: {REPORT_DOCX}")


if __name__ == "__main__":
    main()
