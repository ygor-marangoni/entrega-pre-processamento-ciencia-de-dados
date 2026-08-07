"""Gera visualizações acadêmicas a partir do Top 20 de regras de associação."""

from __future__ import annotations

import argparse
import csv
import os
import re
import tempfile
from collections import Counter
from pathlib import Path

# Evita depender do diretório de configuração do perfil do usuário.
os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "trabalho_4_apriori_mpl")
)

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


CORES = {
    "ÓBVIA": "#7a7a7a",
    "INTERESSANTE": "#2f6f8f",
    "NOVIDADE": "#b06c19",
}
MARCADORES = {"ÓBVIA": "o", "INTERESSANTE": "s", "NOVIDADE": "D"}


def ler_csv(caminho: Path) -> list[dict[str, str]]:
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo, delimiter=";"))


def campo(linha: dict[str, str], prefixo: str) -> str:
    return next(nome for nome in linha if nome.startswith(prefixo))


def nome_item(item: str) -> str:
    """Converte o nome técnico em rótulo curto, preservando a categoria."""
    atributo, categoria = item.split("__", maxsplit=1)
    atributo = atributo.replace("FAIXA_", "").replace("CATEGORIA_", "")
    atributo = atributo.replace("SITUACAO_", "").replace("POSSE_", "")
    categoria = categoria.replace("REJEICAO_PREVIA_", "REJEIÇÃO ")
    return f"{atributo.replace('_', ' ').title()}: {categoria.replace('_', ' ').title()}"


