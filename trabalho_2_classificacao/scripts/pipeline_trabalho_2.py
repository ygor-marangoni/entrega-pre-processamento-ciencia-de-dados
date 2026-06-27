#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pipeline auxiliar do Trabalho 2.

Sem o weka.jar, o pipeline prepara a base completa e gera os templates.
Com o weka.jar, tambem executa as duas rodadas e consolida metricas.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from preparar_bases_weka import DEFAULT_COMPLETE_ARFF, DEFAULT_REDUCED_ARFF, prepare_complete_base


SCRIPT_DIR = Path(__file__).resolve().parent
TRABALHO_DIR = SCRIPT_DIR.parent
RESULTS_DIR = TRABALHO_DIR / "resultados"
CONFIG_PATH = TRABALHO_DIR / "weka_config.json"


def run_step(command: list[str], description: str, required: bool = True) -> bool:
    print(f"\n==> {description}")
    completed = subprocess.run(command, cwd=SCRIPT_DIR)
    if completed.returncode != 0:
        message = f"Etapa falhou: {description}"
        if required:
            raise SystemExit(message)
        print(message)
        return False
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa o fluxo do Trabalho 2.")
    parser.add_argument("--weka-jar", type=Path, default=None, help="Caminho para weka.jar.")
    parser.add_argument("--java", default="java", help="Executavel Java.")
    parser.add_argument("--max-memory", default=None, help="Memoria maxima do Java. Exemplo: 8g, 10g, 12g.")
    parser.add_argument("--seed", type=int, default=42, help="Seed da validacao cruzada.")
    return parser.parse_args()


def load_config() -> dict[str, str]:
    if not CONFIG_PATH.exists():
        return {}
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def resolve_weka_settings(args: argparse.Namespace) -> tuple[str, Path | None, str]:
    config = load_config()
    java_cmd = args.java or config.get("java_cmd", "java")
    max_memory = args.max_memory or config.get("max_memory", "8g")
    weka_jar = args.weka_jar
    if not weka_jar and config.get("weka_jar"):
        weka_jar = Path(config["weka_jar"])
    if weka_jar:
        weka_jar = weka_jar.resolve()
    return java_cmd, weka_jar, max_memory


def main() -> None:
    args = parse_args()
    java_cmd, weka_jar, max_memory = resolve_weka_settings(args)

    print("1/9 Verificando Java e WEKA...")
    run_step([sys.executable, "localizar_weka.py"], "Localizar Java e WEKA", required=False)
    java_cmd, weka_jar, max_memory = resolve_weka_settings(args)
    if not weka_jar or not weka_jar.exists():
        print("weka.jar nao encontrado. Nao e possivel executar WEKA real sem esse arquivo.")
        print("Informe manualmente, por exemplo:")
        print('python pipeline_trabalho_2.py --weka-jar "C:/Program Files/Weka-3-8-6/weka.jar" --max-memory 8g')
        print("O pipeline vai preparar bases e tabelas NA, mas nao vai simular resultados.")

    print("2/9 Preparando base completa...")
    prepare_complete_base()
    print(f"ARFF completo: {DEFAULT_COMPLETE_ARFF}")

    if not weka_jar or not weka_jar.exists():
        run_step([sys.executable, "extrair_atributos_j48.py"], "Criar template de atributos J48", required=False)
        run_step([sys.executable, "gerar_tabelas_relatorio.py"], "Gerar tabelas vazias/NA", required=False)
        print("9/9 Finalizando...")
        print("Concluido parcialmente: falta localizar o weka.jar para rodar os classificadores reais.")
        return

    print("3/9 Executando rodada 1 com base completa...")
    run_step(
        [
            sys.executable,
            "executar_weka.py",
            "--weka-jar",
            str(weka_jar),
            "--base",
            str(DEFAULT_COMPLETE_ARFF),
            "--saida",
            str(RESULTS_DIR / "rodada_1_base_completa"),
            "--java",
            java_cmd,
            "--max-memory",
            max_memory,
            "--seed",
            str(args.seed),
        ],
        "Rodada 1: base completa",
    )

    print("4/9 Extraindo atributos relevantes do J48...")
    run_step([sys.executable, "extrair_atributos_j48.py"], "Extrair atributos do J48 e gerar base reduzida")

    print("5/9 Gerando base reduzida...")
    if DEFAULT_REDUCED_ARFF.exists():
        print(f"Base reduzida pronta: {DEFAULT_REDUCED_ARFF}")
        print("6/9 Executando rodada 2 com base reduzida...")
        run_step(
            [
                sys.executable,
                "executar_weka.py",
                "--weka-jar",
                str(weka_jar),
                "--base",
                str(DEFAULT_REDUCED_ARFF),
                "--saida",
                str(RESULTS_DIR / "rodada_2_base_reduzida"),
                "--java",
                java_cmd,
                "--max-memory",
                max_memory,
                "--seed",
                str(args.seed),
            ],
            "Rodada 2: base reduzida",
        )
    else:
        print("Base reduzida nao foi gerada. Revise atributos_relevantes_j48.txt.")

    print("7/9 Extraindo metricas dos resultados...")
    run_step([sys.executable, "gerar_tabelas_relatorio.py"], "Gerar tabelas de resultados")
    run_step([sys.executable, "gerar_graficos_resultados.py"], "Gerar graficos", required=False)
    print("8/9 Atualizando relatorio...")
    run_step([sys.executable, "atualizar_relatorio.py"], "Atualizar relatorio", required=False)
    print("9/9 Finalizando...")
    print("Concluido.")


if __name__ == "__main__":
    main()
