#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrai e ranqueia atributos usados pela arvore J48 e gera a base reduzida."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

from preparar_bases_weka import (
    DEFAULT_COMPLETE_CSV,
    DEFAULT_REDUCED_ARFF,
    DEFAULT_REDUCED_CSV,
    TARGET_COL,
    TRABALHO_DIR,
    prepare_reduced_base,
)


DEFAULT_J48_TXT = TRABALHO_DIR / "resultados" / "rodada_1_base_completa" / "J48.txt"
DEFAULT_OUTPUT = TRABALHO_DIR / "resultados" / "atributos_relevantes_j48.txt"
DEFAULT_RANKING = TRABALHO_DIR / "resultados" / "ranking_atributos_j48.csv"
DEFAULT_TOP_N = 15

TREE_START_MARKERS = ("J48 pruned tree", "J48 unpruned tree")
TREE_END_MARKERS = (
    "Number of Leaves",
    "Size of the tree",
    "Time taken to build model",
    "=== Evaluation",
    "Correctly Classified Instances",
)
ATTRIBUTE_PATTERN = re.compile(r"^\s*(?:\|\s*)*'?([A-Za-z_][A-Za-z0-9_]*)'?\s*(?:<=|>=|<|>|=)\s*")


def load_attribute_ids(input_csv: Path = DEFAULT_COMPLETE_CSV) -> dict[str, int]:
    with input_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)
    return {name: index + 1 for index, name in enumerate(header) if name != TARGET_COL}


def extract_tree_block(text: str) -> list[str]:
    lines = text.splitlines()
    start_index = None
    for index, line in enumerate(lines):
        if any(marker in line for marker in TREE_START_MARKERS):
            start_index = index + 1
            break

    if start_index is None:
        return []

    block = []
    for line in lines[start_index:]:
        if any(marker in line for marker in TREE_END_MARKERS):
            break
        block.append(line)
    return block


def tree_depth(line: str) -> int:
    return line.count("|")


def extract_attribute_ranking(text: str, attribute_ids: dict[str, int]) -> list[dict[str, object]]:
    stats: dict[str, dict[str, object]] = {}
    for line in extract_tree_block(text):
        if ":" in line:
            line = line.split(":", 1)[0]
        match = ATTRIBUTE_PATTERN.match(line)
        if not match:
            continue
        attribute = match.group(1)
        if attribute == TARGET_COL:
            continue
        depth = tree_depth(line)
        current = stats.setdefault(
            attribute,
            {
                "atributo": attribute,
                "id_atributo": attribute_ids.get(attribute, 0),
                "ocorrencias": 0,
                "menor_profundidade": depth,
                "score_j48": 0.0,
            },
        )
        current["ocorrencias"] = int(current["ocorrencias"]) + 1
        current["menor_profundidade"] = min(int(current["menor_profundidade"]), depth)
        # Repeticoes contam, mas perdem peso conforme o no fica mais distante da raiz.
        current["score_j48"] = float(current["score_j48"]) + (1 / (depth + 1))

    ranking = list(stats.values())
    ranking.sort(
        key=lambda row: (
            int(row["menor_profundidade"]),
            -float(row["score_j48"]),
            -int(row["ocorrencias"]),
            int(row["id_atributo"]),
            str(row["atributo"]),
        )
    )
    for position, row in enumerate(ranking, start=1):
        row["rank_j48"] = position
        row["score_j48"] = round(float(row["score_j48"]), 6)
    return ranking


def select_attributes(ranking: list[dict[str, object]], top_n: int) -> list[str]:
    return [str(row["atributo"]) for row in ranking[:top_n]]


