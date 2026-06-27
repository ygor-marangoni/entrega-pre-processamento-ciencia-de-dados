#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Executa classificadores reais do WEKA com validacao cruzada de 10 folds."""

from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path


CLASSIFIERS = {
    "J48": "weka.classifiers.trees.J48",
    "RandomForest": "weka.classifiers.trees.RandomForest",
    "IBk": "weka.classifiers.lazy.IBk",
    "NaiveBayes": "weka.classifiers.bayes.NaiveBayes",
    "BayesNet": "weka.classifiers.bayes.BayesNet",
}

CLASSIFIER_OPTIONS = {
    "J48": ["-C", "0.25", "-M", "2"],
    "RandomForest": ["-I", "100", "-S", "{seed}"],
    "IBk": ["-K", "5"],
    "NaiveBayes": [],
    "BayesNet": [],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa os metodos de classificacao do WEKA.")
    parser.add_argument("--weka-jar", required=True, type=Path, help="Caminho completo para weka.jar.")
    parser.add_argument("--base", required=True, type=Path, help="Arquivo ARFF usado na execucao.")
    parser.add_argument("--saida", required=True, type=Path, help="Pasta onde os resultados TXT serao salvos.")
    parser.add_argument("--folds", type=int, default=10, help="Quantidade de folds da validacao cruzada.")
    parser.add_argument("--max-memory", default="8g", help="Memoria maxima do Java. Padrao: 8g.")
    parser.add_argument("--seed", type=int, default=42, help="Seed da validacao cruzada e dos metodos aplicaveis.")
    parser.add_argument(
        "--java",
        default="java",
        help="Executavel Java. Use este argumento se o Java nao estiver no PATH.",
    )
    return parser.parse_args()


def validate_inputs(weka_jar: Path, base: Path) -> None:
    if not weka_jar.exists():
        raise FileNotFoundError(
            "weka.jar nao encontrado. Instale o WEKA ou informe o caminho correto, por exemplo: "
            "--weka-jar \"C:/Program Files/Weka-3-8-6/weka.jar\""
        )
    if not base.exists():
        raise FileNotFoundError(f"Base ARFF nao encontrada: {base}")


def classifier_options(name: str, seed: int) -> list[str]:
    return [option.format(seed=seed) for option in CLASSIFIER_OPTIONS.get(name, [])]


def run_classifier(
    java_cmd: str,
    weka_jar: Path,
    base: Path,
    output_dir: Path,
    folds: int,
    max_memory: str,
    seed: int,
    name: str,
    class_path: str,
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = output_dir / f"{name}.txt"
    stderr_path = output_dir / f"{name}.log"

    command = [
        java_cmd,
        f"-Xmx{max_memory}",
        "-cp",
        str(weka_jar),
        class_path,
        "-t",
        str(base),
        "-x",
        str(folds),
        "-s",
        str(seed),
        "-c",
        "last",
        *classifier_options(name, seed),
    ]

    started = time.perf_counter()
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    elapsed = time.perf_counter() - started

    header = [
        f"Metodo: {name}",
        f"Classe WEKA: {class_path}",
        f"Base usada: {base}",
        "Validacao cruzada: sim",
        f"Numero de folds: {folds}",
        f"Seed: {seed}",
        f"Memoria maxima Java: {max_memory}",
        f"Tempo medido pelo script: {elapsed:.2f} segundos",
        "Comando:",
        " ".join(f'"{part}"' if " " in part else part for part in command),
        "",
        "Saida completa do WEKA:",
        "",
    ]
    status_line = "Status da execucao: OK" if completed.returncode == 0 else f"Status da execucao: FALHA ({completed.returncode})"
    stdout_path.write_text("\n".join([status_line, *header]) + completed.stdout, encoding="utf-8")

    if completed.stderr or completed.returncode != 0:
        stderr_path.write_text(completed.stderr or f"Processo finalizou com codigo {completed.returncode}.", encoding="utf-8")
    elif stderr_path.exists():
        stderr_path.unlink()

    return completed.returncode


def main() -> None:
    args = parse_args()
    weka_jar = args.weka_jar.resolve()
    base = args.base.resolve()
    output_dir = args.saida.resolve()
    validate_inputs(weka_jar, base)

    print(f"Executando WEKA na base: {base}")
    print(f"Resultados em: {output_dir}")
    failures = []
    for name, class_path in CLASSIFIERS.items():
        print(f"- {name}...")
        code = run_classifier(
            args.java,
            weka_jar,
            base,
            output_dir,
            args.folds,
            args.max_memory,
            args.seed,
            name,
            class_path,
        )
        if code != 0:
            failures.append(name)
            print(f"  falhou. Verifique {output_dir / (name + '.log')}")
        else:
            print(f"  concluido: {output_dir / (name + '.txt')}")

    if failures:
        print("Execucao concluida com falhas: " + ", ".join(failures))
    else:
        print("Execucao concluida.")


if __name__ == "__main__":
    main()
