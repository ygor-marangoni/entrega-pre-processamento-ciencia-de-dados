"""Consulta a versão e a ajuda reais do Apriori instalado, sem minerar dados."""

from __future__ import annotations

import subprocess
from pathlib import Path


WEKA_JAR = Path(r"C:\Program Files\Weka-3-8-7\weka.jar")


def run(command: list[str]) -> None:
    result = subprocess.run(command, check=False, text=True, capture_output=True)
    print("$ " + " ".join(command))
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"Comando retornou código {result.returncode}.")


def main() -> None:
    if not WEKA_JAR.is_file():
        raise FileNotFoundError(f"weka.jar não encontrado: {WEKA_JAR}")
    run(["java", "-cp", str(WEKA_JAR), "weka.core.Version"])
    run(["java", "-cp", str(WEKA_JAR), "weka.associations.Apriori", "-h"])
    print("Auditoria concluída. Nenhuma base foi fornecida ao Apriori.")


if __name__ == "__main__":
    main()
