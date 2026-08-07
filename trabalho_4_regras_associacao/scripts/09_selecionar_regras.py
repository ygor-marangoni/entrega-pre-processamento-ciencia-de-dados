"""Seleciona as 20 melhores regras fechadas de três itens por Lift."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


def numero(valor: str) -> float:
    convertido = float(valor.replace(",", "."))
    if not math.isfinite(convertido):
        raise ValueError(f"Métrica não finita: {valor}")
    return convertido


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, required=True)
    parser.add_argument("--saida", type=Path, required=True)
    args = parser.parse_args()

    with args.entrada.open(encoding="utf-8", newline="") as arquivo:
        regras = list(csv.DictReader(arquivo, delimiter=";"))

    candidatas: list[dict[str, str]] = []
    for regra in regras:
        if int(regra["total_itens"]) != 3:
            continue
        # A conversão também impede o uso de métricas ausentes, infinitas ou não numéricas.
        for campo in ("suporte", "confianca", "lift", "leverage", "conviction"):
            numero(regra[campo])
        candidatas.append(regra)

    ordenadas = sorted(
        candidatas,
        key=lambda regra: (
            -numero(regra["lift"]),
            -numero(regra["suporte"]),
            -numero(regra["confianca"]),
            int(regra["id_regra"]),
        ),
    )
    selecionadas = ordenadas[:20]
    if len(selecionadas) != 20:
        raise ValueError(
            f"São necessárias 20 regras elegíveis; foram encontradas {len(selecionadas)}."
        )

    campos = [
        "Posição", "Antecedente", "Consequente", "Suporte", "Confiança", "Lift",
        "Leverage", "Conviction",
    ]
    linhas = [
        {
            "Posição": posicao,
            "Antecedente": regra["antecedente"],
            "Consequente": regra["consequente"],
            "Suporte": regra["suporte"],
            "Confiança": regra["confianca"],
            "Lift": regra["lift"],
            "Leverage": regra["leverage"],
            "Conviction": regra["conviction"],
        }
        for posicao, regra in enumerate(selecionadas, start=1)
    ]
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with args.saida.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos, delimiter=";")
        escritor.writeheader()
        escritor.writerows(linhas)

    print(f"REGRAS_ELEGIVEIS={len(candidatas)}")
    print(f"REGRAS_SELECIONADAS={len(selecionadas)}")
    print(f"LIFT_MAIOR={linhas[0]['Lift']}")
    print(f"LIFT_MENOR_TOP20={linhas[-1]['Lift']}")


if __name__ == "__main__":
    main()
