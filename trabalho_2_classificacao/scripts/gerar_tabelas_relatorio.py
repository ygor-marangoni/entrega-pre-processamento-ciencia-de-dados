#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera tabelas CSV a partir das saidas textuais do WEKA."""

from __future__ import annotations

import csv
import re
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
TRABALHO_DIR = SCRIPT_DIR.parent
RESULTS_DIR = TRABALHO_DIR / "resultados"

ROUND_DIRS = {
    "rodada_1_base_completa": ("Rodada 1", "Completa"),
    "rodada_2_base_reduzida": ("Rodada 2", "Reduzida"),
}

METHODS = ["J48", "RandomForest", "IBk", "NaiveBayes", "BayesNet"]
RETRY_OUTPUTS = {
    ("rodada_1_base_completa", "BayesNet"): "BayesNet_retry.txt",
}

OUTPUT_FULL = RESULTS_DIR / "resultados_classificacao.csv"
OUTPUT_COMPARISON = RESULTS_DIR / "comparativo_metricas.csv"


def search_float(pattern: str, text: str) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return "NA"
    value = match.group(1)
    if "," in value:
        return value.replace(".", "").replace(",", ".")
    return value


def parse_correctly_classified(text: str) -> tuple[str, str]:
    match = re.search(r"Correctly Classified Instances\s+(\d+)\s+([\d.,]+)\s*%", text, flags=re.IGNORECASE)
    if not match:
        return "NA", "NA"
    return match.group(1), match.group(2).replace(",", ".")


def parse_incorrectly_classified(text: str) -> tuple[str, str]:
    match = re.search(r"Incorrectly Classified Instances\s+(\d+)\s+([\d.,]+)\s*%", text, flags=re.IGNORECASE)
    if not match:
        return "NA", "NA"
    return match.group(1), match.group(2).replace(",", ".")


def parse_class_one_metrics(text: str) -> dict[str, str]:
    metrics = {
        "tp_rate_classe_1": "NA",
        "fp_rate_classe_1": "NA",
        "precision_classe_1": "NA",
        "recall_classe_1": "NA",
        "f_measure_classe_1": "NA",
        "roc_area_classe_1": "NA",
    }

    in_table = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("TP Rate") and "ROC Area" in line and "Class" in line:
            in_table = True
            continue
        if not in_table:
            continue
        if not line or line.startswith("Weighted Avg"):
            continue
        parts = line.split()
        if len(parts) < 8:
            continue
        class_label = parts[-1]
        if class_label not in {"1", "1.0"}:
            continue
        metrics["tp_rate_classe_1"] = parts[0]
        metrics["fp_rate_classe_1"] = parts[1]
        metrics["precision_classe_1"] = parts[2]
        metrics["recall_classe_1"] = parts[3]
        metrics["f_measure_classe_1"] = parts[4]
        metrics["roc_area_classe_1"] = parts[-3]
        break
    return metrics


def parse_confusion_matrix(text: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if "Confusion Matrix" not in line:
            continue
        matrix_lines = []
        for candidate in lines[index + 1:index + 8]:
            stripped = candidate.strip()
            if not stripped:
                continue
            matrix_lines.append(stripped)
        return " | ".join(matrix_lines) if matrix_lines else "NA"
    return "NA"


def parse_script_time(text: str) -> str:
    return search_float(r"Tempo medido pelo script:\s+([\d.,]+)\s+segundos", text)


def extract_cross_validation_section(text: str) -> str:
    marker = "=== Stratified cross-validation ==="
    marker_index = text.find(marker)
    if marker_index == -1:
        return text
    return text[marker_index:]


def parse_status(text: str) -> str:
    if re.search(r"Status da execucao:\s+FALHA", text, flags=re.IGNORECASE):
        return "FALHA"
    if re.search(r"Status da execucao:\s+OK", text, flags=re.IGNORECASE):
        return "OK"
    return "OK"


def parse_weka_output(path: Path, method: str, round_name: str, base_name: str) -> dict[str, str]:
    if not path.exists():
        return {
            "metodo": method,
            "rodada": round_name,
            "base": base_name,
            "arquivo": str(path),
            "status": "NAO_EXECUTADO",
            "acuracia": "NA",
            "corretas": "NA",
            "incorretas": "NA",
            "kappa": "NA",
            "mean_absolute_error": "NA",
            "root_mean_squared_error": "NA",
            "tp_rate_classe_1": "NA",
            "fp_rate_classe_1": "NA",
            "precision_classe_1": "NA",
            "recall_classe_1": "NA",
            "f_measure_classe_1": "NA",
            "roc_area_classe_1": "NA",
            "matriz_confusao": "NA",
            "tempo_script_segundos": "NA",
        }

    text = path.read_text(encoding="utf-8", errors="replace")
    evaluation_text = extract_cross_validation_section(text)
    correct_count, accuracy = parse_correctly_classified(evaluation_text)
    incorrect_count, _ = parse_incorrectly_classified(evaluation_text)
    row = {
        "metodo": method,
        "rodada": round_name,
        "base": base_name,
        "arquivo": str(path),
        "status": parse_status(text),
        "acuracia": accuracy,
        "corretas": correct_count,
        "incorretas": incorrect_count,
        "kappa": search_float(r"Kappa statistic\s+([-\d.,]+)", evaluation_text),
        "mean_absolute_error": search_float(r"Mean absolute error\s+([-\d.,]+)", evaluation_text),
        "root_mean_squared_error": search_float(r"Root mean squared error\s+([-\d.,]+)", evaluation_text),
        "matriz_confusao": parse_confusion_matrix(evaluation_text),
        "tempo_script_segundos": parse_script_time(text),
    }
    row.update(parse_class_one_metrics(evaluation_text))
    return row


def result_path(folder: Path, round_dir: str, method: str) -> Path:
    retry_name = RETRY_OUTPUTS.get((round_dir, method))
    if retry_name and (folder / retry_name).exists():
        return folder / retry_name
    return folder / f"{method}.txt"


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows: list[dict[str, str]] = []
    for round_dir, (round_name, base_name) in ROUND_DIRS.items():
        folder = RESULTS_DIR / round_dir
        for method in METHODS:
            rows.append(parse_weka_output(result_path(folder, round_dir, method), method, round_name, base_name))

    full_columns = [
        "metodo", "rodada", "base", "arquivo", "status", "acuracia", "corretas", "incorretas",
        "kappa", "mean_absolute_error", "root_mean_squared_error", "tp_rate_classe_1",
        "fp_rate_classe_1", "precision_classe_1", "recall_classe_1", "f_measure_classe_1",
        "roc_area_classe_1", "matriz_confusao", "tempo_script_segundos",
    ]
    comparison_columns = [
        "metodo", "base", "acuracia", "tp_rate_classe_1", "fp_rate_classe_1",
        "precision_classe_1", "recall_classe_1", "f_measure_classe_1",
        "roc_area_classe_1", "tempo_script_segundos",
    ]

    write_csv(OUTPUT_FULL, rows, full_columns)
    write_csv(OUTPUT_COMPARISON, rows, comparison_columns)
    print(f"Tabela completa: {OUTPUT_FULL}")
    print(f"Comparativo: {OUTPUT_COMPARISON}")


if __name__ == "__main__":
    main()
