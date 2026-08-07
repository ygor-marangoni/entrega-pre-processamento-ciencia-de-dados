"""Classifica o Top 20 em ÓBVIA, INTERESSANTE ou NOVIDADE com justificativas.

Critérios aplicados:
- ÓBVIA: regra inversa/reformulação de mesmo itemset, próxima da independência
  ou explicada principalmente pela predominância da categoria consequente.
- INTERESSANTE: associação entre dimensões distintas, não derivada por fórmula,
  mas com evidência ainda fraca ou suporte que recomenda cautela.
- NOVIDADE: padrão entre dimensões distintas, sem derivação estrutural direta,
  com Lift positivo e interpretação plausível. Nesta base, a novidade é tratada
  como preliminar porque o suporte é de 1% e o Lift é moderado.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ANALISES: dict[int, tuple[str, str]] = {
    1: (
        "INTERESSANTE",
        "Combina estágio de vida e histórico de crédito com rejeição prévia; o Lift 1,11 indica associação positiva discreta, mas o suporte de 1% pede cautela.",
    ),
    2: (
        "ÓBVIA",
        "É a direção inversa do mesmo itemset da regra 1 e tem confiança de 7%; não acrescenta evidência independente ao padrão.",
    ),
    3: (
        "NOVIDADE",
        "Crédito muito alto e situação familiar separada/viúva/não informada se associam a um a dois créditos ativos (Lift 1,10; confiança 48%). São dimensões diferentes e não há relação construída por fórmula, embora seja uma novidade preliminar pelo suporte de 1%.",
    ),
    4: (
        "INTERESSANTE",
        "Renda alta e situação solteira associam-se a crédito médio, unindo renda, perfil familiar e crédito. O Lift 1,10 é positivo, porém modesto e observado em 1% das transações.",
    ),
    5: (
        "ÓBVIA",
        "Reorganiza os mesmos três itens da regra 1; a inversão de antecedente e consequente não constitui uma descoberta adicional.",
    ),
    6: (
        "ÓBVIA",
        "Outra direção do itemset da regra 1, com confiança de 7%; descreve o mesmo coocorrimento sem novo poder descritivo.",
    ),
    7: (
        "ÓBVIA",
        "É a direção inversa do itemset da regra 4 e possui confiança de 4%, insuficiente para tratá-la como descoberta separada.",
    ),
    8: (
        "ÓBVIA",
        "É a direção inversa da regra 3 e tem confiança de 2%; não amplia a interpretação da novidade preliminar já registrada.",
    ),
    9: (
        "INTERESSANTE",
        "Idade de 30 a 39 anos com rejeição prévia moderada associa-se a renda muito alta. A associação entre trajetória de crédito e renda é plausível, mas o Lift 1,07 e o suporte de 1% são fracos.",
    ),
    10: (
        "ÓBVIA",
        "Inverte a regra 9 e apresenta confiança de 4%; é uma reformulação de itemset, não uma evidência nova.",
    ),
    11: (
        "ÓBVIA",
        "É uma das direções do mesmo itemset renda alta, crédito médio e situação solteira já representado pela regra 4; não deve ser contado como nova descoberta.",
    ),
    12: (
        "ÓBVIA",
        "Inverte a regra 11, com confiança de 7%, e apenas reexpressa a mesma coocorrência.",
    ),
    13: (
        "ÓBVIA",
        "Lift de 0,99 é praticamente independência; posse de carro e situação solteira não oferecem evidência útil de associação com crédito médio.",
    ),
    14: (
        "ÓBVIA",
        "É a inversão da regra 13, também próxima da independência e com confiança de 4%.",
    ),
    15: (
        "ÓBVIA",
        "A confiança de 71% acompanha a alta frequência de casado/união civil na amostra; o Lift 0,98 não sustenta associação positiva específica.",
    ),
    16: (
        "ÓBVIA",
        "É a direção inversa da regra 15, com confiança de 1%, e não supera a explicação pela frequência predominante de casado/união civil.",
    ),
    17: (
        "ÓBVIA",
        "Reorganiza os mesmos itens das regras 4 e 11; Lift 0,97 não indica associação positiva relevante.",
    ),
    18: (
        "ÓBVIA",
        "Inverte a regra 17, com confiança de 4% e Lift 0,97; não há descoberta adicional.",
    ),
    19: (
        "ÓBVIA",
        "Lift 0,95 indica associação negativa leve, praticamente independente, entre renda muito alta, idade de 30 a 39 anos e rejeição prévia moderada.",
    ),
    20: (
        "ÓBVIA",
        "É a direção inversa da regra 19 e mantém Lift 0,95 e confiança de 7%; não configura padrão novo.",
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, required=True)
    parser.add_argument("--saida", type=Path, required=True)
    args = parser.parse_args()

    with args.entrada.open(encoding="utf-8", newline="") as arquivo:
        regras = list(csv.DictReader(arquivo, delimiter=";"))
    if len(regras) != 20:
        raise ValueError(f"O Top 20 deve conter 20 linhas; foram recebidas {len(regras)}.")

    linhas: list[dict[str, str]] = []
    for regra in regras:
        posicao = int(regra["Posição"])
        if posicao not in ANALISES:
            raise ValueError(f"Posição sem classificação definida: {posicao}")
        classificacao, justificativa = ANALISES[posicao]
        linhas.append({**regra, "Classificação": classificacao, "Justificativa": justificativa})

    campos = list(regras[0].keys()) + ["Classificação", "Justificativa"]
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with args.saida.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos, delimiter=";")
        escritor.writeheader()
        escritor.writerows(linhas)

    for classe in ("ÓBVIA", "INTERESSANTE", "NOVIDADE"):
        print(f"{classe}={sum(linha['Classificação'] == classe for linha in linhas)}")


if __name__ == "__main__":
    main()