def write_ranking_file(ranking: list[dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    columns = ["rank_j48", "id_atributo", "atributo", "ocorrencias", "menor_profundidade", "score_j48"]
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, delimiter=";")
        writer.writeheader()
        writer.writerows(ranking)


def write_attributes_file(attributes: list[str], output_path: Path, source_path: Path, top_n: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if attributes:
        content = [
            "# Atributos relevantes selecionados automaticamente da arvore J48",
            f"# Origem: {source_path}",
            f"# Criterio: top {top_n} priorizando menor profundidade na arvore J48 e, depois, ocorrencia ponderada.",
            "# Ranking completo: resultados/ranking_atributos_j48.csv",
            "# Um atributo por linha; esta lista e a entrada da base reduzida da etapa 2.",
            "",
            *attributes,
            "",
        ]
    else:
        content = [
            "# Atributos relevantes do J48",
            "# A extracao automatica ainda nao encontrou atributos.",
            "# Possiveis motivos:",
            "# - O arquivo J48.txt ainda nao foi gerado pelo WEKA.",
            "# - A saida do WEKA esta em formato diferente do esperado.",
            "# - A arvore nao aparece no arquivo textual.",
            "#",
            "# Preencha manualmente abaixo, um atributo por linha, observando a arvore J48.",
            "# Depois rode novamente:",
            "# python extrair_atributos_j48.py",
            "",
            "# EXEMPLO:",
            "# EXT_SOURCE_2",
            "# EXT_SOURCE_3",
            "# CREDIT_INCOME_RATIO",
            "",
        ]
    output_path.write_text("\n".join(content), encoding="utf-8")


def read_manual_attributes(path: Path) -> list[str]:
    if not path.exists():
        return []
    attributes = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        attributes.append(line)
    return attributes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extrai atributos do J48 e gera base reduzida.")
    parser.add_argument("--j48", type=Path, default=DEFAULT_J48_TXT, help="Arquivo textual gerado pelo J48.")
    parser.add_argument("--saida", type=Path, default=DEFAULT_OUTPUT, help="Arquivo com atributos relevantes.")
    parser.add_argument("--ranking", type=Path, default=DEFAULT_RANKING, help="CSV com ranking completo dos atributos.")
    parser.add_argument(
        "--top-n",
        type=int,
        default=DEFAULT_TOP_N,
        help=f"Quantidade de atributos selecionados para a base reduzida. Padrao: {DEFAULT_TOP_N}.",
    )
    parser.add_argument(
        "--usar-manual",
        action="store_true",
        help="Usa os atributos ja preenchidos no arquivo de saida, sem tentar ler J48.txt.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    attributes: list[str] = []
    ranking: list[dict[str, object]] = []

    if args.top_n < 1:
        raise ValueError("--top-n precisa ser maior ou igual a 1.")

    if args.usar_manual:
        attributes = read_manual_attributes(args.saida)
    elif args.j48.exists():
        attribute_ids = load_attribute_ids(DEFAULT_COMPLETE_CSV)
        ranking = extract_attribute_ranking(args.j48.read_text(encoding="utf-8", errors="replace"), attribute_ids)
        write_ranking_file(ranking, args.ranking)
        attributes = select_attributes(ranking, args.top_n)
        if not attributes:
            attributes = read_manual_attributes(args.saida)
    else:
        print(f"Arquivo J48 ainda nao encontrado: {args.j48}")

    write_attributes_file(attributes, args.saida, args.j48, args.top_n)

    if not attributes:
        print(f"Template criado em: {args.saida}")
        print("Preencha os atributos apos executar o J48 e rode este script novamente.")
        return

    reduced = prepare_reduced_base(attributes, DEFAULT_COMPLETE_CSV)
    print("Atributos selecionados para a etapa 2:")
    for attribute in attributes:
        print(f"- {attribute}")
    if ranking:
        print(f"Ranking completo: {args.ranking}")
    print(f"Base reduzida gerada com {len(reduced.columns) - 1} atributos de entrada.")
    print(f"CSV: {DEFAULT_REDUCED_CSV}")
    print(f"ARFF: {DEFAULT_REDUCED_ARFF}")


if __name__ == "__main__":
    main()