def preparar_estilo() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "axes.edgecolor": "#555555",
            "axes.linewidth": 0.8,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def salvar(figura: plt.Figure, caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(caminho, dpi=300, bbox_inches="tight")
    plt.close(figura)


def grafico_lift(regras: list[dict[str, str]], saida: Path, posicao: str, classificacao: str) -> None:
    ordem = list(reversed(regras))
    rotulos = [f"R{linha[posicao]}" for linha in ordem]
    valores = [float(linha["Lift"]) for linha in ordem]
    cores = [CORES[linha[classificacao]] for linha in ordem]
    figura, eixo = plt.subplots(figsize=(10, 7.4))
    barras = eixo.barh(rotulos, valores, color=cores, edgecolor="#404040", linewidth=0.4)
    eixo.axvline(1, color="#303030", linewidth=1, linestyle="--", label="Lift = 1")
    eixo.set_title("Top 20 regras por Lift")
    eixo.set_xlabel("Lift")
    eixo.set_ylabel("Regra (posição na tabela)")
    eixo.set_xlim(0.90, max(valores) + 0.035)
    eixo.grid(axis="x", color="#d9d9d9", linewidth=0.7)
    eixo.set_axisbelow(True)
    for barra, valor in zip(barras, valores):
        eixo.text(valor + 0.003, barra.get_y() + barra.get_height() / 2, f"{valor:.2f}", va="center", fontsize=8)
    legenda = [
        Line2D([0], [0], marker="s", color="w", markerfacecolor=CORES[classe], markersize=8, label=classe)
        for classe in ("ÓBVIA", "INTERESSANTE", "NOVIDADE")
    ]
    legenda.append(Line2D([0], [0], color="#303030", linestyle="--", label="Lift = 1"))
    eixo.legend(handles=legenda, loc="lower right", frameon=False)
    figura.text(0.01, 0.01, "Fonte: elaboração própria a partir da saída do WEKA 3.8.7.", fontsize=8)
    salvar(figura, saida / "01_top20_lift.png")


def grafico_confianca_lift(regras: list[dict[str, str]], saida: Path, posicao: str, classificacao: str, confianca: str) -> None:
    figura, eixo = plt.subplots(figsize=(9.6, 6.5))
    for classe in ("ÓBVIA", "INTERESSANTE", "NOVIDADE"):
        grupo = [linha for linha in regras if linha[classificacao] == classe]
        eixo.scatter(
            [float(linha["Lift"]) for linha in grupo],
            [float(linha[confianca]) for linha in grupo],
            s=70,
            c=CORES[classe],
            marker=MARCADORES[classe],
            label=classe,
            edgecolors="#333333",
            linewidths=0.5,
            alpha=0.9,
        )
        for linha in grupo:
            eixo.annotate(
                f"R{linha[posicao]}",
                (float(linha["Lift"]), float(linha[confianca])),
                xytext=(4, 4),
                textcoords="offset points",
                fontsize=8,
            )
    eixo.axvline(1, color="#303030", linewidth=1, linestyle="--")
    eixo.set_title("Confiança e Lift das regras selecionadas")
    eixo.set_xlabel("Lift")
    eixo.set_ylabel("Confiança")
    eixo.grid(color="#d9d9d9", linewidth=0.7)
    eixo.set_axisbelow(True)
    eixo.legend(title="Classificação", frameon=False, loc="upper right")
    figura.text(0.01, 0.01, "Fonte: elaboração própria a partir da saída do WEKA 3.8.7.", fontsize=8)
    salvar(figura, saida / "02_confianca_lift_classificacao.png")


def grafico_classificacoes(regras: list[dict[str, str]], saida: Path, classificacao: str) -> None:
    classes = ["ÓBVIA", "INTERESSANTE", "NOVIDADE"]
    contagens = Counter(linha[classificacao] for linha in regras)
    valores = [contagens[classe] for classe in classes]
    figura, eixo = plt.subplots(figsize=(8, 5.2))
    barras = eixo.bar(classes, valores, color=[CORES[classe] for classe in classes], edgecolor="#404040", linewidth=0.5)
    eixo.set_title("Distribuição das regras do Top 20 por classificação")
    eixo.set_ylabel("Quantidade de regras")
    eixo.set_ylim(0, max(valores) + 2)
    eixo.grid(axis="y", color="#d9d9d9", linewidth=0.7)
    eixo.set_axisbelow(True)
    for barra, valor in zip(barras, valores):
        eixo.text(barra.get_x() + barra.get_width() / 2, valor + 0.25, str(valor), ha="center", va="bottom")
    figura.text(0.01, 0.01, "Fonte: elaboração própria a partir da classificação justificada do Top 20.", fontsize=8)
    salvar(figura, saida / "03_distribuicao_classificacao.png")


def grafico_frequencia_itens(regras: list[dict[str, str]], saida: Path, antecedente: str, consequente: str) -> None:
    contador: Counter[str] = Counter()
    for linha in regras:
        contador.update((linha[antecedente] + " + " + linha[consequente]).split(" + "))
    frequentes = contador.most_common(12)
    nomes = [nome_item(item) for item, _ in reversed(frequentes)]
    valores = [quantidade for _, quantidade in reversed(frequentes)]
    figura, eixo = plt.subplots(figsize=(11, 7.2))
    barras = eixo.barh(nomes, valores, color="#2f6f8f", edgecolor="#404040", linewidth=0.4)
    eixo.set_title("Itens mais frequentes nas regras do Top 20")
    eixo.set_xlabel("Número de ocorrências nas regras")
    eixo.set_ylabel("Item discretizado")
    eixo.grid(axis="x", color="#d9d9d9", linewidth=0.7)
    eixo.set_axisbelow(True)
    eixo.set_xlim(0, max(valores) + 1)
    for barra, valor in zip(barras, valores):
        eixo.text(valor + 0.08, barra.get_y() + barra.get_height() / 2, str(valor), va="center", fontsize=8)
    figura.text(0.01, 0.01, "Fonte: elaboração própria a partir das 20 regras selecionadas.", fontsize=8)
    salvar(figura, saida / "04_frequencia_itens_top20.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, required=True)
    parser.add_argument("--saida-diretorio", type=Path, required=True)
    args = parser.parse_args()

    regras = ler_csv(args.entrada)
    if len(regras) != 20:
        raise ValueError(f"São esperadas 20 regras; foram encontradas {len(regras)}.")
    posicao = campo(regras[0], "Pos")
    antecedente = campo(regras[0], "Anteced")
    consequente = campo(regras[0], "Conse")
    confianca = campo(regras[0], "Conf")
    classificacao = campo(regras[0], "Class")
    if sorted(int(linha[posicao]) for linha in regras) != list(range(1, 21)):
        raise ValueError("As posições do Top 20 devem cobrir 1 a 20.")

    preparar_estilo()
    grafico_lift(regras, args.saida_diretorio, posicao, classificacao)
    grafico_confianca_lift(regras, args.saida_diretorio, posicao, classificacao, confianca)
    grafico_classificacoes(regras, args.saida_diretorio, classificacao)
    grafico_frequencia_itens(regras, args.saida_diretorio, antecedente, consequente)
    print("GRAFICOS_GERADOS=4")


if __name__ == "__main__":
    main()
